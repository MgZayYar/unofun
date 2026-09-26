"""Speech-to-text with faster-whisper."""

from __future__ import annotations

from pathlib import Path

from app.core import config

_model = None


def _load():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel

        _model = WhisperModel(
            config.WHISPER_MODEL,
            device=config.WHISPER_DEVICE,
            compute_type=config.WHISPER_COMPUTE_TYPE,
        )
    return _model


def transcribe(video_path: Path) -> tuple[list[dict], str]:
    """Return (segments, detected_language) for the video's audio track."""
    model = _load()
    segments_iter, info = model.transcribe(str(video_path), beam_size=5)
    segments = [
        {"start": float(s.start), "end": float(s.end), "text": s.text.strip()}
        for s in segments_iter
        if s.text.strip()
    ]
    return segments, info.language or "en"
