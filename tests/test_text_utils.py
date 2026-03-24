from __future__ import annotations

import pytest

from app.utils.file_utils import ensure_mp3_name
from app.utils.text_utils import parse_dialogue, to_rate_str


def test_ensure_mp3_name_sanitizes_and_appends_extension() -> None:
    assert ensure_mp3_name("../../tmp/voice") == "voice.mp3"
    assert ensure_mp3_name("lesson.mp3") == "lesson.mp3"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, "-20%"),
        ("-20", "-20%"),
        ("abc", "-20%"),
        (100, "+80%"),
        (-100, "-80%"),
        (5, "+5%"),
    ],
)
def test_to_rate_str(value: str | int | None, expected: str) -> None:
    assert to_rate_str(value) == expected


def test_parse_dialogue_valid() -> None:
    settings = {
        "A": {"voice": "ja-JP-NanamiNeural", "rate": "-20%"},
        "B": {"voice": "ja-JP-KeitaNeural", "rate": "+0%"},
    }

    parsed = parse_dialogue("A: こんにちは\nB: はい", 2, settings)

    assert len(parsed) == 2
    assert parsed[0]["speaker"] == "A"
    assert parsed[1]["voice"] == "ja-JP-KeitaNeural"


def test_parse_dialogue_rejects_invalid_speaker() -> None:
    settings = {"A": {"voice": "ja-JP-NanamiNeural", "rate": "-20%"}}

    with pytest.raises(ValueError, match="Invalid speaker"):
        parse_dialogue("B: テスト", 1, settings)


def test_parse_dialogue_rejects_missing_prefix() -> None:
    settings = {"A": {"voice": "ja-JP-NanamiNeural", "rate": "-20%"}}

    with pytest.raises(ValueError, match="missing a speaker prefix"):
        parse_dialogue("これは不正な行", 1, settings)
