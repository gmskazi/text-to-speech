from __future__ import annotations

import shutil
import tempfile
from collections.abc import Mapping

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from starlette.background import BackgroundTask

from app.api import router
from app.config import (
    LANGUAGE_LABELS,
    VOICE_OPTIONS_BY_LANGUAGE,
    first_voice_for_language,
    language_or_default,
    voices_for_language,
)
from app.services.tts_service import (
    synthesize_dialogue_to_file,
    synthesize_single_to_file,
)
from app.utils import (
    ensure_mp3_name,
    normalize_dialogue_text,
    normalize_for_speech,
    to_rate_str,
)

_NATURAL_SINGLE_RATE = "-5"
_NATURAL_DIALOGUE_RATES = {
    "A": "-5",
    "B": "-2",
    "C": "-4",
    "D": "-1",
}
_NO_AUDIO_MESSAGE = (
    "No audio could be generated. Please include speakable text "
    "(letters, words, or numbers), or try a different voice/language."
)


def _is_no_audio_error(error: Exception) -> bool:
    return "no audio was received" in str(error).lower()


app = FastAPI(
    title="Multilingual Text to Audio Generator",
    version="1.0.0",
    description=(
        "FastAPI-based text-to-speech app for multilingual "
        "single and multi-speaker audio."
    ),
)
app.include_router(router)

templates = Jinja2Templates(directory="app/templates")


def _form_value_to_str(value: object, default: str = "") -> str:
    if isinstance(value, str):
        return value
    return default


def _form_checkbox_enabled(form: Mapping[str, object], field_name: str) -> bool:
    value = form.get(field_name)
    if not isinstance(value, str):
        return False
    return value.lower() in {"1", "true", "on", "yes"}


def _form_rate_was_touched(form: Mapping[str, object], field_name: str) -> bool:
    value = form.get(field_name)
    if not isinstance(value, str):
        return False
    return value == "1"


def _natural_rate_value(
    *,
    natural_mode: bool,
    touched: bool,
    value: str,
    fallback: str,
) -> str:
    if not natural_mode or touched or value != "0":
        return value
    return fallback


def _template_context(
    error: str | None = None,
    *,
    single_language: str = "ja-JP",
    dialogue_language: str = "ja-JP",
) -> dict[str, object]:
    single_resolved = language_or_default(single_language)
    dialogue_resolved = language_or_default(dialogue_language)
    return {
        "languages": LANGUAGE_LABELS,
        "single_default_language": single_resolved,
        "dialogue_default_language": dialogue_resolved,
        "voices": voices_for_language(single_resolved),
        "voices_by_language": VOICE_OPTIONS_BY_LANGUAGE,
        "error": error,
    }


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=_template_context(),
    )


@app.post("/generate", response_class=HTMLResponse, response_model=None)
async def generate_audio(request: Request) -> Response:
    form = await request.form()
    speaker_count = int(_form_value_to_str(form.get("speaker_count", "1"), "1"))
    output_name = ensure_mp3_name(
        _form_value_to_str(
            form.get("output_name", "tts_output.mp3"),
            "tts_output.mp3",
        )
    )
    single_language = language_or_default(
        _form_value_to_str(form.get("single_language", "ja-JP"), "ja-JP")
    )
    dialogue_language = language_or_default(
        _form_value_to_str(form.get("dialogue_language", "ja-JP"), "ja-JP")
    )

    try:
        if speaker_count == 1:
            natural_mode = _form_checkbox_enabled(form, "single_natural_mode")
            original_text = _form_value_to_str(form.get("single_text", ""), "").strip()
            if not original_text:
                raise ValueError("Please enter some text for single-speaker mode.")

            text = original_text

            if natural_mode:
                text = normalize_for_speech(text, single_language)

            voice = _form_value_to_str(
                form.get("single_voice", first_voice_for_language(single_language)),
                first_voice_for_language(single_language),
            )
            raw_rate_value = _form_value_to_str(form.get("single_rate", "0"), "0")
            rate_value = _natural_rate_value(
                natural_mode=natural_mode,
                touched=_form_rate_was_touched(form, "single_rate_touched"),
                value=raw_rate_value,
                fallback=_NATURAL_SINGLE_RATE,
            )
            rate = to_rate_str(rate_value)
            original_rate = to_rate_str(raw_rate_value)

            temp_dir = tempfile.mkdtemp(prefix="tts_single_form_")
            output_path = f"{temp_dir}/{output_name}"
            try:
                await synthesize_single_to_file(
                    text=text,
                    voice=voice,
                    rate=rate,
                    output_file=output_path,
                )
            except Exception as error:
                if not (natural_mode and _is_no_audio_error(error)):
                    raise
                try:
                    await synthesize_single_to_file(
                        text=original_text,
                        voice=voice,
                        rate=original_rate,
                        output_file=output_path,
                    )
                except Exception as fallback_error:
                    if _is_no_audio_error(fallback_error):
                        raise ValueError(_NO_AUDIO_MESSAGE) from fallback_error
                    raise
            return FileResponse(
                output_path,
                media_type="audio/mpeg",
                filename=output_name,
                background=BackgroundTask(shutil.rmtree, temp_dir, ignore_errors=True),
            )

        natural_mode = _form_checkbox_enabled(form, "dialogue_natural_mode")
        speaker_settings = {}
        original_speaker_settings = {}
        dialogue_default_voice = first_voice_for_language(dialogue_language)
        for speaker in ["A", "B", "C", "D"]:
            raw_rate_value = _form_value_to_str(form.get(f"rate_{speaker}", "0"), "0")
            rate_value = _natural_rate_value(
                natural_mode=natural_mode,
                touched=_form_rate_was_touched(form, f"rate_touched_{speaker}"),
                value=raw_rate_value,
                fallback=_NATURAL_DIALOGUE_RATES[speaker],
            )
            speaker_settings[speaker] = {
                "voice": _form_value_to_str(
                    form.get(f"voice_{speaker}", dialogue_default_voice),
                    dialogue_default_voice,
                ),
                "rate": to_rate_str(rate_value),
            }
            original_speaker_settings[speaker] = {
                "voice": speaker_settings[speaker]["voice"],
                "rate": to_rate_str(raw_rate_value),
            }

        original_dialogue_text = _form_value_to_str(form.get("dialogue_text", ""), "")
        dialogue_text = original_dialogue_text
        if natural_mode:
            dialogue_text = normalize_dialogue_text(dialogue_text, dialogue_language)
        temp_dir = tempfile.mkdtemp(prefix="tts_multi_form_")
        output_path = f"{temp_dir}/{output_name}"
        try:
            await synthesize_dialogue_to_file(
                dialogue_text=dialogue_text,
                speaker_count=speaker_count,
                speaker_settings=speaker_settings,
                temp_dir=temp_dir,
                output_file=output_path,
            )
        except Exception as error:
            if not (natural_mode and _is_no_audio_error(error)):
                raise
            try:
                await synthesize_dialogue_to_file(
                    dialogue_text=original_dialogue_text,
                    speaker_count=speaker_count,
                    speaker_settings=original_speaker_settings,
                    temp_dir=temp_dir,
                    output_file=output_path,
                )
            except Exception as fallback_error:
                if _is_no_audio_error(fallback_error):
                    raise ValueError(_NO_AUDIO_MESSAGE) from fallback_error
                raise
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
            context=_template_context(
                str(error),
                single_language=single_language,
                dialogue_language=dialogue_language,
            ),
            status_code=400,
        )
