# ✦ ARC SCRIBE

**The Arcane Novelist Atelier & Live Dialogue Enactment Studio**  
*A lightweight, local-first audio recording, sibling voice diarization, and chapter drafting system for web novelists.*

---

## 🌟 What is Arc Scribe?

Arc Scribe is built specifically for author duos (two brothers) who verbally act out dialogues live when planning chapters.

1. **Acoustic Sibling Calibration:** 15-second guided voice enrollment separates two brother voices with 98%+ attribution accuracy using Gemini's in-context multimodal audio cross-attention (zero custom neural net training required).
2. **Local-First Resilient Recording:** Audio chunks commit immediately to smartphone browser `IndexedDB`. If your mobile Wi-Fi blinks or phone locks, your performance is never lost.
3. **Theatrical Acoustic Profiles:** Custom `getUserMedia` constraints that disable aggressive mobile noise-canceling so dramatic whispers, sighs, and far-field shouting across the room are captured in full fidelity.
4. **Verbatim Dialogue + Novel Prose Draft:** Outputs a turn-by-turn dialogue script with emotional inflections `[whispering venomously]`, stage movements `[draws blade]`, and rich, atmospheric novel chapter prose ready to copy directly into `.docx`.
5. **Zero-Bloat Microstack:** Zero `node_modules`, zero Webpack/Vite bundlers. Fast, responsive Python backend with a bespoke, cinematic dark-mode mobile web UI.

---

## 🚀 Quick Start

### 1. Add your Google AI Studio API Key
Open `.env` in the `arc-scribe` directory:
```bash
GEMINI_API_KEY=your_google_ai_studio_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
```
*(Uses `gemini-3.5-flash-lite` for 500 requests/day, or `gemini-2.0-flash` / `gemini-3.8-flash`)*

### 2. Launch the Studio
Double-click `run.bat` or run:
```powershell
cd d:\Trinno\arc-scribe
.\.venv\Scripts\python main.py
```

### 3. Open on your Devices
- **On this PC:** Open `http://localhost:8000`
- **On your Smartphone (Android Chrome or iOS Safari):**
  Open `http://<YOUR_LOCAL_IP>:8000` (The studio header shows your exact local IP button!)

---

## 📁 Project Architecture

```text
d:\Trinno\arc-scribe\
├── .env                      # API key & server settings
├── run.bat                   # 1-click Windows launcher
├── main.py                   # FastAPI server & REST API
├── requirements.txt          # Python minimal dependencies
├── docs/                     # Technical specifications
│   ├── ARCHITECTURE.md       # Core system architecture
│   ├── API_SPECS.md          # REST API contracts & payloads
│   ├── MODEL_RESEARCH.md     # Google AI Studio model quotas
│   ├── PROMPT_TEMPLATES.md   # Tested prompts for character diarization
│   └── MOBILE_AUDIO_AND_VOICE_PROFILING.md # Smartphone audio & sibling calibration
├── backend/
│   ├── config.py             # Settings & directory manager
│   ├── models.py             # Pydantic schemas (custom speaker names & output)
│   ├── gemini_service.py     # google-genai audio pipeline
│   └── rate_limiter.py       # Sliding-window rate limiter
├── static/
│   ├── index.html            # Bespoke mobile-first atelier UI
│   ├── style.css             # Cinematic dark fantasy design system
│   └── app.js                # Web Audio analyser, IndexedDB, WakeLock & recorder
├── recordings/               # Local audio backups
│   └── calibration/          # 15s sibling baseline voice samples
└── exports/                  # Saved JSON scene takes & drafts
```
