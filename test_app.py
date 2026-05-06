"""Tests for the sample CI/CD app — run by CodeBuild during the build phase."""
from app import app


def test_home():
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json["status"] == "running"


def test_health():
    client = app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json["status"] == "healthy"
