import os

os.environ.pop("ANTHROPIC_API_KEY", None)

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/api/health").json()["status"] == "ok"


def test_storyboard_mock():
    r = client.post("/api/storyboard", json={"idea": "A man discovers an AI living in his smart home", "length_seconds": 30})
    assert r.status_code == 200
    body = r.json()
    assert body["source"] == "mock" and len(body["scenes"]) >= 3
    assert body["total_seconds"] == sum(s["duration_seconds"] for s in body["scenes"])


def test_validation():
    assert client.post("/api/storyboard", json={"idea": "short"}).status_code == 422


def test_regenerate_mock():
    sb = client.post("/api/storyboard", json={"idea": "A funny grandfather superhero story"}).json()
    r = client.post(
        "/api/scene/regenerate",
        json={"request": {"idea": "A funny grandfather superhero story"}, "scene": sb["scenes"][0]},
    )
    assert r.status_code == 200
