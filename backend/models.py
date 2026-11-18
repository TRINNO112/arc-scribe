from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class DialogueLine(BaseModel):
    speaker: str = Field("Speaker 1", description="Name of speaker (e.g. Speaker 1 or Speaker 2)")
    speaker_id: Optional[str] = Field("speaker_1", description="'speaker_1' or 'speaker_2'")
    text: str = Field("", description="Verbatim spoken line")
    vocal_tone: Optional[str] = Field(None, description="Emotional inflection (e.g. whispering, furious, mocking)")
    timestamp: Optional[str] = Field(None, description="Approximate time offset in the scene take")
    overlap_flag: bool = Field(False, description="Flag indicating simultaneous or interrupted speech")

class ProcessAudioResponse(BaseModel):
    success: bool = True
    dialogue_script: List[DialogueLine] = Field(default_factory=list)
    summary: Optional[str] = ""
    raw_audio_filename: Optional[str] = None
    processed_at: str

class SpeakerAcousticProfile(BaseModel):
    speaker_id: str = Field(..., description="'speaker_1' or 'speaker_2'")
    real_name: str = Field(..., description="Real name of brother (e.g. Amit)")
    display_name: str = Field(..., description="UI display label")
    character_counterpart: str = Field(..., description="Character name")
    pitch_register: str = Field("Chest Baritone (95-135 Hz)", description="Baseline fundamental frequency band")
    timbre_description: str = Field("Deeper, resonant, gravelly vocal fry", description="Vocal tract characteristics")
    speech_tempo: str = Field("Measured, steady pauses", description="Tempo & rhythm profile")
    linguistic_quirks: str = Field("Grounded Hindi/Hinglish phrasing", description="Language & dialect quirks")
    audio_filename: str = Field(..., description="Relative file path")
    duration_seconds: float = Field(0.0, description="Anchor duration")
    file_size_bytes: int = Field(0, description="Payload byte size")
    sha256_hash: Optional[str] = Field(None, description="Integrity checksum")
    calibrated_at: str = Field(..., description="ISO 8601 timestamp")

class CalibrationManifest(BaseModel):
    version: str = "1.0.0"
    updated_at: str
    room_environment: Optional[str] = "Normal Living Room / Moderate Reverb"
    speakers: Dict[str, SpeakerAcousticProfile] = Field(default_factory=dict)

class CalibrationUploadResponse(BaseModel):
    success: bool
    speaker_id: str
    message: str
    profile: Optional[SpeakerAcousticProfile] = None

class CalibrationResponse(BaseModel):
    success: bool
    speaker_id: str
    speaker_name: str
    audio_path: str
    message: str

class ServerStatusResponse(BaseModel):
    status: str
    version: str
    model: str
    api_key_configured: bool
    speaker_1_calibrated: bool
    speaker_2_calibrated: bool
    recordings_count: int
