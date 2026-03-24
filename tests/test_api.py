from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_single_tts_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_single(
        *,
        text: str,
        voice: str,
        rate: str,
        output_file: str,
    ) -> None:
        del text, voice, rate
        Path(output_file).write_bytes(b"fake-single")

    monkeypatch.setattr(
        "app.api.routes_tts.synthesize_single_to_file",
        fake_single,
    )

    payload = {
        "text": "こんにちは",
        "voice": "ja-JP-NanamiNeural",
        "rate": -20,
        "output_name": "sample.mp3",
    }
    response = client.post("/tts/single", json=payload)

    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"
    assert response.content == b"fake-single"


def test_dialogue_tts_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_dialogue(
        *,
        dialogue_text: str,
        speaker_count: int,
        speaker_settings: dict[str, dict[str, str]],
        temp_dir: str,
        output_file: str,
    ) -> None:
        Path(output_file).write_bytes(b"fake-dialogue")

    monkeypatch.setattr(
        "app.api.routes_tts.synthesize_dialogue_to_file",
        fake_dialogue,
    )

    payload = {
        "speaker_count": 2,
        "dialogue_text": "A: こんにちは\nB: はい",
        "speakers": {
            "A": {"voice": "ja-JP-NanamiNeural", "rate": -20},
            "B": {"voice": "ja-JP-KeitaNeural", "rate": -20},
        },
        "output_name": "dialogue.mp3",
    }
    response = client.post("/tts/dialogue", json=payload)

    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"
    assert response.content == b"fake-dialogue"


def test_dialogue_validation_error(monkeypatch: pytest.MonkeyPatch) -> None:
    async def failing_dialogue(
        *,
        dialogue_text: str,
        speaker_count: int,
        speaker_settings: dict[str, dict[str, str]],
        temp_dir: str,
        output_file: str,
    ) -> None:
        raise ValueError("Invalid speaker 'C'. Allowed speakers: A, B")

    monkeypatch.setattr(
        "app.api.routes_tts.synthesize_dialogue_to_file",
        failing_dialogue,
    )

    payload = {
        "speaker_count": 2,
        "dialogue_text": "C: こんにちは",
        "speakers": {
            "A": {"voice": "ja-JP-NanamiNeural", "rate": -20},
            "B": {"voice": "ja-JP-KeitaNeural", "rate": -20},
        },
        "output_name": "dialogue.mp3",
    }
    response = client.post("/tts/dialogue", json=payload)

    assert response.status_code == 400
    assert "Invalid speaker" in response.json()["detail"]


def test_create_job_and_read_status(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run_single_job(job_id: str, payload: Any) -> None:
        del payload
        from app.services.job_store import job_store

        record = job_store.get(job_id)
        assert record is not None
        job_store.update(
            job_id,
            status="done",
            file_path="/tmp/file.mp3",
            temp_dir="/tmp",
        )

    monkeypatch.setattr("app.api.routes_tts._run_single_job", fake_run_single_job)

    payload = {
        "text": "こんにちは",
        "voice": "ja-JP-NanamiNeural",
        "rate": -20,
        "output_name": "job.mp3",
    }
    create_response = client.post("/tts/single/jobs", json=payload)
    assert create_response.status_code == 202

    job_id = create_response.json()["job_id"]
    status_response = client.get(f"/jobs/{job_id}")
    assert status_response.status_code == 200
    assert status_response.json()["job_id"] == job_id
