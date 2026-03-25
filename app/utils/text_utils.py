from __future__ import annotations

from typing import TypedDict

from app.config import MAX_SPEAKERS


class DialogueLine(TypedDict):
    speaker: str
    text: str
    voice: str
    rate: str


def to_rate_str(value: str | int | float | None) -> str:
    if value is None:
        rate = 0
    else:
        try:
            rate = int(value)
        except (TypeError, ValueError):
            rate = 0
    rate = max(-80, min(80, rate))
    return f"{rate:+d}%"


def parse_dialogue(
    raw_text: str,
    speaker_count: int,
    speaker_settings: dict[str, dict[str, str]],
) -> list[DialogueLine]:
    if speaker_count < 1 or speaker_count > MAX_SPEAKERS:
        raise ValueError(
            f"Speaker count must be between 1 and {MAX_SPEAKERS}."
        )

    allowed_speakers = [chr(ord("A") + i) for i in range(speaker_count)]
    parsed: list[DialogueLine] = []

    for raw_line in raw_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if ":" not in line:
            raise ValueError(f"Line is missing a speaker prefix: {line}")

        speaker, text = line.split(":", 1)
        speaker = speaker.strip().upper()
        text = text.strip()

        if speaker not in allowed_speakers:
            allowed = ", ".join(allowed_speakers)
            raise ValueError(
                f"Invalid speaker '{speaker}'. Allowed speakers: {allowed}"
            )

        if not text:
            raise ValueError(f"Speaker {speaker} has an empty line.")

        if speaker not in speaker_settings:
            raise ValueError(f"Missing voice/rate settings for speaker {speaker}.")

        parsed.append(
            {
                "speaker": speaker,
                "text": text,
                "voice": speaker_settings[speaker]["voice"],
                "rate": speaker_settings[speaker]["rate"],
            }
        )

    if not parsed:
        raise ValueError("No dialogue lines were provided.")

    return parsed
