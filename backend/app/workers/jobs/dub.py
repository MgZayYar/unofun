"""Full dubbing pipeline for one job.

Stages: transcribe -> translate -> synthesize -> mix -> done.
Progress and stage are recorded on the DubJob row so the frontend can
show a live, stage-aware progress bar.
"""

from __future__ import annotations

import asyncio
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.ai.dubbing.audio import assign_speakers, build_dubbed_video, synthesize_segments
from app.ai.dubbing.providers import get_provider
from app.ai.dubbing.voices import resolve_speaker_voices
from app.core import config
from app.db.session import SessionLocal
from app.models import DubJob, Video
from app.services.languages import BY_CODE, resolve_voice
from app.services.transcribe import transcribe
from app.services.translate import translate_segments


class JobCancelled(Exception):
    """The user cancelled the job; stop at the next stage boundary."""


def _set_stage(job_id: int, stage: str, progress: int) -> None:
    with SessionLocal() as db:
        job = db.get(DubJob, job_id)
        if job is None or job.status != "processing":
            raise JobCancelled(f"dub job {job_id} is no longer processing")
        job.stage = stage
        job.progress = max(0, min(100, progress))
        db.commit()


async def run(job_id: int) -> None:
    with SessionLocal() as db:
        job = db.get(DubJob, job_id)
        video = db.get(Video, job.video_id) if job else None
        if job is None or video is None:
            raise RuntimeError("Dub job or video not found")
        target_language = job.target_language
        requested_voice = job.voice
        video_path = config.UPLOADS_DIR / video.stored_filename

    if target_language not in BY_CODE:
        raise RuntimeError(f"Unsupported language: {target_language}")
    if not video_path.is_file():
        raise RuntimeError("Video file not found")

    _set_stage(job_id, "transcribing", 5)
    segments, detected = await asyncio.to_thread(transcribe, video_path)
    if not segments:
        raise RuntimeError("No speech detected in the video")

    _set_stage(job_id, "translating", 20)
    translated = await asyncio.to_thread(translate_segments, segments, target_language)

    _set_stage(job_id, "synthesizing", 30)
    provider = get_provider(config.TTS_PROVIDER if config.TTS_PROVIDER != "edge" else "edge")
    assigned = assign_speakers(translated)
    voice_id = resolve_voice(target_language, requested_voice)
    voices = await resolve_speaker_voices(provider.name, target_language, voice_id=voice_id)

    loop = asyncio.get_running_loop()
    filename = f"{uuid4().hex}_dubbed.mp4"
    output_path = config.OUTPUTS_DIR / filename
    with tempfile.TemporaryDirectory(prefix="unofun-dub-") as tmp:
        def _on_synth(done: int, total: int) -> None:
            pct = 30 + int(40 * done / max(total, 1))
            loop.call_soon_threadsafe(_set_stage, job_id, "synthesizing", pct)

        dubbed = await synthesize_segments(provider, assigned, voices, Path(tmp), _on_synth)
        _set_stage(job_id, "mixing", 75)
        await asyncio.to_thread(build_dubbed_video, video_path, dubbed, output_path)

    _set_stage(job_id, "finalizing", 95)
    with SessionLocal() as db:
        job = db.get(DubJob, job_id)
        if job is None:
            raise RuntimeError("Dub job disappeared")
        job.output_filename = filename
        job.stage = "done"
        job.progress = 100
        job.status = "completed"
        job.finished_at = datetime.now(timezone.utc)
        db.commit()
