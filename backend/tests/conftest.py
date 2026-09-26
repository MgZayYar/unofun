"""Test fixtures: isolated app + database."""

import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

_tmp = tempfile.mkdtemp(prefix="unofun-test-")
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"
os.environ["JWT_SECRET_KEY"] = "test-secret"
os.environ["UPLOADS_DIR"] = f"{_tmp}/uploads"
os.environ["OUTPUTS_DIR"] = f"{_tmp}/outputs"
os.environ["OPENAI_API_KEY"] = ""

import app.db.session as session_module  # noqa: E402
import app.models  # noqa: E402 - register models on Base.metadata
from app.core import config  # noqa: E402
from app.db.session import Base  # noqa: E402

config.UPLOADS_DIR = Path(os.environ["UPLOADS_DIR"])
config.OUTPUTS_DIR = Path(os.environ["OUTPUTS_DIR"])
config.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
config.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

_test_engine = create_engine(os.environ["DATABASE_URL"], connect_args={"check_same_thread": False})
TestingSession = sessionmaker(bind=_test_engine, autoflush=False, expire_on_commit=False)
session_module.engine = _test_engine
session_module.SessionLocal = TestingSession


@pytest.fixture(autouse=True)
def _fresh_db():
    Base.metadata.drop_all(_test_engine)
    Base.metadata.create_all(_test_engine)
    yield
    Base.metadata.drop_all(_test_engine)


@pytest.fixture()
def client():
    import app.main as main_module

    with TestClient(main_module.app) as c:
        yield c


@pytest.fixture()
def user_token(client):
    resp = client.post("/api/auth/register",
                       json={"email": "tester@example.com", "password": "secret123"})
    assert resp.status_code == 201, resp.text
    return resp.json()["access_token"]


@pytest.fixture()
def auth_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}
