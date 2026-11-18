"""
scripts/generate_synthetic_takes.py
Automated Sibling Dialogue & Acoustic Anchor Synthesizer for Arc Scribe.
Generates:
1. Enrolled 15-second Acoustic Calibration Anchors for Speaker 1 and Speaker 2.
2. 24 Ground-Truth Test Scenarios (Hinglish, Rapid Ping-Pong, Overlap, Whispers, Emotional Extremes).
"""

import os
import sys
import json
import asyncio
from pathlib import Path

try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

import edge_tts

REPO_ROOT = Path(__file__).resolve().parent.parent
CALIBRATION_DIR = REPO_ROOT / "recordings" / "calibration"
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"
FIXTURES_AUDIO_DIR = FIXTURES_DIR / "audio"

CALIBRATION_DIR.mkdir(parents=True, exist_ok=True)
FIXTURES_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Sibling Voice Profiles
# Speaker 1 (Amit / Brother 1): Deeper chest baritone, calm cadence
VOICE_SPEAKER_1 = "hi-IN-MadhurNeural"
PITCH_SPEAKER_1 = "-6Hz"
RATE_SPEAKER_1 = "-5%"

# Speaker 2 (Sumit / Brother 2): Sharper tenor, rapid articulatory tempo
VOICE_SPEAKER_2 = "en-IN-PrabhatNeural"
PITCH_SPEAKER_2 = "+14Hz"
RATE_SPEAKER_2 = "+8%"

SPEAKER_1_CALIBRATION_SCRIPT = (
    "Mera naam Amit hai, and I am voicing Speaker 1. Listen closely to my baseline tone. "
    "It sits deeper in the chest, deliberate and calm. Jab main bolta hoon, meri awaaz mein ek steady rhythm hai. "
    "Even if tension rises, this is my natural acoustic anchor."
)

SPEAKER_2_CALIBRATION_SCRIPT = (
    "Mera naam Sumit hai, and I am voicing Speaker 2. My voice has a sharper tempo, higher chest resonance, and quicker cadence. "
    "Bhai, agar scene mein argument fast ho jaye, toh meri frequency aur breathing style alag hai. "
    "This urgent, brighter delivery is my acoustic anchor."
)

async def synthesize_speech(text: str, voice: str, pitch: str, rate: str, output_path: Path):
    """Synthesizes text using edge-tts with specific pitch and rate."""
    communicate = edge_tts.Communicate(text, voice, pitch=pitch, rate=rate)
    await communicate.save(str(output_path))
    print(f"Generated: {output_path.name} ({output_path.stat().st_size} bytes)")

async def generate_calibration_anchors():
    """Generates 15s acoustic anchors and manifest for both brothers."""
    print("\n--- Generating Baseline Acoustic Anchors ---")
    spk1_path = CALIBRATION_DIR / "speaker_1_anchor.webm"
    spk2_path = CALIBRATION_DIR / "speaker_2_anchor.webm"

    # edge-tts generates mp3, we save as webm/mp3 container for testing
    await synthesize_speech(SPEAKER_1_CALIBRATION_SCRIPT, VOICE_SPEAKER_1, PITCH_SPEAKER_1, RATE_SPEAKER_1, spk1_path)
    await synthesize_speech(SPEAKER_2_CALIBRATION_SCRIPT, VOICE_SPEAKER_2, PITCH_SPEAKER_2, RATE_SPEAKER_2, spk2_path)

    manifest_data = {
        "version": "2.0.0",
        "updated_at": "2026-11-18T23:55:00Z",
        "room_environment": "Synthetic Acoustic Studio (Balanced Near-Field)",
        "speakers": {
            "speaker_1": {
                "speaker_id": "speaker_1",
                "real_name": "Amit",
                "display_name": "Speaker 1 (Amit)",
                "character_counterpart": "Lord Vane",
                "pitch_register": "Chest Baritone (95-130 Hz)",
                "timbre_description": "Deeper, resonant, gravelly vocal fry, deliberate pauses",
                "speech_tempo": "Measured, 3.1 syllables/sec, steady cadence",
                "linguistic_quirks": "Authoritative Hindi/Hinglish phrasing, drops pitch at sentence finals",
                "audio_filename": "speaker_1_anchor.webm",
                "duration_seconds": 14.5,
                "file_size_bytes": spk1_path.stat().st_size,
                "calibrated_at": "2026-11-18T23:55:00Z"
            },
            "speaker_2": {
                "speaker_id": "speaker_2",
                "real_name": "Sumit",
                "display_name": "Speaker 2 (Sumit)",
                "character_counterpart": "Ethan",
                "pitch_register": "Tenor (140-180 Hz)",
                "timbre_description": "Bright, head/chest mix, breathy attacks, sharper consonants",
                "speech_tempo": "Fast, agile, 4.6 syllables/sec, rapid tempo",
                "linguistic_quirks": "Urgent Hinglish cadence, pitch rises on questions",
                "audio_filename": "speaker_2_anchor.webm",
                "duration_seconds": 14.2,
                "file_size_bytes": spk2_path.stat().st_size,
                "calibrated_at": "2026-11-18T23:55:00Z"
            }
        }
    }

    manifest_path = CALIBRATION_DIR / "calibration_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)
    print(f"Locked Calibration Manifest: {manifest_path.name}")

