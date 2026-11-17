# Arc Scribe - API & Integration Specifications

This document defines the REST API contract, Google AI Studio configuration, environment variables, schema definitions, and client-side integration patterns for Arc Scribe.

---

## 1. Environment Configuration

Arc Scribe requires an API key from [Google AI Studio](https://aistudio.google.com/). Configuration is managed via environment variables and loaded from a `.env` file at the project root.

### Environment Variables (`.env`)

```bash
# Google AI Studio API Key (Required)
GEMINI_API_KEY=your_gemini_api_key_here

# Active Model: Default is gemini-3.8-flash (Free Tier)
# Fallback model: gemini-3.5-flash
GEMINI_MODEL=gemini-3.8-flash

# Backend Server Configuration
HOST=127.0.0.1
PORT=8000
DEBUG=false

# Rate Limiting & Safety Parameters
MAX_RPM_LIMIT=12
AUDIO_MAX_SIZE_MB=25
MAX_SCENE_DURATION_MINUTES=20
TEMP_AUDIO_DIR=./temp_audio
```

---

## 2. Google AI Studio SDK Configuration

Arc Scribe uses the official `google-genai` SDK (`from google import genai`) with structured JSON outputs and multimodal audio handling.

### SDK Initialization Example (`backend/gemini_client.py`)

```python
import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model_id = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


def generate_scene_transcription(audio_bytes: bytes, mime_type: str, system_prompt: str):
    """Processes audio input with structured JSON output."""
    response = client.models.generate_content(
        model=model_id,
        contents=[
            types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
            "Process this audio recording according to the system instructions."
        ],
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.2,  # Low temperature for verbatim accuracy
            response_mime_type="application/json"
        )
    )
    return response.text
```

---

## 3. Endpoints Specification

### 3.1. `POST /api/process-audio`

Receives the recorded dialogue audio and character metadata, passes it to Gemini 3.8 Flash, and returns structured dialogue, emotional inflection cues, scene beats, and drafted novel prose.

- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Rate Limit**: Max 12 requests/min per client IP

#### Form Parameters

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `audio` | File (Binary) | Yes | Audio file in `audio/webm`, `audio/ogg`, or `audio/wav` format. Max size 25MB. |
| `scene_title` | String | No | Title or working header for the scene (e.g., "The Grand Council Confrontation"). |
| `setting` | String | No | Setting context (e.g., "Dimly lit study during a rainstorm"). |
| `speaker_1_name` | String | Yes | Name of Character A voiced by Speaker 1 (e.g., "Lord Vane"). |
| `speaker_1_voice`| String | Yes | Voice traits for Speaker 1 (e.g., "Deeper pitch, slow measured cadence, cold authority"). |
| `speaker_2_name` | String | Yes | Name of Character B voiced by Speaker 2 (e.g., "Ethan"). |
| `speaker_2_voice`| String | Yes | Voice traits for Speaker 2 (e.g., "Higher pitch, breathy, agitated, faster cadence"). |
| `prose_style` | String | No | Narrative style: `"web_novel"` (default), `"grimdark"`, `"light_novel"`, or `"dialogue_only"`. |

#### Success Response (`200 OK`)

```json
{
  "status": "success",
  "metadata": {
    "scene_title": "The Grand Council Confrontation",
    "duration_seconds": 142.5,
    "model_used": "gemini-3.8-flash",
    "timestamp": "2026-11-17T21:45:00Z"
  },
  "speakers": {
    "speaker_1": {
      "character_name": "Lord Vane",
      "voice_profile": "Deeper pitch, slow measured cadence, cold authority"
    },
    "speaker_2": {
      "character_name": "Ethan",
      "voice_profile": "Higher pitch, breathy, agitated, faster cadence"
    }
  },
  "dialogue_script": [
    {
      "index": 1,
      "speaker_id": "speaker_1",
      "character_name": "Lord Vane",
      "dialogue": "You think you can walk out of this citadel after what you witnessed?",
      "emotional_cue": "low, menacing whisper; controlled breathing",
      "action_parenthetical": "leaning forward, resting palms on obsidian desk",
      "timestamp_estimate": "00:03 - 00:08"
    },
    {
      "index": 2,
      "speaker_id": "speaker_2",
      "character_name": "Ethan",
      "dialogue": "I saw your seals on the poison orders, Vane! I don't think—I know!",
      "emotional_cue": "strained, voice cracking at pitch peak, indignant fury",
      "action_parenthetical": "taking a sharp step back, hand hovering above hilt",
      "timestamp_estimate": "00:09 - 00:15"
    }
  ],
  "scene_beats": [
    {
      "beat_number": 1,
      "type": "Tension Escalation",
      "summary": "Lord Vane corners Ethan with an implicit death threat.",
      "emotional_shift": "Restrained menace to overt confrontation"
    },
    {
      "beat_number": 2,
      "type": "Climax Reveal",
      "summary": "Ethan reveals he found the poisoned seals.",
      "emotional_shift": "Defensive anxiety to desperate defiance"
    }
  ],
  "novel_draft": {
    "chapter_hook": "The silence in the high study was colder than the rain lashing against the diamond-paned glass.",
    "prose_text": "The silence in the high study was colder than the rain lashing against the diamond-paned glass.\n\n\"You think you can walk out of this citadel after what you witnessed?\" Lord Vane's voice didn't rise; it sank into a dark, gravelly murmur. He leaned over the obsidian surface of the desk, knuckles pressing pale against the stone.\n\nEthan stepped back, the leather of his boots squeaking against the wet flagstones. His chest heaved, adrenaline surging through his throat. \"I saw your seals on the poison orders, Vane!\" The younger man's pitch cracked on the patriarch's name, ragged and desperate. \"I don't think—I know!\"",
    "word_count": 108
  }
}
```

---

### 3.2. `GET /api/status`

Health check, Gemini API key validation, and live rate-limit tracking.

- **Method**: `GET`
- **Content-Type**: `application/json`

#### Success Response (`200 OK`)

```json
{
  "status": "healthy",
  "active_model": "gemini-3.8-flash",
  "api_key_configured": true,
  "rate_limits": {
    "rpm_limit": 15,
    "rpm_safety_ceiling": 12,
    "requests_last_minute": 2,
    "requests_remaining": 10,
    "cooldown_seconds": 0
  },
  "server_uptime_seconds": 3482
}
```

---

### 3.3. `POST /api/characters`

Saves or updates character vocal presets so the brothers do not have to retype voice profiles before each recording.

- **Method**: `POST`
- **Content-Type**: `application/json`

#### Request Payload

```json
{
  "characters": [
    {
      "id": "char_vane",
      "name": "Lord Vane",
      "default_speaker": "speaker_1",
      "voice_description": "Baritone, slow cadence, gravelly dry tone, haughty aristocratic pauses"
    },
    {
      "id": "char_ethan",
      "name": "Ethan",
      "default_speaker": "speaker_2",
      "voice_description": "Tenor, quick nervous pacing, sharp breathing, emotional pitch rises"
    }
  ]
}
```

#### Success Response (`200 OK`)

```json
{
  "status": "saved",
  "character_count": 2
}
```

---

### 3.4. `POST /api/export`

Exports the processed scene into formatted Markdown (`.md`), Plain Text (`.txt`), or HTML ready to be pasted into Scrivener, Google Docs, or Royal Road.

- **Method**: `POST`
- **Content-Type**: `application/json`

#### Request Payload

```json
{
  "scene_data": { "...processed scene JSON object..." },
  "format": "markdown",
  "include_dialogue_script": true,
  "include_scene_beats": true,
  "include_novel_prose": true
}
```

#### Success Response (`200 OK`)

- **Content-Type**: `text/markdown; charset=utf-8`
- **Body**: Formatted markdown with scene title, metadata, script, beats, and drafted prose.

---

## 4. Error Handling & HTTP Status Codes

Arc Scribe implements clear error envelopes for reliable frontend feedback:

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Free tier quota capacity reached. Please wait 18 seconds before sending the next scene.",
    "retry_after_seconds": 18
  }
}
```

### HTTP Status Code Reference

| Status Code | Code Identifier | Reason & Mitigation |
| :--- | :--- | :--- |
| `200 OK` | `SUCCESS` | Request succeeded; valid JSON payload returned. |
| `400 Bad Request` | `INVALID_PAYLOAD` | Missing audio file, missing character names, or unsupported audio codec. |
| `413 Payload Too Large`| `FILE_TOO_LARGE` | Audio exceeds 25MB. Suggest splitting the scene into smaller improv takes. |
| `429 Too Many Requests`| `RATE_LIMIT_EXCEEDED`| Gemini 15 RPM safety ceiling reached. Frontend displays a live cooldown countdown. |
| `500 Internal Error` | `PROCESSING_FAILED` | Gemini failed to parse audio. Raw audio remains safely cached in browser IndexedDB. |
| `503 Unavailable` | `GEMINI_UPSTREAM_ERROR` | Upstream Google AI Studio outage or network failure. Retry automatically with exponential backoff. |

---

## 5. Client-Side Integration Reference

### Audio Upload & Progress Handling (`frontend/app.js`)

```javascript
async function uploadAndProcessAudio(audioBlob, sceneData) {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'scene_recording.webm');
  formData.append('scene_title', sceneData.title);
  formData.append('setting', sceneData.setting);
  formData.append('speaker_1_name', sceneData.speaker1.name);
  formData.append('speaker_1_voice', sceneData.speaker1.voice);
  formData.append('speaker_2_name', sceneData.speaker2.name);
  formData.append('speaker_2_voice', sceneData.speaker2.voice);
  formData.append('prose_style', sceneData.proseStyle || 'web_novel');

  try {
    const response = await fetch('/api/process-audio', {
      method: 'POST',
      body: formData
    });

    if (response.status === 429) {
      const errorData = await response.json();
      const waitTime = errorData.error?.retry_after_seconds || 15;
      triggerCooldownTimer(waitTime);
      throw new Error(`Rate limit reached. Retry in ${waitTime}s.`);
    }

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.error?.message || 'Failed to process audio.');
    }

    const sceneResult = await response.json();
    renderSceneResults(sceneResult);
  } catch (error) {
    console.error('Arc Scribe processing error:', error);
    showNotification(error.message, 'error');
  }
}
```
