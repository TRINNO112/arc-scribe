from typing import List, Optional
from pydantic import BaseModel, Field

class DialogueLine(BaseModel):
    speaker: str = Field("Speaker 1", description="Name of speaker (e.g. Speaker 1 or Speaker 2)")
    speaker_id: Optional[str] = Field("speaker_1", description="'speaker_1' or 'speaker_2'")
    text: str = Field("", description="Verbatim spoken line")
    vocal_tone: Optional[str] = Field(None, description="Emotional inflection (e.g. whispering, furious, mocking scoff)")
    timestamp: Optional[str] = Field(None, description="Approximate time offset in the scene take")

class ProcessAudioResponse(BaseModel):
    success: bool = True
    dialogue_script: List[DialogueLine] = Field(default_factory=list)
    summary: Optional[str] = ""
    raw_audio_filename: Optional[str] = None
    processed_at: str

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
