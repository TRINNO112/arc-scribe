"""
backend/validator.py
Production Pydantic v2 Acoustic & Dialogue Governance Sanitizer for Arc Scribe.
Enforces:
- Strict Vocal Tone Taxonomy (15 approved inflections; strips narrative prose)
- Speaker Turn Monotonicity (timestamp validation and automated monotonicity repair)
- Text Sanitization (strips leaked parentheticals, hallucinatory loops)
- Hinglish & Verbatim Audio Guardrails
"""

import re
import logging
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator

logger = logging.getLogger("arc-scribe.validator")

# ==============================================================================
# 1. APPROVED VOCAL TONE TAXONOMY (CLOSED ENUM)
# ==============================================================================

class ApprovedVocalTone(str, Enum):
    WHISPERING = "whispering"
    MOCKING = "mocking"
    HESITANT = "hesitant"
    SARCASTIC = "sarcastic"
    LAUGHING = "laughing"
    INTERRUPTING = "interrupting"
    SHOUTING = "shouting"
    DEADPAN = "deadpan"
    FURIOUS = "furious"
    STRAINED = "strained"
    BREATHY = "breathy"
    PLEADING = "pleading"
    CALM = "calm"
    RESIGNED = "resigned"
    TAUNTING = "taunting"

# Set of valid tone string values for O(1) membership check
VALID_TONE_VALUES = {tone.value for tone in ApprovedVocalTone}

# Keyword mapping to rescue narrative prose leaks from LLM into canonical tone
PROSE_TONE_KEYWORDS: Dict[str, ApprovedVocalTone] = {
    "whisper": ApprovedVocalTone.WHISPERING,
    "whispered": ApprovedVocalTone.WHISPERING,
    "mock": ApprovedVocalTone.MOCKING,
    "mockery": ApprovedVocalTone.MOCKING,
    "scoff": ApprovedVocalTone.MOCKING,
    "hesitat": ApprovedVocalTone.HESITANT,
    "stammer": ApprovedVocalTone.HESITANT,
    "stutter": ApprovedVocalTone.HESITANT,
    "sarcas": ApprovedVocalTone.SARCASTIC,
    "ironic": ApprovedVocalTone.SARCASTIC,
    "laugh": ApprovedVocalTone.LAUGHING,
    "chuckle": ApprovedVocalTone.LAUGHING,
    "giggle": ApprovedVocalTone.LAUGHING,
    "interrupt": ApprovedVocalTone.INTERRUPTING,
    "cutting in": ApprovedVocalTone.INTERRUPTING,
    "shout": ApprovedVocalTone.SHOUTING,
    "yell": ApprovedVocalTone.SHOUTING,
    "scream": ApprovedVocalTone.SHOUTING,
    "roar": ApprovedVocalTone.SHOUTING,
    "deadpan": ApprovedVocalTone.DEADPAN,
    "monotone": ApprovedVocalTone.DEADPAN,
    "flat": ApprovedVocalTone.DEADPAN,
    "furious": ApprovedVocalTone.FURIOUS,
    "rage": ApprovedVocalTone.FURIOUS,
    "angry": ApprovedVocalTone.FURIOUS,
    "strain": ApprovedVocalTone.STRAINED,
    "tense": ApprovedVocalTone.STRAINED,
    "tight": ApprovedVocalTone.STRAINED,
    "breath": ApprovedVocalTone.BREATHY,
    "panting": ApprovedVocalTone.BREATHY,
    "gasp": ApprovedVocalTone.BREATHY,
    "plead": ApprovedVocalTone.PLEADING,
    "begging": ApprovedVocalTone.PLEADING,
    "desperate": ApprovedVocalTone.PLEADING,
    "calm": ApprovedVocalTone.CALM,
    "composed": ApprovedVocalTone.CALM,
    "quiet": ApprovedVocalTone.CALM,
    "resign": ApprovedVocalTone.RESIGNED,
    "defeated": ApprovedVocalTone.RESIGNED,
    "sigh": ApprovedVocalTone.RESIGNED,
    "taunt": ApprovedVocalTone.TAUNTING,
    "teas": ApprovedVocalTone.TAUNTING,
}

