"""Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(RegisterRequest):
    pass


class UserResponse(BaseModel):
    id: int
    email: str
    credits_minutes: int
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class VideoResponse(BaseModel):
    id: int
    title: str
    source_url: str | None
    duration_seconds: float | None
    created_at: datetime


class VideoFromUrlRequest(BaseModel):
    url: str = Field(min_length=8, max_length=2048)
    title: str | None = Field(default=None, max_length=500)


class DubStartRequest(BaseModel):
    video_id: int
    target_language: str = Field(min_length=2, max_length=16)
    voice: str | None = Field(default=None, max_length=120)


class DubJobResponse(BaseModel):
    id: int
    video_id: int
    target_language: str
    voice: str | None
    status: str
    stage: str
    progress: int
    error_message: str | None
    minutes_charged: int
    created_at: datetime
    finished_at: datetime | None


class LanguageInfo(BaseModel):
    code: str
    name: str
    voices: list[str]


class VoicePreviewRequest(BaseModel):
    voice: str = Field(min_length=1, max_length=120)
    text: str | None = Field(default=None, max_length=280)
