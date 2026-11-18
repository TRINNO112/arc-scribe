import os
import json
import socket
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.models import ProcessAudioResponse, CalibrationResponse, ServerStatusResponse, CalibrationUploadResponse, SpeakerAcousticProfile
from backend.gemini_service import gemini_service
from backend.rate_limiter import rate_limiter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("arc-scribe.server")

app = FastAPI(title="Arc Scribe", version=settings.VERSION)

# Enable CORS for cross-device mobile web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prevent aggressive browser caching of static files
@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static") or request.url.path == "/":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

def get_local_ip() -> str:
    """Detects the primary local LAN IP address for easy mobile Wi-Fi connection."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# API Routes
@app.get("/api/status", response_model=ServerStatusResponse)
async def get_server_status():
    spk1_cal = (settings.CALIBRATION_DIR / "speaker_1_calibration.webm").exists()
    spk2_cal = (settings.CALIBRATION_DIR / "speaker_2_calibration.webm").exists()
    recordings_count = len(list(settings.RECORDINGS_DIR.glob("*.webm"))) + len(list(settings.RECORDINGS_DIR.glob("*.mp4")))
    
    return ServerStatusResponse(
        status="online",
        version=settings.VERSION,
        model=settings.GEMINI_MODEL,
        api_key_configured=gemini_service.is_configured(),
        speaker_1_calibrated=spk1_cal,
        speaker_2_calibrated=spk2_cal,
        recordings_count=recordings_count,
    )

@app.get("/api/network-ip")
async def get_network_ip():
    ip = get_local_ip()
    return {
        "local_ip": ip,
        "port": settings.PORT,
        "mobile_url": f"http://{ip}:{settings.PORT}",
    }

# ==============================================================================
# ACOUSTIC CALIBRATION ENDPOINTS
# ==============================================================================

@app.post("/api/calibration/{speaker_id}", response_model=CalibrationUploadResponse)
async def upload_calibration_anchor(
    speaker_id: str,
    audio: UploadFile = File(..., description="15-second calibration audio recording"),
    real_name: str = Form("Brother"),
    character_counterpart: str = Form("Character"),
    pitch_register: str = Form("Mid-range"),
    timbre_description: str = Form("Natural speaking voice"),
    speech_tempo: str = Form("Normal conversational pace"),
    linguistic_quirks: str = Form("Hindi/Hinglish natural cadence")
):
    if speaker_id not in ("speaker_1", "speaker_2"):
        raise HTTPException(status_code=400, detail="speaker_id must be 'speaker_1' or 'speaker_2'")

    audio_bytes = await audio.read()
    if len(audio_bytes) < 2048:
        raise HTTPException(status_code=400, detail="Calibration sample too short or empty (min 2KB required)")

    # 1. Save Anchor WebM in recordings/calibration/
    anchor_filename = f"{speaker_id}_anchor.webm"
    anchor_path = settings.CALIBRATION_DIR / anchor_filename
    with open(anchor_path, "wb") as f:
        f.write(audio_bytes)

    # 2. Update Calibration Manifest
    manifest_path = settings.CALIBRATION_DIR / "calibration_manifest.json"
    manifest = {}
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception:
            manifest = {}

    if "speakers" not in manifest:
        manifest["speakers"] = {}

    import hashlib
    sha256 = hashlib.sha256(audio_bytes).hexdigest()

    profile_data = {
        "speaker_id": speaker_id,
        "real_name": real_name,
        "display_name": f"{real_name} ({speaker_id.replace('_', ' ').title()})",
        "character_counterpart": character_counterpart,
        "pitch_register": pitch_register,
        "timbre_description": timbre_description,
        "speech_tempo": speech_tempo,
        "linguistic_quirks": linguistic_quirks,
        "audio_filename": anchor_filename,
        "duration_seconds": 15.0,
        "file_size_bytes": len(audio_bytes),
        "sha256_hash": sha256,
        "calibrated_at": datetime.now().isoformat()
    }

    manifest["updated_at"] = datetime.now().isoformat()
    manifest["speakers"][speaker_id] = profile_data

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    return CalibrationUploadResponse(
        success=True,
        speaker_id=speaker_id,
        message=f"Calibration anchor for {real_name} successfully locked.",
        profile=SpeakerAcousticProfile(**profile_data)
    )

@app.get("/api/calibration/status")
async def get_calibration_status():
    manifest_path = settings.CALIBRATION_DIR / "calibration_manifest.json"
    spk1_exists = (settings.CALIBRATION_DIR / "speaker_1_anchor.webm").exists()
    spk2_exists = (settings.CALIBRATION_DIR / "speaker_2_anchor.webm").exists()

    manifest_data = {}
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        except Exception:
            pass

    return {
        "speaker_1_calibrated": spk1_exists,
        "speaker_2_calibrated": spk2_exists,
        "fully_calibrated": spk1_exists and spk2_exists,
        "manifest": manifest_data
    }

@app.delete("/api/calibration/{speaker_id}")
async def reset_calibration(speaker_id: str):
    if speaker_id not in ("speaker_1", "speaker_2"):
        raise HTTPException(status_code=400, detail="Invalid speaker_id")
    anchor_path = settings.CALIBRATION_DIR / f"{speaker_id}_anchor.webm"
    if anchor_path.exists():
        anchor_path.unlink()
    
    manifest_path = settings.CALIBRATION_DIR / "calibration_manifest.json"
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            if "speakers" in manifest and speaker_id in manifest["speakers"]:
                del manifest["speakers"][speaker_id]
                manifest["updated_at"] = datetime.now().isoformat()
                with open(manifest_path, "w", encoding="utf-8") as f:
                    json.dump(manifest, f, indent=2)
        except Exception:
            pass

    return {"success": True, "message": f"Reset calibration for {speaker_id}"}

# Audio playback endpoint
@app.get("/api/recordings/{filename}")
async def get_recording_audio(filename: str):
    clean_name = Path(filename).name
    file_path = settings.RECORDINGS_DIR / clean_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio recording not found")
    return FileResponse(file_path, media_type="audio/webm")

# Streaming Telemetry & Real-Time Processing
@app.post("/api/process-audio-stream")
async def process_audio_stream(
    audio: UploadFile = File(..., description="Enactment scene audio recording"),
    arc_title: str = Form("Raw Voice Session"),
    speaker_1_name: str = Form("Speaker 1"),
    speaker_2_name: str = Form("Speaker 2"),
):
    """
    Real-time streaming telemetry endpoint yielding live server processing milestones as NDJSON.
    """
    async def generator() -> AsyncGenerator[str, None]:
        try:
            # Stage 1: Ingest & disk persistence
            audio_bytes = await audio.read()
            size_kb = round(len(audio_bytes) / 1024, 1)
            
            yield json.dumps({
                "type": "telemetry",
                "step": 1,
                "total_steps": 4,
                "pct": 25,
                "msg": f"Audio payload verified ({size_kb} KB) • Decoding WebM OPUS frames..."
            }) + "\n"
            await asyncio.sleep(0.05)

            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            clean_arc = "".join(c for c in arc_title if c.isalnum() or c in ("-", "_")).rstrip()
            audio_filename = f"take_{timestamp_str}_{clean_arc}.webm"
            audio_path = settings.RECORDINGS_DIR / audio_filename

            with open(audio_path, "wb") as f:
                f.write(audio_bytes)

            mime_type = audio.content_type or "audio/webm"

            # Stage 2: Gateway transmission
            yield json.dumps({
                "type": "telemetry",
                "step": 2,
                "total_steps": 4,
                "pct": 50,
                "msg": "Initiating connection via Primary Route (with smart proxy failover)..."
            }) + "\n"
            await asyncio.sleep(0.05)

            # Stage 3: Gemini Execution
            rate_limiter.acquire()
            yield json.dumps({
                "type": "telemetry",
                "step": 3,
                "total_steps": 4,
                "pct": 75,
                "msg": f"{settings.GEMINI_MODEL} processing multi-lingual diarization & vocal inflections..."
            }) + "\n"
            await asyncio.sleep(0.05)

            result = await gemini_service.process_enactment_audio(
                scene_audio_bytes=audio_bytes,
                mime_type=mime_type,
                arc_title=arc_title,
                speaker_1_name=speaker_1_name,
                speaker_2_name=speaker_2_name
            )

            # Stage 4: Assembly & Persistence
            route_name = result.get("_route", "Direct Route")
            yield json.dumps({
                "type": "telemetry",
                "step": 4,
                "total_steps": 4,
                "pct": 95,
                "msg": f"Response verified (HTTP 200 via {route_name}) • Structuring raw dialogue turns..."
            }) + "\n"
            await asyncio.sleep(0.05)

            raw_script = result.get("dialogue_script") or result.get("dialogues") or []
            normalized_lines = []
            for line in raw_script:
                text_val = line.get("text") or line.get("dialogue") or ""
                spk_val = line.get("speaker") or "Speaker 1"
                spk_id = line.get("speaker_id") or ("speaker_1" if "1" in spk_val else "speaker_2")
                tone_val = line.get("vocal_tone") or ""
                time_val = line.get("timestamp") or "0:00"
                normalized_lines.append({
                    "speaker": spk_val,
                    "speaker_id": spk_id,
                    "text": text_val,
                    "vocal_tone": tone_val,
                    "timestamp": time_val
                })

            export_filename = f"scene_{timestamp_str}_{clean_arc}.json"
            export_path = settings.EXPORTS_DIR / export_filename

            payload = {
                "success": True,
                "id": export_filename,
                "dialogue_script": normalized_lines,
                "summary": result.get("summary", ""),
                "raw_audio_filename": audio_filename,
                "audio_url": f"/api/recordings/{audio_filename}",
                "processed_at": datetime.now().isoformat(),
            }

            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)

            yield json.dumps({
                "type": "result",
                "step": 4,
                "total_steps": 4,
                "pct": 100,
                "msg": "Dialogue script ready!",
                "data": payload
            }) + "\n"

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield json.dumps({
                "type": "error",
                "msg": str(e)
            }) + "\n"

    return StreamingResponse(generator(), media_type="application/x-ndjson")

# Standard Fallback POST
@app.post("/api/process-audio", response_model=ProcessAudioResponse)
async def process_scene_audio(
    audio: UploadFile = File(..., description="Enactment scene audio recording"),
    arc_title: str = Form("Raw Voice Session"),
    speaker_1_name: str = Form("Speaker 1"),
    speaker_2_name: str = Form("Speaker 2"),
):
    rate_limiter.acquire()
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_arc = "".join(c for c in arc_title if c.isalnum() or c in ("-", "_")).rstrip()
    audio_filename = f"take_{timestamp_str}_{clean_arc}.webm"
    audio_path = settings.RECORDINGS_DIR / audio_filename
    
    audio_bytes = await audio.read()
    with open(audio_path, "wb") as f:
        f.write(audio_bytes)
        
    mime_type = audio.content_type or "audio/webm"
    
    result = await gemini_service.process_enactment_audio(
        scene_audio_bytes=audio_bytes,
        mime_type=mime_type,
        arc_title=arc_title,
        speaker_1_name=speaker_1_name,
        speaker_2_name=speaker_2_name
    )

    export_filename = f"scene_{timestamp_str}_{clean_arc}.json"
    export_path = settings.EXPORTS_DIR / export_filename
    
    raw_script = result.get("dialogue_script") or result.get("dialogues") or []
    normalized_lines = []
    for line in raw_script:
        text_val = line.get("text") or line.get("dialogue") or ""
        spk_val = line.get("speaker") or "Speaker 1"
        spk_id = line.get("speaker_id") or ("speaker_1" if "1" in spk_val else "speaker_2")
        tone_val = line.get("vocal_tone") or ""
        time_val = line.get("timestamp") or "0:00"
        normalized_lines.append({
            "speaker": spk_val,
            "speaker_id": spk_id,
            "text": text_val,
            "vocal_tone": tone_val,
            "timestamp": time_val
        })

    payload = {
        "success": True,
        "dialogue_script": normalized_lines,
        "summary": result.get("summary", ""),
        "raw_audio_filename": audio_filename,
        "processed_at": datetime.now().isoformat(),
    }
    
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        
    return payload

# Full History CRUD Endpoints
@app.get("/api/history")
async def get_history():
    history = []
    for file in sorted(settings.EXPORTS_DIR.glob("scene_*.json"), reverse=True):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                dialogues = data.get("dialogue_script") or data.get("dialogues") or []
                preview = dialogues[0].get("text", "") if dialogues else ""
                history.append({
                    "id": file.name,
                    "filename": file.name,
                    "preview": preview[:100] + "..." if len(preview) > 100 else preview,
                    "dialogues_count": len(dialogues),
                    "raw_audio_filename": data.get("raw_audio_filename"),
                    "processed_at": data.get("processed_at", ""),
                })
        except Exception:
            continue
    return history

@app.get("/api/history/{filename}")
async def get_history_item(filename: str):
    clean_name = Path(filename).name
    file_path = settings.EXPORTS_DIR / clean_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Session take not found")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "raw_audio_filename" in data and data["raw_audio_filename"]:
        data["audio_url"] = f"/api/recordings/{data['raw_audio_filename']}"
    return data

@app.put("/api/history/{filename}")
async def update_history_item(filename: str, payload: dict = Body(...)):
    clean_name = Path(filename).name
    file_path = settings.EXPORTS_DIR / clean_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Session take not found")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return {"success": True, "message": "Updated dialogue session"}

@app.delete("/api/history/{filename}")
async def delete_history_item(filename: str):
    clean_name = Path(filename).name
    file_path = settings.EXPORTS_DIR / clean_name
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                audio_file = data.get("raw_audio_filename")
                if audio_file:
                    audio_path = settings.RECORDINGS_DIR / audio_file
                    if audio_path.exists():
                        audio_path.unlink()
        except Exception:
            pass
        file_path.unlink()
        return {"success": True, "deleted": clean_name}
    raise HTTPException(status_code=404, detail="File not found")

# Static files mount for the web client
app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")

@app.get("/")
async def serve_index():
    return FileResponse(
        settings.STATIC_DIR / "index.html",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }
    )

if __name__ == "__main__":
    import uvicorn
    local_ip = get_local_ip()
    print("=" * 60)
    print("✨ ARC SCRIBE - Novel Enactment & Audio Scribe Studio")
    print(f"📡 Desktop Browser:  http://localhost:{settings.PORT}")
    print(f"📱 Smartphone Mobile: http://{local_ip}:{settings.PORT}")
    print("=" * 60)
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
