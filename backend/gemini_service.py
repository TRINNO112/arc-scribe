import os
import json
import base64
import socket
import logging
import requests
from typing import Optional, Dict, Any
from backend.config import settings

logger = logging.getLogger("arc-scribe.gemini")

class GeminiAudioService:
    def __init__(self):
        pass

    def is_configured(self) -> bool:
        return bool(settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY.strip()) > 10)

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
        Sends raw voice audio to Gemini (gemini-3.5-flash-lite) via HTTP/1.1 REST.
        Performs speaker diarization between the two brothers and generates clean dialogue script.
        """
        if not self.is_configured():
            raise ValueError("GEMINI_API_KEY is not configured! Please set it in arc-scribe/.env")

        api_key = settings.GEMINI_API_KEY.strip()
        model = settings.GEMINI_MODEL or "gemini-3.5-flash-lite"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        # 1. Base64 encode the audio file
        audio_b64 = base64.b64encode(scene_audio_bytes).decode("utf-8")
        clean_mime = mime_type.split(";")[0].strip() or "audio/webm"

        # 2. System Instruction / Prompt for Sibling Diarization
        system_prompt = """
You are Arc Scribe, an expert voice diarization and script generation assistant for two brothers recording spoken dialogue.
Your mission is to separate their voices into a clean, verbatim dialogue script.

CRITICAL INSTRUCTIONS:
1. DIARIZE SPEAKERS: Identify when Speaker 1 is speaking vs Speaker 2 based on vocal pitch, timbre, cadence, and conversational turn-taking.
2. VERBATIM ACCURACY: Transcribe the spoken dialogue accurately without omitting words.
3. CAPTURE VOCAL INFLECTIONS: Tag tone and emotional delivery in 'vocal_tone' (e.g. whispering, laughing, mocking, hesitant, sarcastic, shouting, interrupting).
4. CHRONOLOGICAL ORDER: Return the dialogue lines strictly in the order they were spoken.

Respond ONLY with valid JSON in this exact structure:
{
  "dialogue_script": [
    {
      "speaker": "Speaker 1",
      "speaker_id": "speaker_1",
      "text": "Exact transcribed spoken words",
      "vocal_tone": "e.g. laughing or whispering",
      "timestamp": "0:05"
    },
    {
      "speaker": "Speaker 2",
      "speaker_id": "speaker_2",
      "text": "Next response line",
      "vocal_tone": "e.g. sarcastic scoff",
      "timestamp": "0:09"
    }
  ]
}
"""

        parts = [
            {"text": system_prompt},
            {
                "inlineData": {
                    "mimeType": clean_mime,
                    "data": audio_b64
                }
            }
        ]

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.2
            }
        }

        headers = {"Content-Type": "application/json"}
        route_used = "Direct Route"
        resp = None

        logger.info(f"Invoking {model} for dialogue analysis ({len(scene_audio_bytes)} bytes)...")

        # 1. Primary Attempt: Direct TCP connection (Main connection, zero proxy dependency)
        try:
            logger.info("Attempting primary direct TCP connection to Google AI Studio...")
            resp = requests.post(
                url,
                headers=headers,
                json=payload,
                proxies=None,
                timeout=30
            )
            route_used = "Direct Route"
        except requests.exceptions.RequestException as direct_err:
            logger.warning(f"Primary direct connection failed ({direct_err}). Testing backup proxy failover...")
            
            # 2. Automatic Backup Failover: Check if backup proxy server is reachable
            backup_proxies = self.get_backup_proxies()
            if backup_proxies:
                logger.info("Backup proxy server detected & reachable. Engaging backup proxy route...")
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
                    raise ValueError(
                        f"Both primary connection ({direct_err}) and backup proxy ({proxy_err}) failed to reach Gemini API."
                    )
            else:
                logger.error(f"Primary connection failed and backup proxy is not reachable: {direct_err}")
                raise ValueError(
                    f"Main connection failed ({direct_err}), and backup proxy server is offline or unreachable."
                )

        if resp is None:
            raise ValueError("No response received from Gemini API.")

        if resp.status_code != 200:
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

            parsed = json.loads(raw_text.strip())
            
            # Normalization fallback for frontend compatibility
            if "dialogue_script" not in parsed and "dialogues" in parsed:
                parsed["dialogue_script"] = parsed["dialogues"]

            parsed["_route"] = route_used
            return parsed

        except Exception as e:
            logger.error(f"Error during Gemini REST generation: {e}")
            raise

gemini_service = GeminiAudioService()
