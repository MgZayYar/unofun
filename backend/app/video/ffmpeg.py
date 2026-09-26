"""ffmpeg subprocess helper."""

from __future__ import annotations

import subprocess

from app.core import config


class FFmpegError(RuntimeError):
    pass


def run_ffmpeg(*args: str, timeout: float = 600) -> None:
    cmd = [config.FFMPEG_BINARY, *args]
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=True)
    except subprocess.TimeoutExpired as exc:
        raise FFmpegError(f"ffmpeg timed out after {timeout}s") from exc
    except subprocess.CalledProcessError as exc:
        tail = (exc.stderr or "")[-2000:]
        raise FFmpegError(f"ffmpeg failed: {tail}") from exc
