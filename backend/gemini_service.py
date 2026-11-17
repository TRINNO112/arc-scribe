import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from backend.config import settings

logger = logging.getLogger("arc-scribe.gemini")

class GeminiAudioService:
    def __init__(self):
        self._client = None

    def get_client(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is not configured! Please open arc-scribe/.env and add your Google AI Studio API key."
            )
        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
            except Exception as e:
                logger.error(f"Failed to initialize google-genai Client: {e}")
                raise
        return self._client

    def is_configured(self) -> bool:
        return bool(settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY.strip()) > 10)

    async def process_enactment_audio(
        self,
        scene_audio_bytes: bytes,
        mime_type: str,
        arc_title: str,
        speaker_1_name: str,
        speaker_1_char: str,
        speaker_1_notes: str,
        speaker_2_name: str,
        speaker_2_char: str,
        speaker_2_notes: str,
        scene_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Sends raw scene audio + optional calibration anchors to Gemini for speaker diarization and novel prose synthesis."""
        client = self.get_client()
        from google.genai import types

        contents = []

        # 1. Attach Acoustic Calibration Anchors if they exist
        spk1_cal_path = settings.CALIBRATION_DIR / "speaker_1_calibration.webm"
        spk2_cal_path = settings.CALIBRATION_DIR / "speaker_2_calibration.webm"

        calibration_context_notes = []

        if spk1_cal_path.exists():
            with open(spk1_cal_path, "rb") as f:
                spk1_bytes = f.read()
            contents.append("=== ACOUSTIC REFERENCE 1: " + speaker_1_name + " (BASELINE VOICE PROFILE) ===")
            contents.append(types.Part.from_bytes(data=spk1_bytes, mime_type="audio/webm"))
            calibration_context_notes.append(f"Acoustic Reference 1 represents {speaker_1_name} ({speaker_1_char}).")

        if spk2_cal_path.exists():
            with open(spk2_cal_path, "rb") as f:
                spk2_bytes = f.read()
            contents.append("=== ACOUSTIC REFERENCE 2: " + speaker_2_name + " (BASELINE VOICE PROFILE) ===")
            contents.append(types.Part.from_bytes(data=spk2_bytes, mime_type="audio/webm"))
            calibration_context_notes.append(f"Acoustic Reference 2 represents {speaker_2_name} ({speaker_2_char}).")

        # 2. Attach Target Scene Enactment Audio
        contents.append("=== TARGET ENACTMENT SCENE AUDIO ===")
        contents.append(types.Part.from_bytes(data=scene_audio_bytes, mime_type=mime_type))

        # 3. Assemble Structured Prompt
        prompt = f"""
You are Arc Scribe, an expert creative AI assistant for a collaborative web novel author duo who act out character dialogues live.

### SCENE METADATA:
- Arc / Chapter: {arc_title}
- Context / Setting: {scene_context or 'Live improv scene enactment.'}

### SPEAKER & CHARACTER PROFILES:
- SPEAKER 1:
  * Real Name / Label: {speaker_1_name}
  * Character Played: {speaker_1_char}
  * Vocal / Acting Notes: {speaker_1_notes or 'Author 1 natural register.'}
- SPEAKER 2:
  * Real Name / Label: {speaker_2_name}
  * Character Played: {speaker_2_char}
  * Vocal / Acting Notes: {speaker_2_notes or 'Author 2 natural register.'}

{' '.join(calibration_context_notes)}

### YOUR TASKS:
1. DIARIZE & TRANSCRIBE:
   - Identify who is speaking each line ({speaker_1_name} as {speaker_1_char} vs {speaker_2_name} as {speaker_2_char}).
   - Transcribe every spoken line VERBATIM. Do not sanitize, skip, or summarize lines.
   - Capture nuanced emotional delivery in 'vocal_tone' (e.g. whispering with suppressed fury, mocking scoff, stammering, sudden violent shout).
   - Infer physical gestures or stage movements in 'physical_cue' (e.g. [paces backward], [draws blade], [slams table]).
   - Record approximate timestamps.

2. SCENE BEATS BREAKDOWN:
   - Break down the narrative flow into chronological beats with dramatic tension ratings (Low, Medium, High, Climax).

3. NOVELIZED PROSE DRAFT:
   - Transform this raw spoken dialogue and its emotional energy into a rich, immersive novel scene draft with evocative sensory descriptions, internal thoughts, and atmospheric prose, ready to paste directly into a web novel chapter document.

Respond ONLY with valid JSON conforming to this exact structure:
{{
  "arc_title": "{arc_title}",
  "summary": "Short 2-3 sentence overview of what occurred in this scene.",
  "dialogues": [
    {{
      "speaker": "{speaker_1_name} or {speaker_2_name}",
      "character": "{speaker_1_char} or {speaker_2_char}",
      "dialogue": "Exact spoken words",
      "vocal_tone": "e.g. (whispering venomously)",
      "physical_cue": "e.g. [steps into the lantern light]",
      "timestamp": "0:14"
    }}
  ],
  "scene_beats": [
    {{
      "beat_number": 1,
      "title": "Beat Title",
      "description": "What happens in this beat",
      "dramatic_tension": "Medium"
    }}
  ],
  "novel_prose_draft": "Full atmospheric web novel chapter prose rendering of the scene..."
}}
"""
        contents.append(prompt)

        # 4. Invoke Model
        model_name = settings.GEMINI_MODEL
        logger.info(f"Invoking {model_name} for scene '{arc_title}'...")

        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,  # Low temperature for verbatim transcription accuracy
                )
            )
            raw_text = response.text.strip()
            # Clean possible markdown wrapping if returned
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            
            parsed = json.loads(raw_text.strip())
            return parsed
        except Exception as e:
            logger.error(f"Error during Gemini generation: {e}")
            raise

gemini_service = GeminiAudioService()
