FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /srv/app
COPY backend/pyproject.toml ./
RUN pip install --no-cache-dir -e .
COPY backend/ ./

ENV DATABASE_URL=sqlite:////srv/data/app.db
ENV UPLOADS_DIR=/srv/data/uploads
ENV OUTPUTS_DIR=/srv/data/outputs

EXPOSE 8000
CMD ["sh", "-c", "python -m alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
