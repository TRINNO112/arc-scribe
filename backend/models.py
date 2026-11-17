from typing import List, Optional
from pydantic import BaseModel, Field

class DialogueLine(BaseModel):
    speaker: str = Field(..., description="Name of speaker (e.g. Author 1 or Author 2)")
    character: str = Field(..., description="Character persona name in the novel")
    dialogue: str = Field(..., description="Verbatim spoken line")
    vocal_tone: Optional[str] = Field(None, description="Emotional inflection (e.g. whispering, furious, mocking scoff)")
    physical_cue: Optional[str] = Field(None, description="Implied stage direction, gesture, or physical action")
    timestamp: Optional[str] = Field(None, description="Approximate time offset in the scene take")

class SceneBeat(BaseModel):
    beat_number: int
    title: str
    description: str
    dramatic_tension: Optional[str] = Field(None, description="Tension rating: Low, Medium, High, Climax")

class ProcessAudioResponse(BaseModel):
    success: bool
    arc_title: str
    summary: str
    dialogues: List[DialogueLine]
    scene_beats: List[SceneBeat]
    novel_prose_draft: str
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
