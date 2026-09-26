"""Video ingest: uploads and URL downloads."""

import shutil
import subprocess
import uuid
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import current_user, db_session
from app.core import config
from app.models import User, Video
from app.schemas import VideoFromUrlRequest, VideoResponse

router = APIRouter(prefix="/api/videos", tags=["videos"])

ALLOWED_EXTENSIONS = {".mp4", ".mov", ".webm", ".mkv", ".m4v"}
ALLOWED_CONTENT_TYPES = {"video/mp4", "video/quicktime", "video/webm", "video/x-matroska"}


def _probe_duration(path: Path) -> float | None:
    try:
        result = subprocess.run(
            [config.FFMPEG_BINARY.replace("ffmpeg", "ffprobe"), "-v", "error",
             "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
            capture_output=True, text=True, timeout=30,
        )
        return float(result.stdout.strip())
    except Exception:
        return None


def _response(video: Video) -> VideoResponse:
    return VideoResponse(
        id=video.id,
        title=video.title,
        source_url=video.source_url,
        duration_seconds=video.duration_seconds,
        created_at=video.created_at,
    )


@router.post("/upload", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
async def upload_video(file: UploadFile, db: Session = Depends(db_session),
                       user: User = Depends(current_user)):
    original = Path(file.filename or "upload").name
    ext = Path(original).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}")
    stored = f"{uuid.uuid4().hex}{ext}"
    dest = config.UPLOADS_DIR / stored
    size = 0
    with dest.open("wb") as out:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > config.MAX_UPLOAD_BYTES:
                dest.unlink(missing_ok=True)
                raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "File too large")
            out.write(chunk)
    video = Video(user_id=user.id, title=original, stored_filename=stored,
                  duration_seconds=_probe_duration(dest))
    db.add(video)
    db.commit()
    db.refresh(video)
    return _response(video)


@router.post("/from-url", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
async def video_from_url(payload: VideoFromUrlRequest, db: Session = Depends(db_session),
                         user: User = Depends(current_user)):
    url = payload.url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "URL must start with http:// or https://")
    stored = f"{uuid.uuid4().hex}.mp4"
    dest = config.UPLOADS_DIR / stored
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=60) as client:
            async with client.stream("GET", url) as resp:
                if resp.status_code >= 400:
                    raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                        f"Could not fetch URL (HTTP {resp.status_code})")
                ctype = resp.headers.get("content-type", "").split(";")[0].strip()
                if ctype and not (ctype.startswith("video/") or ctype == "application/octet-stream"):
                    raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                        f"URL does not point to a video (content-type: {ctype})")
                size = 0
                with dest.open("wb") as out:
                    async for chunk in resp.aiter_bytes(1024 * 64):
                        size += len(chunk)
                        if size > config.MAX_URL_DOWNLOAD_BYTES:
                            dest.unlink(missing_ok=True)
                            raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                                                "Remote file too large")
                        out.write(chunk)
    except HTTPException:
        raise
    except Exception as exc:
        dest.unlink(missing_ok=True)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Download failed: {exc}") from exc
    video = Video(user_id=user.id, title=payload.title or url, stored_filename=stored,
                  source_url=url, duration_seconds=_probe_duration(dest))
    db.add(video)
    db.commit()
    db.refresh(video)
    return _response(video)


@router.get("", response_model=list[VideoResponse])
def list_videos(db: Session = Depends(db_session), user: User = Depends(current_user)):
    videos = db.query(Video).filter(Video.user_id == user.id).order_by(Video.created_at.desc()).all()
    return [_response(v) for v in videos]


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_video(video_id: int, db: Session = Depends(db_session), user: User = Depends(current_user)):
    video = db.query(Video).filter(Video.id == video_id, Video.user_id == user.id).first()
    if video is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Video not found")
    (config.UPLOADS_DIR / video.stored_filename).unlink(missing_ok=True)
    db.delete(video)
    db.commit()
