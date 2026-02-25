"""API endpoint tests."""

import os


def test_health_check(client):
    """Health endpoint should return ok."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["mock_mode"] is True


def test_upload_session(client, sample_wav):
    """Upload a WAV file and get a transcribed session back."""
    with open(sample_wav, "rb") as f:
        resp = client.post(
            "/api/sessions",
            files={"file": ("test.wav", f, "audio/wav")},
        )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "completed"
    assert data["transcript"]  # Should have mock transcript
    assert data["summary"]
    assert isinstance(data["key_points"], list)
    assert isinstance(data["action_items"], list)
    assert data["id"]


def test_upload_invalid_format(client):
    """Uploading a non-audio file should fail."""
    resp = client.post(
        "/api/sessions",
        files={"file": ("test.txt", b"not audio", "text/plain")},
    )
    assert resp.status_code == 400
    assert "Unsupported" in resp.json()["detail"]


def test_list_sessions_empty(client):
    """List sessions when none exist."""
    resp = client.get("/api/sessions")
    assert resp.status_code == 200
    data = resp.json()
    assert data["sessions"] == []
    assert data["total"] == 0


def test_list_sessions_with_data(client, sample_wav):
    """List sessions after uploading."""
    # Create a session first
    with open(sample_wav, "rb") as f:
        client.post("/api/sessions", files={"file": ("test.wav", f, "audio/wav")})

    resp = client.get("/api/sessions")
    data = resp.json()
    assert data["total"] == 1
    assert len(data["sessions"]) == 1


def test_get_session_detail(client, sample_wav):
    """Get a specific session by ID."""
    with open(sample_wav, "rb") as f:
        create_resp = client.post(
            "/api/sessions", files={"file": ("test.wav", f, "audio/wav")}
        )
    session_id = create_resp.json()["id"]

    resp = client.get(f"/api/sessions/{session_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == session_id
    assert data["transcript"]


def test_get_session_not_found(client):
    """Get a non-existent session."""
    resp = client.get("/api/sessions/nonexistent-id")
    assert resp.status_code == 404


def test_delete_session(client, sample_wav):
    """Delete a session."""
    with open(sample_wav, "rb") as f:
        create_resp = client.post(
            "/api/sessions", files={"file": ("test.wav", f, "audio/wav")}
        )
    session_id = create_resp.json()["id"]

    resp = client.delete(f"/api/sessions/{session_id}")
    assert resp.status_code == 204

    # Verify it's gone
    resp = client.get(f"/api/sessions/{session_id}")
    assert resp.status_code == 404


def test_search_sessions(client, sample_wav):
    """Search sessions by text."""
    with open(sample_wav, "rb") as f:
        client.post("/api/sessions", files={"file": ("test.wav", f, "audio/wav")})

    # Search for text from mock transcript
    resp = client.get("/api/sessions", params={"search": "VoiceAid"})
    data = resp.json()
    assert data["total"] >= 1

    # Search for non-existent text
    resp = client.get("/api/sessions", params={"search": "xyznonexistent"})
    data = resp.json()
    assert data["total"] == 0


def test_resummarize_session(client, sample_wav):
    """Re-summarize with different sentence count."""
    with open(sample_wav, "rb") as f:
        create_resp = client.post(
            "/api/sessions", files={"file": ("test.wav", f, "audio/wav")}
        )
    session_id = create_resp.json()["id"]

    resp = client.post(
        f"/api/sessions/{session_id}/resummarize",
        json={"sentence_count": 3},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["summary"]
