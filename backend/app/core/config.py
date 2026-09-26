"""Centralized application configuration."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_DIR = Path(__file__).resolve().parents[2]

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{PROJECT_DIR}/storage/app.db")
UPLOADS_DIR = Path(os.getenv("UPLOADS_DIR", PROJECT_DIR / "storage" / "uploads"))
OUTPUTS_DIR = Path(os.getenv("OUTPUTS_DIR", PROJECT_DIR / "storage" / "outputs"))
FFMPEG_BINARY = os.getenv("FFMPEG_BINARY", "ffmpeg")

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
TRANSLATION_MODEL = os.getenv("TRANSLATION_MODEL", "gpt-4.1-mini")
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "edge").strip().lower()  # edge | openai

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-secret-change-me")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(2 * 1024**3)))
MAX_URL_DOWNLOAD_BYTES = int(os.getenv("MAX_URL_DOWNLOAD_BYTES", str(2 * 1024**3)))

FREE_TRIAL_MINUTES = int(os.getenv("FREE_TRIAL_MINUTES", "30"))
WORKER_POLL_INTERVAL = float(os.getenv("WORKER_POLL_INTERVAL", "2.0"))

for _d in (UPLOADS_DIR, OUTPUTS_DIR):
    _d.mkdir(parents=True, exist_ok=True)
