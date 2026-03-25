from __future__ import annotations

import pytest

from app.utils.file_utils import ensure_mp3_name
from app.utils.text_utils import (
    contains_speakable_content,
    normalize_dialogue_text,
    normalize_for_speech,
    parse_dialogue,
    to_rate_str,
)


def test_ensure_mp3_name_sanitizes_and_appends_extension() -> None:
    assert ensure_mp3_name("../../tmp/voice") == "voice.mp3"
    assert ensure_mp3_name("lesson.mp3") == "lesson.mp3"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, "+0%"),
        ("-20", "-20%"),
        ("abc", "+0%"),
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

    parsed = parse_dialogue("B: テスト", 1, settings)
    assert parsed[0]["speaker"] == "A"
    assert parsed[0]["text"] == "B: テスト"


def test_parse_dialogue_missing_prefix_uses_last_or_default_speaker() -> None:
    settings = {"A": {"voice": "ja-JP-NanamiNeural", "rate": "-20%"}}
    parsed = parse_dialogue("これは不正な行\n続きの行", 1, settings)
    assert len(parsed) == 2
    assert parsed[0]["speaker"] == "A"
    assert parsed[1]["speaker"] == "A"


def test_parse_dialogue_unlabeled_line_continues_previous_speaker() -> None:
    settings = {
        "A": {"voice": "ja-JP-NanamiNeural", "rate": "-20%"},
        "B": {"voice": "ja-JP-KeitaNeural", "rate": "+0%"},
    }
    parsed = parse_dialogue("A: こんにちは\n続きます\nB: はい", 2, settings)
    assert parsed[0]["speaker"] == "A"
    assert parsed[1]["speaker"] == "A"
    assert parsed[2]["speaker"] == "B"


def test_parse_dialogue_supports_fullwidth_colon_labels() -> None:
    settings = {
        "A": {"voice": "ja-JP-NanamiNeural", "rate": "-20%"},
        "B": {"voice": "ja-JP-KeitaNeural", "rate": "+0%"},
    }
    parsed = parse_dialogue("A：こんにちは\nB：はい", 2, settings)
    assert parsed[0]["speaker"] == "A"
    assert parsed[1]["speaker"] == "B"


def test_normalize_for_speech_english() -> None:
    text = "Hello!!!    How are you????"
    assert normalize_for_speech(text, "en-US") == "Hello! How are you?"


def test_normalize_for_speech_japanese() -> None:
    text = "こんにちは！！！   元気ですか？？"
    assert normalize_for_speech(text, "ja-JP") == "こんにちは！ 元気ですか？"


def test_normalize_dialogue_text_preserves_labels() -> None:
    dialogue = "A: Hello!!!\nB: I'm fine????"
    normalized = normalize_dialogue_text(dialogue, "en-US")
    assert normalized == "A: Hello!\nB: I'm fine?"


def test_normalize_dialogue_text_supports_fullwidth_colon() -> None:
    dialogue = "A：Hello!!!\nB：I am fine????"
    normalized = normalize_dialogue_text(dialogue, "en-US")
    assert normalized == "A: Hello!\nB: I am fine?"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Hello", True),
        ("こんにちは", True),
        ("123", True),
        ("🙂", True),
        ("...", False),
        ("!!!", False),
        ("   ", False),
    ],
)
def test_contains_speakable_content(value: str, expected: bool) -> None:
    assert contains_speakable_content(value) is expected
