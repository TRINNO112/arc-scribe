import os
import time
import json
import base64
import socket
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import requests

from backend.config import settings
from backend.validator import DialogueSanitizerService

logger = logging.getLogger("arc-scribe.gemini")

class GeminiAudioService:
    def __init__(self):
        self.calibration_manifest_path = settings.CALIBRATION_DIR / "calibration_manifest.json"
        self.rules_path = settings.BASE_DIR / "backend" / "arc-rules.json"

    def is_configured(self) -> bool:
        return bool(settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY.strip()) > 10)

    def load_calibration_manifest(self) -> Dict[str, Any]:
        """Loads cached calibration metadata from disk if present."""
        if self.calibration_manifest_path.exists():
            try:
                with open(self.calibration_manifest_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not parse calibration_manifest.json: {e}")
        return {"speakers": {}}

    def read_anchor_audio(self, speaker_key: str) -> Optional[Tuple[bytes, str]]:
        """Reads anchor WebM bytes from recordings/calibration/ if available."""
        anchor_path = settings.CALIBRATION_DIR / f"{speaker_key}_anchor.webm"
        if anchor_path.exists():
            try:
                data = anchor_path.read_bytes()
                if len(data) > 1024:
                    return data, "audio/webm"
            except Exception as e:
                logger.warning(f"Failed to read anchor for {speaker_key}: {e}")
        return None

    def get_backup_proxies(self) -> Optional[Dict[str, str]]:
        """
        Backup Connection Probe:
        1. Checks configured gateway proxy URL (from .env).
        2. Rapid 0.5s socket probe to verify if the backup proxy server is reachable.
        3. Returns proxy dictionary if reachable, None otherwise.
        """
        proxy_url = settings.GATEWAY_PROXY_URL.strip() or os.environ.get("HTTPS_PROXY", "").strip() or os.environ.get("HTTP_PROXY", "").strip()
        if not proxy_url:
            return None

        try:
            target = proxy_url.split("://")[-1]
            host = target.split(":")[0]
            port = int(target.split(":")[1].split("/")[0])

            probe_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            probe_socket.settimeout(0.5)
            probe_socket.connect((host, port))
            probe_socket.close()

            return {
                "http": proxy_url,
                "https": proxy_url,
            }
        except Exception as e:
            logger.warning(f"Backup gateway proxy ({proxy_url}) unreachable: {e}")
            return None

    def build_multimodal_payload(
        self,
        scene_audio_bytes: bytes,
        scene_mime_type: str,
        arc_title: str,
        speaker_1_name: str,
        speaker_2_name: str
    ) -> Dict[str, Any]:
        """
        Assembles the multi-part Gemini payload incorporating:
        1. Reasoning budget governance (< 1,000 tokens, zero discursive speculation).
        2. Persistent baseline acoustic reference anchors for both brothers.
        3. Verbatim Hinglish Latin-script rules & closed 15-tone taxonomy.
        """
        manifest = self.load_calibration_manifest()
        spk1_meta = manifest.get("speakers", {}).get("speaker_1", {})
        spk2_meta = manifest.get("speakers", {}).get("speaker_2", {})

        spk1_anchor = self.read_anchor_audio("speaker_1")
        spk2_anchor = self.read_anchor_audio("speaker_2")

        parts = []

        # 1. DOMAIN INSTRUCTION & REASONING BUDGET GOVERNANCE
        system_instruction_text = (
            "You are Arc Scribe's Master Acoustic Diarization & Dialogue Governor. "
            "You are processing a live audio recording of two biological brothers roleplaying character dialogue in Hindi, English, and Hinglish. "
            "--- REASONING BUDGET GOVERNANCE & ACOUSTIC THINKING GUARDRAIL (CRITICAL) --- "
            "1. ZERO DISCURSIVE LITERARY SPECULATION: Do NOT write character motivation, dramaturgical critiques, or plot forecasts in your thinking trace. "
            "2. DIRECT BINARY ACOUSTIC ANCHOR MATCHING: Compare acoustic waveforms directly against Reference Anchor 1 and Reference Anchor 2 in a single step. "
            "3. DIRECT SCENE TIMESTAMP GROUNDING: Extract accurate audible start offsets. Timestamps must strictly advance monotonically (T[i] >= T[i-1]). "
            "4. ZERO SPECULATIVE PHONETIC RECONSTRUCTION: If audio is muffled or masked by room reverb, emit '[INAUDIBLE]'—never invent dialogue. "
            "5. CONCISE THOUGHT TRACE CEILING: Keep internal reasoning crisp, forensic, and under 1,000 tokens."
        )

        # 2. ACOUSTIC ANCHOR INJECTION (GROUND TRUTH)
        if spk1_anchor and spk2_anchor:
            s1_bytes, s1_mime = spk1_anchor
            s1_b64 = base64.b64encode(s1_bytes).decode("utf-8")
            s1_name = spk1_meta.get("display_name", speaker_1_name)
            s1_char = spk1_meta.get("character_counterpart", speaker_1_name)
            s1_timbre = spk1_meta.get("timbre_description", "Low baritone, deliberate chest resonance")
            s1_tempo = spk1_meta.get("speech_tempo", "Measured, steady pauses")

            parts.append({
                "text": (
                    f"=== ACOUSTIC REFERENCE 1: Speaker 1 (Ground Truth Anchor) ===\n"
                    f"Speaker ID: speaker_1\n"
                    f"Name: {s1_name} | Role: {s1_char}\n"
                    f"Acoustic Traits: {s1_timbre} | Tempo: {s1_tempo}\n"
                    f"Listen to Reference 1 audio below as the verified acoustic baseline for Speaker 1:"
                )
            })
            parts.append({"inlineData": {"mimeType": s1_mime, "data": s1_b64}})

            s2_bytes, s2_mime = spk2_anchor
            s2_b64 = base64.b64encode(s2_bytes).decode("utf-8")
            s2_name = spk2_meta.get("display_name", speaker_2_name)
            s2_char = spk2_meta.get("character_counterpart", speaker_2_name)
            s2_timbre = spk2_meta.get("timbre_description", "Tenor, bright throat resonance, breathy attacks")
            s2_tempo = spk2_meta.get("speech_tempo", "Rapid, agile, reactive tempo")

            parts.append({
                "text": (
                    f"=== ACOUSTIC REFERENCE 2: Speaker 2 (Ground Truth Anchor) ===\n"
                    f"Speaker ID: speaker_2\n"
                    f"Name: {s2_name} | Role: {s2_char}\n"
                    f"Acoustic Traits: {s2_timbre} | Tempo: {s2_tempo}\n"
                    f"Listen to Reference 2 audio below as the verified acoustic baseline for Speaker 2:"
                )
            })
            parts.append({"inlineData": {"mimeType": s2_mime, "data": s2_b64}})

        elif spk1_anchor and not spk2_anchor:
            s1_bytes, s1_mime = spk1_anchor
            s1_b64 = base64.b64encode(s1_bytes).decode("utf-8")
            parts.append({
                "text": (
                    f"=== ACOUSTIC REFERENCE 1: Speaker 1 (Ground Truth Anchor) ===\n"
                    f"Speaker ID: speaker_1\n"
                    f"Verified vocal baseline for Speaker 1 provided below. "
                    f"RULE: Any vocal turns that match this anchor belong to Speaker 1. "
                    f"Any contrasting male voice diverging in pitch, timbre, or cadence must be attributed to Speaker 2 ({speaker_2_name})."
                )
            })
            parts.append({"inlineData": {"mimeType": s1_mime, "data": s1_b64}})

        elif spk2_anchor and not spk1_anchor:
            s2_bytes, s2_mime = spk2_anchor
            s2_b64 = base64.b64encode(s2_bytes).decode("utf-8")
            parts.append({
                "text": (
                    f"=== ACOUSTIC REFERENCE 2: Speaker 2 (Ground Truth Anchor) ===\n"
                    f"Speaker ID: speaker_2\n"
                    f"Verified vocal baseline for Speaker 2 provided below. "
                    f"RULE: Any vocal turns that match this anchor belong to Speaker 2. "
                    f"Any contrasting voice diverging in pitch, timbre, or cadence must be attributed to Speaker 1 ({speaker_1_name})."
                )
            })
            parts.append({"inlineData": {"mimeType": s2_mime, "data": s2_b64}})

        else:
            parts.append({
                "text": (
                    f"=== ACOUSTIC NOTE: UNCALIBRATED SESSION ===\n"
                    f"No pre-recorded anchors supplied. Identify Speaker 1 ({speaker_1_name}) vs Speaker 2 ({speaker_2_name}) "
                    f"via comparative contrast of baseline pitch, vocal timbre, and conversational turn-taking."
                )
            })

        # 3. TARGET ENACTMENT AUDIO & DIRECTIVES
        clean_target_mime = scene_mime_type.split(";")[0].strip() or "audio/webm"
        target_b64 = base64.b64encode(scene_audio_bytes).decode("utf-8")

        target_instructions = f"""
=== TARGET ENACTMENT AUDIO: {arc_title} ===
Languages: Hindi, English, and Hinglish.

CRITICAL INSTRUCTIONS:
1. DIARIZE SPEAKERS: Cross-reference every utterance against the supplied acoustic anchors.
2. VERBATIM MULTILINGUAL TRANSCRIPTION:
   - For English dialogue: Standard English spelling.
   - For Hindi/Hinglish: Clear Romanized Latin script phonetics (e.g. "Main keh raha hoon ki ruk jao", "Why are you doing this, bhai?").
   - NEVER output Devanagari script. NEVER translate Hindi words to English.
   - Preserve colloquial slang and contractions: 'yaar', 'arre', 'bhai', 'scene sorted hai', 'pakka', 'chal na', 'matlab'.
3. PARALINGUISTIC NOISE REJECTION:
   - Filter out physical room noises (mic thumps, table bumps, footsteps).
   - Non-verbal vocalizations: '[SIGHS]', '[SCOFFS]', '[LAUGHS]', or '[THROAT_CLEAR]'.
4. STRICT VOCAL TONE TAXONOMY:
   - 'vocal_tone' must be EXACTLY ONE token from this closed list:
     ["whispering", "mocking", "hesitant", "sarcastic", "laughing", "interrupting", "shouting", "deadpan", "furious", "strained", "breathy", "pleading", "calm", "resigned", "taunting"]
   - PROHIBITION: NEVER write narrative sentences or stage directions in 'vocal_tone'.
5. TIMESTAMP MONOTONICITY:
   - Timestamps must advance monotonically: Timestamp(Turn[i]) >= Timestamp(Turn[i-1]). Format: 'MM:SS'.

Respond ONLY with valid JSON matching this schema:
{{
  "dialogue_script": [
    {{
      "speaker": "{speaker_1_name}",
      "speaker_id": "speaker_1",
      "text": "Exact verbatim transcribed spoken line",
      "vocal_tone": "whispering",
      "timestamp": "0:04",
      "overlap_flag": false
    }}
  ],
  "summary": "Brief 1-2 sentence dramatic summary of the scene exchange"
}}
"""
        parts.append({"text": target_instructions})
        parts.append({"inlineData": {"mimeType": clean_target_mime, "data": target_b64}})

        payload = {
            "systemInstruction": {
                "parts": [{"text": system_instruction_text}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": parts
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.15
            }
        }
        return payload

    async def process_enactment_audio(
        self,
        scene_audio_bytes: bytes,
        mime_type: str,
        arc_title: str = "Raw Voice Session",
        speaker_1_name: str = "Speaker 1",
        speaker_1_char: str = "Speaker 1",
        speaker_1_notes: str = "",
        speaker_2_name: str = "Speaker 2",
        speaker_2_char: str = "Speaker 2",
        speaker_2_notes: str = "",
        scene_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sends raw voice audio to Gemini via HTTP/1.1 REST with multi-audio anchor grounding,
        reasoning governance, and post-processing Pydantic sanitization.
        """
        if not self.is_configured():
            raise ValueError("GEMINI_API_KEY is not configured! Please set it in arc-scribe/.env")

        api_key = settings.GEMINI_API_KEY.strip()
        model = settings.GEMINI_MODEL or "gemini-3.5-flash-lite"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        payload = self.build_multimodal_payload(
            scene_audio_bytes=scene_audio_bytes,
            scene_mime_type=mime_type,
            arc_title=arc_title,
            speaker_1_name=speaker_1_name,
            speaker_2_name=speaker_2_name
        )

        headers = {"Content-Type": "application/json"}
        route_used = "Direct Route"
        resp = None

        logger.info(f"Invoking {model} for governed dialogue analysis ({len(scene_audio_bytes)} bytes)...")

        # Send request with automatic retry for transient 503 / 429 surges
        max_retries = 3
        for attempt in range(max_retries):
            resp = None
            try:
                # 1. Primary Attempt: Direct TCP connection
                resp = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    proxies={"http": "", "https": ""},
                    timeout=35
                )
                route_used = "Direct Route"
            except requests.exceptions.RequestException as direct_err:
                logger.warning(f"Primary direct connection failed ({direct_err}). Testing backup proxy failover...")
                
                # 2. Automatic Backup Failover: Check if backup proxy server is reachable
                backup_proxies = self.get_backup_proxies()
                if backup_proxies:
                    try:
                        resp = requests.post(
                            url,
                            headers=headers,
                            json=payload,
                            proxies=backup_proxies,
                            timeout=45
                        )
                        route_used = "Backup Proxy Route"
                    except requests.exceptions.RequestException as proxy_err:
                        logger.error(f"Backup proxy request failed: {proxy_err}")
                else:
                    if attempt == max_retries - 1:
                        raise ValueError(f"Connection failed: {direct_err}. Backup proxy unreachable.")

            if resp is not None:
                if resp.status_code == 200:
                    break
                elif resp.status_code in (429, 503) and attempt < max_retries - 1:
                    sleep_time = 2.0 * (attempt + 1)
                    logger.warning(f"Gemini {resp.status_code} high demand surge. Retrying in {sleep_time}s (Attempt {attempt+1}/{max_retries})...")
                    time.sleep(sleep_time)
                    continue
                else:
                    logger.error(f"Gemini REST error ({resp.status_code}): {resp.text}")
                    raise ValueError(f"Gemini API returned status {resp.status_code}: {resp.text}")

        try:
            result_json = resp.json()
            candidates = result_json.get("candidates", [])
            if not candidates:
                raise ValueError("No candidates returned from Gemini.")

            raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()

            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]

            raw_parsed = json.loads(raw_text.strip())

            # 3. Pydantic Governance & Sanitization
            sanitized = DialogueSanitizerService.sanitize_gemini_payload(
                raw_payload=raw_parsed,
                speaker_1_name=speaker_1_name,
                speaker_2_name=speaker_2_name
            )
            sanitized["_route"] = route_used
            return sanitized

        except Exception as e:
            logger.error(f"Error during Gemini REST generation or sanitization: {e}")
            raise

gemini_service = GeminiAudioService()
