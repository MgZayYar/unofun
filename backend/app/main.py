"""unofun API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, dub, health, videos

app = FastAPI(
    title="unofun API",
    description="AI video dubbing in 20+ languages.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(videos.router)
app.include_router(dub.router)


@app.get("/")
def root():
    return {"name": "unofun", "docs": "/docs"}
