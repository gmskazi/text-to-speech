from __future__ import annotations

import shutil
import tempfile

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from starlette.background import BackgroundTask

from app.api import router
from app.config import VOICE_OPTIONS
from app.services.tts_service import (
    synthesize_dialogue_to_file,
    synthesize_single_to_file,
)
from app.utils import ensure_mp3_name, to_rate_str

app = FastAPI(
    title="Japanese Text to Audio Generator",
    version="1.0.0",
    description="FastAPI-based text-to-speech app for single and multi-speaker audio.",
)
app.include_router(router)

templates = Jinja2Templates(directory="app/templates")


def _form_value_to_str(value: object, default: str = "") -> str:
    if isinstance(value, str):
        return value
    return default


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"voices": VOICE_OPTIONS, "error": None},
    )


@app.post("/generate", response_class=HTMLResponse, response_model=None)
async def generate_audio(request: Request) -> Response:
    form = await request.form()
    speaker_count = int(_form_value_to_str(form.get("speaker_count", "1"), "1"))
    output_name = ensure_mp3_name(
        _form_value_to_str(
            form.get("output_name", "japanese_audio.mp3"),
            "japanese_audio.mp3",
        )
    )

    try:
        if speaker_count == 1:
            text = _form_value_to_str(form.get("single_text", ""), "").strip()
            if not text:
                raise ValueError("Please enter some text for single-speaker mode.")

            voice = _form_value_to_str(
                form.get("single_voice", "ja-JP-NanamiNeural"),
                "ja-JP-NanamiNeural",
            )
            rate_value = _form_value_to_str(form.get("single_rate", "-20"), "-20")
            rate = to_rate_str(rate_value)

            temp_dir = tempfile.mkdtemp(prefix="tts_single_form_")
            output_path = f"{temp_dir}/{output_name}"
            await synthesize_single_to_file(
                text=text,
                voice=voice,
                rate=rate,
                output_file=output_path,
            )
            return FileResponse(
                output_path,
                media_type="audio/mpeg",
                filename=output_name,
                background=BackgroundTask(shutil.rmtree, temp_dir, ignore_errors=True),
            )

        speaker_settings = {}
        for speaker in ["A", "B", "C", "D"]:
            speaker_settings[speaker] = {
                "voice": _form_value_to_str(
                    form.get(f"voice_{speaker}", "ja-JP-NanamiNeural"),
                    "ja-JP-NanamiNeural",
                ),
                "rate": to_rate_str(
                    _form_value_to_str(form.get(f"rate_{speaker}", "-20"), "-20")
                ),
            }

        dialogue_text = _form_value_to_str(form.get("dialogue_text", ""), "")
        temp_dir = tempfile.mkdtemp(prefix="tts_multi_form_")
        output_path = f"{temp_dir}/{output_name}"
        await synthesize_dialogue_to_file(
            dialogue_text=dialogue_text,
            speaker_count=speaker_count,
            speaker_settings=speaker_settings,
            temp_dir=temp_dir,
            output_file=output_path,
        )
        return FileResponse(
            output_path,
            media_type="audio/mpeg",
            filename=output_name,
            background=BackgroundTask(shutil.rmtree, temp_dir, ignore_errors=True),
        )

    except Exception as error:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"voices": VOICE_OPTIONS, "error": str(error)},
            status_code=400,
        )
