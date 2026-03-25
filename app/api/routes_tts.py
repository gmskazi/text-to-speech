from __future__ import annotations

import asyncio
import shutil
import tempfile

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from app.config import LANGUAGE_LABELS, language_or_default, voices_for_language
from app.models import (
    DialogueRequest,
    JobCreateResponse,
    JobStatusResponse,
    SingleSpeakerRequest,
)
from app.services.job_store import job_store
from app.services.tts_service import (
    synthesize_dialogue_to_file,
    synthesize_single_to_file,
)
from app.utils import ensure_mp3_name, to_rate_str

router = APIRouter()


def _speaker_map_for_dialogue(payload: DialogueRequest) -> dict[str, dict[str, str]]:
    allowed_speakers = [chr(ord("A") + i) for i in range(payload.speaker_count)]
    return {
        speaker: {
            "voice": payload.speakers[speaker].voice,
            "rate": to_rate_str(payload.speakers[speaker].rate),
        }
        for speaker in allowed_speakers
    }


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/tts/voices")
async def list_tts_voices(
    language: str = Query(default="ja-JP"),
) -> dict[str, object]:
    resolved = language_or_default(language)
    options = voices_for_language(resolved)
    return {
        "language": resolved,
        "language_label": LANGUAGE_LABELS.get(resolved, "Japanese"),
        "voices": [
            {"label": label, "value": value}
            for label, value in options.items()
        ],
    }


@router.post("/tts/single")
async def tts_single(payload: SingleSpeakerRequest) -> FileResponse:
    output_name = ensure_mp3_name(payload.output_name)
    temp_dir = tempfile.mkdtemp(prefix="tts_single_")
    output_path = f"{temp_dir}/{output_name}"

    try:
        await synthesize_single_to_file(
            text=payload.text,
            voice=payload.voice,
            rate=to_rate_str(payload.rate),
            output_file=output_path,
        )
    except ValueError as error:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail=str(error)) from error
    except RuntimeError as error:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(error)) from error
    except Exception as error:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail="TTS generation failed.") from error

    return FileResponse(
        output_path,
        media_type="audio/mpeg",
        filename=output_name,
        background=BackgroundTask(shutil.rmtree, temp_dir, ignore_errors=True),
    )


@router.post("/tts/dialogue")
async def tts_dialogue(payload: DialogueRequest) -> FileResponse:
    output_name = ensure_mp3_name(payload.output_name)
    temp_dir = tempfile.mkdtemp(prefix="tts_multi_")
    output_path = f"{temp_dir}/{output_name}"

    try:
        await synthesize_dialogue_to_file(
            dialogue_text=payload.dialogue_text,
            speaker_count=payload.speaker_count,
            speaker_settings=_speaker_map_for_dialogue(payload),
            temp_dir=temp_dir,
            output_file=output_path,
        )
    except ValueError as error:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail=str(error)) from error
    except RuntimeError as error:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(error)) from error
    except Exception as error:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(
            status_code=500,
            detail="Dialogue generation failed.",
        ) from error

    return FileResponse(
        output_path,
        media_type="audio/mpeg",
        filename=output_name,
        background=BackgroundTask(shutil.rmtree, temp_dir, ignore_errors=True),
    )


def _run_single_job(job_id: str, payload: SingleSpeakerRequest) -> None:
    record = job_store.update(job_id, status="running")
    temp_dir = tempfile.mkdtemp(prefix="tts_job_single_")
    output_path = f"{temp_dir}/{record.output_name}"
    try:
        asyncio.run(
            synthesize_single_to_file(
                text=payload.text,
                voice=payload.voice,
                rate=to_rate_str(payload.rate),
                output_file=output_path,
            )
        )
        job_store.update(
            job_id,
            status="done",
            file_path=output_path,
            temp_dir=temp_dir,
        )
    except Exception as error:
        shutil.rmtree(temp_dir, ignore_errors=True)
        job_store.update(job_id, status="failed", error=str(error))


def _run_dialogue_job(job_id: str, payload: DialogueRequest) -> None:
    record = job_store.update(job_id, status="running")
    temp_dir = tempfile.mkdtemp(prefix="tts_job_dialogue_")
    output_path = f"{temp_dir}/{record.output_name}"
    try:
        asyncio.run(
            synthesize_dialogue_to_file(
                dialogue_text=payload.dialogue_text,
                speaker_count=payload.speaker_count,
                speaker_settings=_speaker_map_for_dialogue(payload),
                temp_dir=temp_dir,
                output_file=output_path,
            )
        )
        job_store.update(
            job_id,
            status="done",
            file_path=output_path,
            temp_dir=temp_dir,
        )
    except Exception as error:
        shutil.rmtree(temp_dir, ignore_errors=True)
        job_store.update(job_id, status="failed", error=str(error))


@router.post("/tts/single/jobs", response_model=JobCreateResponse, status_code=202)
async def create_single_job(
    payload: SingleSpeakerRequest,
    background_tasks: BackgroundTasks,
) -> JobCreateResponse:
    output_name = ensure_mp3_name(payload.output_name)
    record = job_store.create_job(output_name)
    background_tasks.add_task(_run_single_job, record.job_id, payload)
    return JobCreateResponse(job_id=record.job_id, status="queued")


@router.post("/tts/dialogue/jobs", response_model=JobCreateResponse, status_code=202)
async def create_dialogue_job(
    payload: DialogueRequest,
    background_tasks: BackgroundTasks,
) -> JobCreateResponse:
    output_name = ensure_mp3_name(payload.output_name)
    record = job_store.create_job(output_name)
    background_tasks.add_task(_run_dialogue_job, record.job_id, payload)
    return JobCreateResponse(job_id=record.job_id, status="queued")


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str) -> JobStatusResponse:
    record = job_store.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return JobStatusResponse(
        job_id=record.job_id,
        status=record.status,
        output_name=record.output_name,
        error=record.error,
    )


def _cleanup_downloaded_job(job_id: str) -> None:
    record = job_store.get(job_id)
    if record is None:
        return
    if record.temp_dir:
        shutil.rmtree(record.temp_dir, ignore_errors=True)
    job_store.update(job_id, status="downloaded")


@router.get("/jobs/{job_id}/download")
async def download_job_result(job_id: str) -> FileResponse:
    record = job_store.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    if record.status != "done" or not record.file_path:
        raise HTTPException(status_code=409, detail="Job result is not ready.")

    background_tasks = BackgroundTasks()
    background_tasks.add_task(_cleanup_downloaded_job, job_id)
    return FileResponse(
        record.file_path,
        media_type="audio/mpeg",
        filename=record.output_name,
        background=background_tasks,
    )
