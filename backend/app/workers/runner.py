"""Standalone worker: ``python -m app.workers.runner``.

The database is the durable queue. Jobs are claimed with one atomic
``UPDATE ... RETURNING`` statement, so any number of workers can run
against the same database without double-processing.
"""

from __future__ import annotations

import asyncio
import logging
import signal
from datetime import datetime, timezone

from sqlalchemy import select, update

from app.core.config import WORKER_POLL_INTERVAL
from app.db.session import SessionLocal
from app.models import TERMINAL_STATUSES, DubJob
from app.workers.jobs.dub import JobCancelled, run as run_dub

logger = logging.getLogger("unofun.worker")
_shutdown = False


def _handle_signal(*_args) -> None:  # pragma: no cover - process plumbing
    global _shutdown
    _shutdown = True


def claim_next_job() -> int | None:
    oldest = (
        select(DubJob.id)
        .where(DubJob.status == "queued")
        .order_by(DubJob.created_at, DubJob.id)
        .limit(1)
        .scalar_subquery()
    )
    with SessionLocal() as db:
        row = db.execute(
            update(DubJob)
            .where(DubJob.status == "queued", DubJob.id == oldest)
            .values(status="processing", stage="starting", progress=0)
            .returning(DubJob.id)
        ).first()
        db.commit()
    return row[0] if row else None


def recover_interrupted() -> int:
    with SessionLocal() as db:
        result = db.execute(
            update(DubJob)
            .where(DubJob.status == "processing")
            .values(status="queued", stage="queued", progress=0)
        )
        db.commit()
        return result.rowcount


def _fail(job_id: int, message: str) -> None:
    with SessionLocal() as db:
        job = db.get(DubJob, job_id)
        if job is not None and job.status not in TERMINAL_STATUSES:
            job.status = "failed"
            job.stage = "failed"
            job.error_message = message[:2000]
            job.finished_at = datetime.now(timezone.utc)
            db.commit()


async def _run_forever() -> None:
    recovered = recover_interrupted()
    if recovered:
        logger.info("requeued %d interrupted job(s)", recovered)
    while not _shutdown:
        job_id = await asyncio.to_thread(claim_next_job)
        if job_id is None:
            await asyncio.sleep(WORKER_POLL_INTERVAL)
            continue
        logger.info("processing dub job %d", job_id)
        try:
            await run_dub(job_id)
            logger.info("dub job %d completed", job_id)
        except JobCancelled:
            logger.info("dub job %d cancelled", job_id)
        except Exception as exc:  # noqa: BLE001 - a failed job must not kill the worker
            logger.exception("dub job %d failed", job_id)
            await asyncio.to_thread(_fail, job_id, str(exc))


def main() -> None:  # pragma: no cover - process entrypoint
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)
    asyncio.run(_run_forever())


if __name__ == "__main__":
    main()
