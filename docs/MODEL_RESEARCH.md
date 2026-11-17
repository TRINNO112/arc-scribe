# Google AI Studio & Gemini API Technical Research Report

Comprehensive investigation into model availability, free-tier quotas, multimodal audio processing, speaker diarization, and zero-cost fallback options for Arc Scribe.

---

## 1. Active Models in Google AI Studio (Free Tier)

When creating an API key on [Google AI Studio](https://aistudio.google.com/) without a linked credit card, the following models are available at zero cost:

| Model Identifier | Primary Use Case | Context Window | Free Quotas |
| :--- | :--- | :--- | :--- |
| **`gemini-2.0-flash`** | **Recommended Primary** (Multimodal, Low Latency) | 1,048,576 tokens | 15 RPM / 1M TPM / 1,500 RPD |
| **`gemini-2.0-flash-lite`** | Ultra-Fast High-Throughput / Classifications | 1,048,576 tokens | 30 RPM / 1M TPM / 1,500 RPD |
| **`gemini-1.5-flash`** | Production Long-Context Fallback | 1,048,576 tokens | 15 RPM / 1M TPM / 1,500 RPD |
| **`gemini-1.5-pro`** | Deep Reasoning & Complex Logic | 2,097,152 tokens | 2 RPM / 32K TPM / 50 RPD |

> **Privacy Note on Free Tier:** Free tier inputs/outputs may be reviewed by human reviewers to refine models (except in EEA, UK, Switzerland). Keep your API key private in `.env`.

---

## 2. Audio Processing Specifications

- **Supported Formats:** MP3, WAV, WEBM (Opus), M4A, AAC, FLAC, OGG.
- **Audio Tokenization Rate:** ~32 tokens per second of audio (~1,920 tokens per minute).
- **Audio Capacity:** A 1-million-token context window can ingest up to **~9.5 hours** of continuous audio in a single prompt.
- **Internal Downsampling:** Gemini automatically downsamples audio to 16 kbps mono for efficient phonetic processing.

---

## 3. Official SDK: `google-genai`

> ⚠️ The legacy `google-generativeai` package is deprecated. Always use `google-genai`.

### Installation
```bash
pip install google-genai
```

### Direct Inline Audio Ingest (Files < 20 MB)
```python
from google import genai
from google.genai import types

client = genai.Client()  # Reads GEMINI_API_KEY from environment

with open("roleplay_scene.webm", "rb") as f:
    audio_bytes = f.read()

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[
        types.Part.from_bytes(data=audio_bytes, mime_type="audio/webm"),
        "Transcribe this scene verbatim with speaker labels and emotional cues.",
    ],
)
print(response.text)
```

---

## 4. Multi-Speaker Diarization & Roleplay Context

Unlike standard speech-to-text engines that require separate acoustic clustering models, Gemini processes audio waveforms directly in the same embedding space as text.

When given character profiles before recording:
- **Speaker 1 (Me):** Deeper pitch, slower cadence $\rightarrow$ Mapped to *Character A*.
- **Speaker 2 (Brother):** Higher register, rapid tempo $\rightarrow$ Mapped to *Character B*.

Gemini binds acoustic characteristics directly to character personas and outputs structured JSON with:
1. `character`: Assigned persona name.
2. `dialogue_text`: Verbatim spoken words.
3. `vocal_tone`: Emotional delivery cues (e.g. `whispering, sarcastic`, `furious outburst`).
4. `physical_cue`: Inferred action or posture.

---

## 5. Free-Tier Fallback Providers

| Provider | Model | Free Allowance | Strength |
| :--- | :--- | :--- | :--- |
| **Groq Cloud** | `whisper-large-v3-turbo` | 2,000 RPD / 8 hrs audio daily | Fastest STT in the world (~2s for 1hr audio) |
| **Deepgram** | Nova-2 | $200 Free Lifetime Credit | Native acoustic diarization (`diarize=true`) |
| **Cloudflare Workers AI** | Whisper | 10,000 Neurons/Day (~4 hrs audio) | Serverless edge deployment |