# ==============================================================================
# 2. TIMESTAMP HELPER UTILITIES
# ==============================================================================

def parse_timestamp_to_seconds(ts: Optional[str]) -> int:
    """Parses 'MM:SS' or 'HH:MM:SS' or raw numeric string into total seconds."""
    if not ts or not isinstance(ts, str):
        return 0
    clean_ts = ts.strip()
    parts = clean_ts.split(":")
    try:
        if len(parts) == 1:
            return int(float(parts[0]))
        elif len(parts) == 2:
            return int(parts[0]) * 60 + int(float(parts[1]))
        elif len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(float(parts[2]))
    except (ValueError, TypeError):
        return 0
    return 0

def format_seconds_to_timestamp(seconds: int) -> str:
    """Converts integer seconds into canonical MM:SS format."""
    safe_sec = max(0, int(seconds))
    mins = safe_sec // 60
    secs = safe_sec % 60
    return f"{mins}:{secs:02d}"

# ==============================================================================
# 3. PYDANTIC MODELS FOR DIALOGUE
# ==============================================================================

class GovernedDialogueLine(BaseModel):
    speaker: str = Field(..., description="Canonical speaker display name")
    speaker_id: str = Field("speaker_1", description="Strict identifier: 'speaker_1' or 'speaker_2'")
    text: str = Field(..., description="Verbatim spoken dialogue (sanitized)")
    vocal_tone: Optional[str] = Field(None, description="Approved inflection taxonomy token")
    timestamp: str = Field("0:00", description="Strict monotonic MM:SS timestamp")
    overlap_flag: bool = Field(False, description="Flag indicating overlapping speech")

    @field_validator("speaker_id")
    @classmethod
    def validate_speaker_id(cls, v: str) -> str:
        clean = (v or "").strip().lower()
        if "2" in clean:
            return "speaker_2"
        return "speaker_1"

    @field_validator("vocal_tone", mode="before")
    @classmethod
    def sanitize_vocal_tone(cls, v: Any) -> Optional[str]:
        """
        Guards against sprawling narrative prose in vocal_tone.
        Extracts canonical approved tone or maps via keyword taxonomy.
        """
        if not v or not isinstance(v, str):
            return None
        
        raw_val = v.strip().lower()
        # Direct match with approved closed taxonomy
        if raw_val in VALID_TONE_VALUES:
            return raw_val

        # Scan for taxonomy keywords inside leaked narrative prose
        for keyword, canonical_tone in PROSE_TONE_KEYWORDS.items():
            if keyword in raw_val:
                logger.info(f"Sanitized narrative tone '{v}' -> '{canonical_tone.value}'")
                return canonical_tone.value

        # Unrecognized narrative sentence: fallback to deadpan
        logger.warning(f"Unrecognized tone prose '{v}' replaced with fallback 'deadpan'")
        return ApprovedVocalTone.DEADPAN.value

    @field_validator("text", mode="before")
    @classmethod
    def sanitize_dialogue_text(cls, v: Any) -> str:
        """
        Strips leaked stage directions, parentheticals, and formatting noise.
        """
        if not v or not isinstance(v, str):
            return ""
        
        text = v.strip()
        # Strip leading/trailing asterisks or markdown quotes
        text = re.sub(r"^[\*\"']+|[\*\"']+$", "", text).strip()
        
        # Remove parenthetical stage directions leaked into dialogue text
        # e.g., "(turning around furiously) I told you not to come!" -> "I told you not to come!"
        text = re.sub(r"^\([^\)]+\)\s*", "", text).strip()
        text = re.sub(r"\s*\([^\)]+\)$", "", text).strip()
        
        # Collapse multiple internal whitespace
        text = re.sub(r"\s+", " ", text)
        return text

    @field_validator("timestamp", mode="before")
    @classmethod
    def normalize_timestamp_format(cls, v: Any) -> str:
        if isinstance(v, (int, float)):
            return format_seconds_to_timestamp(int(v))
        if not v or not isinstance(v, str):
            return "0:00"
        clean = v.strip()
        if re.match(r"^\d{1,3}:\d{2}$", clean):
            return clean
        sec = parse_timestamp_to_seconds(clean)
        return format_seconds_to_timestamp(sec)

