from __future__ import annotations

from pathlib import Path

import edge_tts

from app.services.audio_merge import merge_mp3_files
from app.utils.text_utils import DialogueLine, parse_dialogue


async def generate_single_speaker(
    text: str,
    voice: str,
    rate: str,
    output_file: str,
) -> None:
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(output_file)


async def generate_dialogue_parts(
    lines: list[DialogueLine],
    temp_dir: str,
) -> list[str]:
    output_files: list[str] = []
    for index, line in enumerate(lines):
        out_file = Path(temp_dir) / f"part_{index:03d}.mp3"
        communicate = edge_tts.Communicate(
            text=line["text"],
            voice=line["voice"],
            rate=line["rate"],
        )
        await communicate.save(str(out_file))
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
