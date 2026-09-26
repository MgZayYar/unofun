"""Dubbing API: languages, voices, job lifecycle, downloads."""

import math
import tempfile
from pathlib import Path

import edge_tts
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.ai.dubbing.providers import get_provider
from app.api.deps import current_user, db_session
from app.core import config
from app.models import TERMINAL_STATUSES, DubJob, User, Video
from app.schemas import DubJobResponse, DubStartRequest, LanguageInfo, VoicePreviewRequest
from app.services.languages import BY_CODE, LANGUAGES, OPENAI_VOICES, resolve_voice

router = APIRouter(prefix="/api/dub", tags=["dub"])


def _response(job: DubJob) -> DubJobResponse:
    return DubJobResponse(
        id=job.id,
        video_id=job.video_id,
        target_language=job.target_language,
        voice=job.voice,
        status=job.status,
        stage=job.stage,
        progress=job.progress,
        error_message=job.error_message,
        minutes_charged=job.minutes_charged,
        created_at=job.created_at,
        finished_at=job.finished_at,
    )


@router.get("/languages", response_model=list[LanguageInfo])
def languages():
    provider = config.TTS_PROVIDER
    out = []
    for entry in LANGUAGES:
        voices = OPENAI_VOICES if provider == "openai" else entry["voices"]
        out.append(LanguageInfo(code=entry["code"], name=entry["name"], voices=voices))
    return out


@router.get("/voices")
async def voices(language: str | None = None):
    """Live voice list from the configured TTS provider (Edge TTS by default)."""
    provider = get_provider("openai" if config.TTS_PROVIDER == "openai" else "edge")
    listed = await provider.list_voices(language)
    return [{"id": v.id, "name": v.name, "language": v.language, "gender": v.gender} for v in listed]


@router.post("/preview")
async def preview_voice(payload: VoicePreviewRequest):
    """Render a short TTS sample so users can hear a voice before dubbing."""
    text = payload.text or "Hello! This is a preview of how your dubbed video will sound."
    provider = get_provider("openai" if config.TTS_PROVIDER == "openai" else "edge")
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        path = Path(tmp.name)
    try:
        await provider.synthesize(text, payload.voice, path)
        return FileResponse(path, media_type="audio/mpeg", filename="preview.mp3")
    except Exception:
        path.unlink(missing_ok=True)
        raise


@router.post("/start", response_model=DubJobResponse, status_code=status.HTTP_201_CREATED)
def start_dub(payload: DubStartRequest, db: Session = Depends(db_session),
              user: User = Depends(current_user)):
    if payload.target_language not in BY_CODE:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            f"Unsupported language: {payload.target_language}")
    video = db.query(Video).filter(Video.id == payload.video_id,
                                   Video.user_id == user.id).first()
    if video is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Video not found")
    if payload.voice:
        resolve_voice(payload.target_language, payload.voice)  # validates; raises ValueError
    minutes = max(1, math.ceil((video.duration_seconds or 60) / 60))
    if user.credits_minutes < minutes:
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED,
                            f"Not enough credits: this dub needs {minutes} minute(s), "
                            f"you have {user.credits_minutes}.")
    user.credits_minutes -= minutes
    job = DubJob(user_id=user.id, video_id=video.id,
                 target_language=payload.target_language, voice=payload.voice,
                 minutes_charged=minutes)
    db.add(job)
    db.commit()
    db.refresh(user)
    db.refresh(job)
    return _response(job)


@router.get("/jobs", response_model=list[DubJobResponse])
def list_jobs(db: Session = Depends(db_session), user: User = Depends(current_user)):
    jobs = db.query(DubJob).filter(DubJob.user_id == user.id)\
        .order_by(DubJob.created_at.desc()).limit(100).all()
    return [_response(j) for j in jobs]


@router.get("/jobs/{job_id}", response_model=DubJobResponse)
def get_job(job_id: int, db: Session = Depends(db_session), user: User = Depends(current_user)):
    job = db.query(DubJob).filter(DubJob.id == job_id, DubJob.user_id == user.id).first()
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    return _response(job)


@router.post("/jobs/{job_id}/cancel", response_model=DubJobResponse)
def cancel_job(job_id: int, db: Session = Depends(db_session), user: User = Depends(current_user)):
    job = db.query(DubJob).filter(DubJob.id == job_id, DubJob.user_id == user.id).first()
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    if job.status in TERMINAL_STATUSES:
        raise HTTPException(status.HTTP_409_CONFLICT, "Job already finished")
    # Cooperative: the worker checks between stages; a queued job stops here.
    job.status = "cancelled"
    job.stage = "cancelled"
    db.commit()
    db.refresh(job)
    return _response(job)


@router.get("/jobs/{job_id}/download")
def download(job_id: int, db: Session = Depends(db_session), user: User = Depends(current_user)):
    job = db.query(DubJob).filter(DubJob.id == job_id, DubJob.user_id == user.id).first()
    if job is None or job.status != "completed" or not job.output_filename:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Dubbed video not ready")
    path = (config.OUTPUTS_DIR / job.output_filename).resolve()
    if config.OUTPUTS_DIR.resolve() not in path.parents or not path.is_file():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "File not found")
    return FileResponse(path, media_type="video/mp4",
                        filename=f"unofun-dubbed-{job.id}.mp4")
