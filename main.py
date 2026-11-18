import os
import json
import socket
import logging
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.models import ProcessAudioResponse, CalibrationResponse, ServerStatusResponse
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

# Prevent aggressive browser caching of static files (especially on mobile browsers)
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

@app.post("/api/calibrate-voice", response_model=CalibrationResponse)
async def calibrate_voice(
    speaker_id: str = Form(..., description="'speaker_1' or 'speaker_2'"),
    speaker_name: str = Form(..., description="Custom name/label of the speaker"),
    audio: UploadFile = File(..., description="15s baseline audio recording")
):
    """Saves baseline acoustic calibration audio for either brother."""
    if speaker_id not in ["speaker_1", "speaker_2"]:
        raise HTTPException(status_code=400, detail="speaker_id must be 'speaker_1' or 'speaker_2'.")
    
    filename = f"{speaker_id}_calibration.webm"
    save_path = settings.CALIBRATION_DIR / filename
    
    content = await audio.read()
    with open(save_path, "wb") as f:
        f.write(content)
        
    logger.info(f"Calibration voice profile saved for {speaker_name} ({speaker_id}) at {save_path}")
    return CalibrationResponse(
        success=True,
        speaker_id=speaker_id,
        speaker_name=speaker_name,
        audio_path=str(save_path.name),
        message=f"Voice profile for {speaker_name} saved successfully!"
    )

@app.post("/api/process-audio", response_model=ProcessAudioResponse)
async def process_scene_audio(
    audio: UploadFile = File(..., description="Enactment scene audio recording"),
    arc_title: str = Form("Untitled Arc Scene"),
    speaker_1_name: str = Form("Author 1"),
    speaker_1_char: str = Form("Character A"),
    speaker_1_notes: str = Form(""),
    speaker_2_name: str = Form("Author 2"),
    speaker_2_char: str = Form("Character B"),
    speaker_2_notes: str = Form(""),
    scene_context: str = Form("")
):
    """Processes live enactment audio: diarizes speakers, tags emotions, and generates novel prose."""
    # 1. Rate Limit Guard
    rate_limiter.acquire()
    
    # 2. Save raw audio take locally in recordings/
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_arc = "".join(c for c in arc_title if c.isalnum() or c in ("-", "_")).rstrip()
    audio_filename = f"take_{timestamp_str}_{clean_arc}.webm"
    audio_path = settings.RECORDINGS_DIR / audio_filename
    
    audio_bytes = await audio.read()
    with open(audio_path, "wb") as f:
        f.write(audio_bytes)
        
    mime_type = audio.content_type or "audio/webm"
    logger.info(f"Received scene audio '{audio_filename}' ({len(audio_bytes)} bytes, MIME: {mime_type})")
    
    # 3. Process via Gemini Audio Service
    try:
        result = await gemini_service.process_enactment_audio(
            scene_audio_bytes=audio_bytes,
            mime_type=mime_type,
            arc_title=arc_title,
            speaker_1_name=speaker_1_name,
            speaker_1_char=speaker_1_char,
            speaker_1_notes=speaker_1_notes,
            speaker_2_name=speaker_2_name,
            speaker_2_char=speaker_2_char,
            speaker_2_notes=speaker_2_notes,
            scene_context=scene_context
        )
    except Exception as e:
        logger.error(f"Gemini processing error: {e}")
        raise HTTPException(status_code=500, detail=f"AI processing failed: {str(e)}")

    # 4. Save structured result into exports/
    export_filename = f"scene_{timestamp_str}_{clean_arc}.json"
    export_path = settings.EXPORTS_DIR / export_filename
    
    payload = {
        "success": True,
        "arc_title": result.get("arc_title", arc_title),
        "summary": result.get("summary", ""),
        "dialogues": result.get("dialogues", []),
        "scene_beats": result.get("scene_beats", []),
        "novel_prose_draft": result.get("novel_prose_draft", ""),
        "raw_audio_filename": audio_filename,
        "processed_at": datetime.now().isoformat(),
    }
    
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        
    return payload

@app.get("/api/history")
async def get_history():
    """Lists past exported scenes."""
    history = []
    for file in sorted(settings.EXPORTS_DIR.glob("scene_*.json"), reverse=True):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                history.append({
                    "filename": file.name,
                    "arc_title": data.get("arc_title", "Untitled"),
                    "summary": data.get("summary", "")[:120] + "...",
                    "processed_at": data.get("processed_at", ""),
                    "dialogues_count": len(data.get("dialogues", []))
                })
        except Exception:
            continue
    return history

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
