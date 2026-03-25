from __future__ import annotations

from pathlib import Path

import edge_tts

from app.config import first_voice_for_language, language_or_default
from app.services.audio_merge import merge_mp3_files
from app.utils.text_utils import (
    DialogueLine,
    contains_speakable_content,
    infer_language_from_voice,
    parse_dialogue,
)


def _is_no_audio_error(error: Exception) -> bool:
    return "no audio was received" in str(error).lower()


async def _save_with_voice_fallback(
    *,
    text: str,
    voice: str,
    rate: str,
    output_file: str,
) -> None:
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    no_audio_error: Exception | None = None
    try:
        await communicate.save(output_file)
        return
    except Exception as error:
        if not _is_no_audio_error(error):
            raise
        no_audio_error = error

    language = language_or_default(infer_language_from_voice(voice))
    fallback_voice = first_voice_for_language(language)
    if fallback_voice == voice:
        if no_audio_error is not None:
            raise no_audio_error
        raise RuntimeError("No audio was received.")

    fallback_communicate = edge_tts.Communicate(
        text=text,
        voice=fallback_voice,
        rate=rate,
    )
    await fallback_communicate.save(output_file)


async def generate_single_speaker(
    text: str,
    voice: str,
    rate: str,
    output_file: str,
) -> None:
    if not contains_speakable_content(text):
        raise ValueError(
            "Input text does not contain speakable content. "
            "Please include letters, numbers, or words."
        )
    await _save_with_voice_fallback(
        text=text,
        voice=voice,
        rate=rate,
        output_file=output_file,
    )


async def generate_dialogue_parts(
    lines: list[DialogueLine],
    temp_dir: str,
) -> list[str]:
    output_files: list[str] = []
    for index, line in enumerate(lines):
        if not contains_speakable_content(line["text"]):
            raise ValueError(
                f"Speaker {line['speaker']} line does not contain speakable content."
            )
        out_file = Path(temp_dir) / f"part_{index:03d}.mp3"
        await _save_with_voice_fallback(
            text=line["text"],
            voice=line["voice"],
            rate=line["rate"],
            output_file=str(out_file),
        )
        output_files.append(str(out_file))
    return output_files


async def synthesize_single_to_file(
    *,
    text: str,
    voice: str,
    rate: str,
    output_file: str,
) -> None:
    await generate_single_speaker(
        text=text,
        voice=voice,
        rate=rate,
        output_file=output_file,
    )


async def synthesize_dialogue_to_file(
    *,
    dialogue_text: str,
    speaker_count: int,
    speaker_settings: dict[str, dict[str, str]],
    temp_dir: str,
    output_file: str,
) -> None:
    parsed_lines = parse_dialogue(dialogue_text, speaker_count, speaker_settings)
    part_files = await generate_dialogue_parts(parsed_lines, temp_dir)
    merge_mp3_files(part_files, output_file, temp_dir)
