"""Auth, videos, dub lifecycle, credits."""

import io


def test_register_grants_free_trial_credits(client):
    resp = client.post("/api/auth/register",
                       json={"email": "new@example.com", "password": "secret123"})
    assert resp.status_code == 201
    assert resp.json()["user"]["credits_minutes"] == 30


def test_register_duplicate_email_rejected(client, user_token):
    resp = client.post("/api/auth/register",
                       json={"email": "tester@example.com", "password": "secret123"})
    assert resp.status_code == 400


def test_login_and_me(client, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "tester@example.com"


def test_unauthenticated_rejected(client):
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/dub/jobs").status_code == 401


def _upload(client, auth_headers, name="clip.mp4"):
    data = b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 2048
    resp = client.post("/api/videos/upload", headers=auth_headers,
                       files={"file": (name, io.BytesIO(data), "video/mp4")})
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_upload_and_list_videos(client, auth_headers):
    video = _upload(client, auth_headers)
    assert video["title"] == "clip.mp4"
    listed = client.get("/api/videos", headers=auth_headers).json()
    assert len(listed) == 1


def test_upload_rejects_bad_extension(client, auth_headers):
    resp = client.post("/api/videos/upload", headers=auth_headers,
                       files={"file": ("evil.exe", io.BytesIO(b"x"), "application/octet-stream")})
    assert resp.status_code == 400


def test_start_dub_deducts_credits(client, auth_headers):
    video = _upload(client, auth_headers)
    resp = client.post("/api/dub/start", headers=auth_headers,
                       json={"video_id": video["id"], "target_language": "my"})
    assert resp.status_code == 201, resp.text
    job = resp.json()
    assert job["status"] == "queued"
    assert job["minutes_charged"] >= 1
    me = client.get("/api/auth/me", headers=auth_headers).json()
    assert me["credits_minutes"] == 30 - job["minutes_charged"]


def test_start_dub_rejects_unknown_language(client, auth_headers):
    video = _upload(client, auth_headers)
    resp = client.post("/api/dub/start", headers=auth_headers,
                       json={"video_id": video["id"], "target_language": "xx"})
    assert resp.status_code == 400


def test_start_dub_rejects_foreign_video(client, auth_headers):
    # video id 999 belongs to nobody
    resp = client.post("/api/dub/start", headers=auth_headers,
                       json={"video_id": 999, "target_language": "my"})
    assert resp.status_code == 404


def test_start_dub_insufficient_credits(client, auth_headers):
    from app.db.session import SessionLocal
    from app.models import User

    with SessionLocal() as db:
        user = db.query(User).filter(User.email == "tester@example.com").first()
        user.credits_minutes = 0
        db.commit()
    video = _upload(client, auth_headers)
    resp = client.post("/api/dub/start", headers=auth_headers,
                       json={"video_id": video["id"], "target_language": "my"})
    assert resp.status_code == 402


def test_job_status_and_cancel(client, auth_headers):
    video = _upload(client, auth_headers)
    job = client.post("/api/dub/start", headers=auth_headers,
                      json={"video_id": video["id"], "target_language": "my"}).json()
    got = client.get(f"/api/dub/jobs/{job['id']}", headers=auth_headers).json()
    assert got["id"] == job["id"]
    cancelled = client.post(f"/api/dub/jobs/{job['id']}/cancel", headers=auth_headers)
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"
    again = client.post(f"/api/dub/jobs/{job['id']}/cancel", headers=auth_headers)
    assert again.status_code == 409


def test_download_before_completion_404(client, auth_headers):
    video = _upload(client, auth_headers)
    job = client.post("/api/dub/start", headers=auth_headers,
                      json={"video_id": video["id"], "target_language": "my"}).json()
    resp = client.get(f"/api/dub/jobs/{job['id']}/download", headers=auth_headers)
    assert resp.status_code == 404


def test_languages_endpoint(client):
    langs = client.get("/api/dub/languages").json()
    codes = [entry["code"] for entry in langs]
    assert "my" in codes and "th" in codes and "en" in codes
    assert len(langs) >= 20


def test_openapi_builds(client):
    spec = client.get("/openapi.json").json()
    assert "/api/dub/start" in spec["paths"]
    assert "/api/auth/register" in spec["paths"]