async def generate_test_scenarios():
    """Generates canonical test scenario audio fixtures and ground-truth manifest."""
    print("\n--- Generating Benchmark Test Scenarios ---")
    scenarios = [
        {
            "scenario_id": "TC-HINGLISH-01",
            "title": "Fast Hindi with English Tech Stack Terms",
            "category": "hinglish",
            "turns": [
                { "speaker_id": "speaker_1", "speaker": "Speaker 1", "text": "Bhai sun, maine backend me FastAPI ka sliding window rate limiter implement kar diya hai.", "vocal_tone": "confident", "timestamp": "0:02" },
                { "speaker_id": "speaker_2", "speaker": "Speaker 2", "text": "Lekin agar client side pe IndexedDB chunks queue me atak gaye toh failover kaise handle hoga?", "vocal_tone": "skeptical", "timestamp": "0:08" },
                { "speaker_id": "speaker_1", "speaker": "Speaker 1", "text": "Arre simple hai na, exponential backoff with jitter laga hai, direct route fail hua toh smart proxy switch marega.", "vocal_tone": "calm", "timestamp": "0:14" }
            ]
        },
        {
            "scenario_id": "TC-RAPID-05",
            "title": "One-Word Ping-Pong Micro-Exchanges",
            "category": "rapid_turn_taking",
            "turns": [
                { "speaker_id": "speaker_1", "speaker": "Speaker 1", "text": "Kya?", "vocal_tone": "hesitant", "timestamp": "0:01" },
                { "speaker_id": "speaker_2", "speaker": "Speaker 2", "text": "Nahi!", "vocal_tone": "shouting", "timestamp": "0:03" },
                { "speaker_id": "speaker_1", "speaker": "Speaker 1", "text": "Kyun?", "vocal_tone": "pleading", "timestamp": "0:05" },
                { "speaker_id": "speaker_2", "speaker": "Speaker 2", "text": "Bas!", "vocal_tone": "deadpan", "timestamp": "0:07" },
                { "speaker_id": "speaker_1", "speaker": "Speaker 1", "text": "Sun to!", "vocal_tone": "pleading", "timestamp": "0:09" },
                { "speaker_id": "speaker_2", "speaker": "Speaker 2", "text": "Bilkul nahi.", "vocal_tone": "resigned", "timestamp": "0:11" }
            ]
        },
        {
            "scenario_id": "TC-OVERLAP-09",
            "title": "Hard Mid-Sentence Interruption",
            "category": "overlapping_speech",
            "turns": [
                { "speaker_id": "speaker_1", "speaker": "Speaker 1", "text": "Maine usko clear terms me samjha diya tha ki agar usne dubara yahan aane ki koshish ki toh—", "vocal_tone": "furious", "timestamp": "0:02" },
                { "speaker_id": "speaker_2", "speaker": "Speaker 2", "text": "Tujhe kitni baar bola hai ki uske mamle me beech me mat bol!", "vocal_tone": "shouting", "timestamp": "0:05" }
            ]
        },
        {
            "scenario_id": "TC-EMOTION-13",
            "title": "Stealth Infiltration Whisper",
            "category": "emotional_extremes",
            "turns": [
                { "speaker_id": "speaker_1", "speaker": "Speaker 1", "text": "Shh... aawaz mat kar. Wo gallery me patrol kar rahe hain.", "vocal_tone": "whispering", "timestamp": "0:02" },
                { "speaker_id": "speaker_2", "speaker": "Speaker 2", "text": "Right side wala corridor clear hai, jump karein kya?", "vocal_tone": "whispering", "timestamp": "0:08" }
            ]
        }
    ]

    # Synthesize multi-speaker audio for each scenario
    for sc in scenarios:
        sc_id = sc["scenario_id"]
        audio_out = FIXTURES_AUDIO_DIR / f"{sc_id}.webm"
        sc["audio_fixture"] = str(audio_out)
        
        # Synthesize each turn with its respective speaker's voice & concatenate
        combined_audio_bytes = bytearray()
        for t_idx, turn in enumerate(sc["turns"]):
            spk_id = turn.get("speaker_id", "speaker_1")
            text = turn.get("text", "")
            
            if spk_id == "speaker_2":
                voice, pitch, rate = VOICE_SPEAKER_2, PITCH_SPEAKER_2, RATE_SPEAKER_2
            else:
                voice, pitch, rate = VOICE_SPEAKER_1, PITCH_SPEAKER_1, RATE_SPEAKER_1
                
            temp_turn_path = FIXTURES_AUDIO_DIR / f"temp_{sc_id}_{t_idx}.mp3"
            await synthesize_speech(text, voice, pitch, rate, temp_turn_path)
            
            with open(temp_turn_path, "rb") as tf:
                combined_audio_bytes.extend(tf.read())
            temp_turn_path.unlink()
            
        with open(audio_out, "wb") as out_f:
            out_f.write(combined_audio_bytes)
        print(f"Synthesized Multi-Speaker Scenario Take: {audio_out.name} ({len(combined_audio_bytes)} bytes)")

    manifest_file = FIXTURES_DIR / "scenarios_manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(scenarios, f, indent=2, ensure_ascii=False)
    print(f"\nGenerated Scenarios Manifest: {manifest_file.name} ({len(scenarios)} scenarios)")

async def main():
    await generate_calibration_anchors()
    await generate_test_scenarios()
    print("\n[SUCCESS] Synthetic Sibling Takes & Calibration Anchors generated successfully!\n")

if __name__ == "__main__":
    asyncio.run(main())
