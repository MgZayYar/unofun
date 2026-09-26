# unofun 🎙️

**Any video. Any language.** Paste a video URL or upload a file — get a natural
AI voice-over in 21 languages with perfectly timed audio, in minutes.

- 🎬 **URL ingest or upload** — paste any direct video link or upload a file
- 🗣️ **Real dubbing pipeline** — faster-whisper transcription → LLM translation → Edge TTS / OpenAI TTS → mixed over ducked original audio
- 🌏 **21 languages** — deep Southeast Asia coverage: Myanmar, Thai, Indonesian, Vietnamese, Malay, Filipino, Khmer, Lao + 13 more
- 🎭 **Two-speaker voices** — speaker turns detected from pauses, contrasting voices
- 💳 **Credits** — 30 free minutes on signup, 1 credit per minute dubbed
- 📊 **Live progress** — stage-aware progress (transcribing → translating → synthesizing → mixing)
- 🐳 **Docker Compose** — api + worker + web

## Quick start (Windows — easiest)

1. Install [Python 3.12](https://www.python.org/downloads/) (tick **"Add python.exe to PATH"**),
   [Node.js 20 LTS](https://nodejs.org/), and
   [ffmpeg](https://www.gyan.dev/ffmpeg/builds/) (extract, add its `bin` folder to PATH).
2. In `C:\`, run: `git clone https://github.com/MgZayYar/unofun.git`
3. Open the `unofun` folder in VS Code, right-click **`setup.ps1`** → **Run with PowerShell**.
   It checks the prerequisites, installs everything, and builds the database automatically.
4. Edit `.env` — set `JWT_SECRET_KEY` (any long random string) and `OPENAI_API_KEY`.
5. Right-click **`start.ps1`** → **Run with PowerShell**. Open http://localhost:3000.

> If PowerShell blocks the script, run once:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

## Quick start (manual)

**Backend**

```powershell
cd backend
python -m venv .venv; .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
copy ..\..\.env.example .env   # then set JWT_SECRET_KEY and OPENAI_API_KEY
python -m alembic upgrade head
uvicorn app.main:app --reload        # terminal 1
python -m app.workers.runner         # terminal 2
```

**Frontend**

```powershell
cd frontend
npm install
npm run dev   # http://localhost:3000 (proxies /api to the backend)
```

**Docker**

```powershell
copy .env.example .env   # fill in secrets
docker compose up --build
```

## How dubbing works

1. Video is ingested (uploaded or downloaded from URL)
2. `transcribe` — faster-whisper extracts timestamped segments
3. `translate` — segments translated to the target language (OpenAI)
4. `synthesize` — each segment voiced with Edge TTS (free) or OpenAI TTS
5. `mix` — dubs placed at original timestamps over the original audio ducked to 15%

Credits are deducted up-front (rounded up per minute). Cancel a running job any
time from the dashboard; queued jobs stop immediately, processing jobs stop at
the next stage boundary.

## API

Interactive docs at `http://localhost:8000/docs`. Key endpoints:

- `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`
- `POST /api/videos/upload`, `POST /api/videos/from-url`
- `GET /api/dub/languages`, `GET /api/dub/voices`, `POST /api/dub/preview`
- `POST /api/dub/start`, `GET /api/dub/jobs`, `GET /api/dub/jobs/{id}`,
  `POST /api/dub/jobs/{id}/cancel`, `GET /api/dub/jobs/{id}/download`

## License

MIT
