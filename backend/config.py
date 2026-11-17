import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "Arc Scribe"
    VERSION: str = "1.0.0"
    
    # AI Studio Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    
    # Server Network Binding
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Directories
    RECORDINGS_DIR: Path = BASE_DIR / "recordings"
    CALIBRATION_DIR: Path = BASE_DIR / "recordings" / "calibration"
    EXPORTS_DIR: Path = BASE_DIR / "exports"
    STATIC_DIR: Path = BASE_DIR / "static"
    
    # Rate Limits (Safe defaults matching user's AI Studio quotas)
    MAX_RPM: int = 15
    SAFETY_RPM_CEILING: int = 12

settings = Settings()

# Ensure required directories exist
settings.RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
settings.CALIBRATION_DIR.mkdir(parents=True, exist_ok=True)
settings.EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
settings.STATIC_DIR.mkdir(parents=True, exist_ok=True)