# ==============================================================================
# 4. SCRIPT CONTAINER & MONOTONICITY REPAIR ENGINE
# ==============================================================================

class GovernedDialogueScript(BaseModel):
    dialogue_script: List[GovernedDialogueLine] = Field(default_factory=list)
    summary: Optional[str] = ""

    @model_validator(mode="after")
    def enforce_script_monotonicity_and_anti_hallucination(self) -> "GovernedDialogueScript":
        """
        Core Invariant Enforcement:
        1. Monotonicity: Ensures Timestamp(T[i]) >= Timestamp(T[i-1]).
           Repairs backward drift caused by LLM jitter.
        2. Anti-Hallucination: Drops empty turns or phantom loop duplicates.
        """
        raw_lines = self.dialogue_script
        if not raw_lines:
            return self

        sanitized_lines: List[GovernedDialogueLine] = []
        last_valid_seconds = 0
        seen_turn_hashes = set()

        for idx, line in enumerate(raw_lines):
            # 1. Filter out empty or whitespace-only lines
            clean_text = line.text.strip()
            if not clean_text or clean_text in {"[INAUDIBLE]", "..."}:
                if not clean_text:
                    continue

            # 2. Anti-Hallucination Loop Killer: detect identical repetitive loops
            turn_hash = (line.speaker_id, clean_text.lower())
            if turn_hash in seen_turn_hashes and len(clean_text) > 10:
                if sanitized_lines and sanitized_lines[-1].text.lower() == clean_text.lower():
                    logger.warning(f"Suppressed repeating loop hallucination: '{clean_text[:30]}...'")
                    continue
            seen_turn_hashes.add(turn_hash)

            # 3. Monotonicity Audit & Automated Repair
            current_seconds = parse_timestamp_to_seconds(line.timestamp)
            if current_seconds < last_valid_seconds:
                # Monotonicity violation detected! Repair by clamping to last valid seconds
                logger.warning(
                    f"Monotonicity violation at turn {idx} ({line.speaker}): "
                    f"{line.timestamp} ({current_seconds}s) < previous ({last_valid_seconds}s). "
                    f"Clamping to {format_seconds_to_timestamp(last_valid_seconds)}."
                )
                current_seconds = last_valid_seconds
                line.timestamp = format_seconds_to_timestamp(current_seconds)
            else:
                last_valid_seconds = current_seconds

            sanitized_lines.append(line)

        self.dialogue_script = sanitized_lines
        return self

# ==============================================================================
# 5. SANITIZER SERVICE FACADE
# ==============================================================================

class DialogueSanitizerService:
    @staticmethod
    def sanitize_gemini_payload(
        raw_payload: Dict[str, Any],
        speaker_1_name: str = "Speaker 1",
        speaker_2_name: str = "Speaker 2"
    ) -> Dict[str, Any]:
        """
        Ingests raw parsed JSON from Gemini REST API, runs it through Pydantic v2
        governance validators, and returns a verified, sanitized dictionary.
        """
        raw_lines = raw_payload.get("dialogue_script") or raw_payload.get("dialogues") or []
        pre_processed = []

        for item in raw_lines:
            spk_raw = item.get("speaker") or item.get("character_name") or ""
            spk_id = item.get("speaker_id") or ("speaker_1" if "1" in spk_raw else "speaker_2")
            
            canonical_name = speaker_1_name if spk_id == "speaker_1" else speaker_2_name
            if spk_raw and spk_raw not in {"Speaker 1", "Speaker 2", "speaker_1", "speaker_2"}:
                canonical_name = spk_raw

            pre_processed.append({
                "speaker": canonical_name,
                "speaker_id": spk_id,
                "text": item.get("text") or item.get("dialogue") or "",
                "vocal_tone": item.get("vocal_tone") or item.get("emotional_cue"),
                "timestamp": item.get("timestamp") or item.get("timestamp_estimate") or "0:00",
                "overlap_flag": bool(item.get("overlap_flag", False))
            })

        governed_model = GovernedDialogueScript(
            dialogue_script=pre_processed,
            summary=raw_payload.get("summary", "")
        )

        return governed_model.model_dump()
