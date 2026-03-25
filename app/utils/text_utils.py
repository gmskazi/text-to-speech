from __future__ import annotations

import re
import unicodedata
from typing import TypedDict

from app.config import MAX_SPEAKERS


class DialogueLine(TypedDict):
    speaker: str
    text: str
    voice: str
    rate: str


_VOICE_LANG_RE = re.compile(r"^[a-z]{2}-[A-Z]{2}")
_DIALOGUE_LABEL_RE = re.compile(r"^\s*([A-Za-z])\s*[:：]\s*(.*)$")


def infer_language_from_voice(voice: str, fallback: str = "ja-JP") -> str:
    match = _VOICE_LANG_RE.match(voice)
    if match is None:
        return fallback
    return match.group(0)


def normalize_for_speech(text: str, language: str) -> str:
    collapsed = re.sub(r"[ \t]+", " ", text)
    lines = [line.strip() for line in collapsed.splitlines()]
    normalized: list[str] = []

    for line in lines:
        if not line:
            continue
        normalized.append(_normalize_line_for_language(line, language))

    return "\n".join(normalized)


def normalize_dialogue_text(dialogue_text: str, language: str) -> str:
    normalized_lines: list[str] = []

    for raw_line in dialogue_text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        match = _DIALOGUE_LABEL_RE.match(stripped)
        if match is None:
            normalized_lines.append(stripped)
            continue

        speaker = match.group(1)
        text = match.group(2)
        normalized_text = normalize_for_speech(text, language)
        normalized_lines.append(f"{speaker.strip()}: {normalized_text}".strip())

    return "\n".join(normalized_lines)


def contains_speakable_content(text: str) -> bool:
    for char in text:
        if char.isspace():
            continue
        category = unicodedata.category(char)
        if category.startswith(("L", "N")) or category == "So":
            return True
    return False


def _normalize_line_for_language(text: str, language: str) -> str:
    normalized = text

    if language.startswith("en-"):
        normalized = re.sub(r"([!?])\1+", r"\1", normalized)
        normalized = re.sub(r"\.{4,}", "...", normalized)
    elif language.startswith("ja-"):
        normalized = re.sub(r"([！？])\1+", r"\1", normalized)
        normalized = re.sub(r"。{2,}", "。", normalized)
        normalized = re.sub(r"…{2,}", "…", normalized)

    return normalized


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
        raise ValueError(f"Speaker count must be between 1 and {MAX_SPEAKERS}.")

    allowed_speakers = [chr(ord("A") + i) for i in range(speaker_count)]
    parsed: list[DialogueLine] = []
    last_speaker: str | None = None

    for raw_line in raw_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        speaker = last_speaker or "A"
        text = line

        match = _DIALOGUE_LABEL_RE.match(line)
        if match is not None:
            candidate = match.group(1).strip().upper()
            if candidate in allowed_speakers:
                speaker = candidate
                text = match.group(2).strip()
            else:
                text = line

        last_speaker = speaker

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
