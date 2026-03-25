from __future__ import annotations

from typing import Final

MAX_SPEAKERS: Final[int] = 4

LANGUAGE_LABELS: Final[dict[str, str]] = {
    "ja-JP": "Japanese",
    "en-US": "English (US)",
    "en-GB": "English (UK)",
    "es-ES": "Spanish",
    "fr-FR": "French",
    "de-DE": "German",
    "ko-KR": "Korean",
    "zh-CN": "Chinese (Mainland)",
}

VOICE_OPTIONS_BY_LANGUAGE: Final[dict[str, dict[str, str]]] = {
    "ja-JP": {
        "Nanami (Female)": "ja-JP-NanamiNeural",
        "Keita (Male)": "ja-JP-KeitaNeural",
        "Ava (Multilingual)": "en-US-AvaMultilingualNeural",
        "Andrew (Multilingual)": "en-US-AndrewMultilingualNeural",
        "Emma (Multilingual)": "en-US-EmmaMultilingualNeural",
        "Vivienne (Multilingual)": "fr-FR-VivienneMultilingualNeural",
        "Hyunsu (Multilingual)": "ko-KR-HyunsuMultilingualNeural",
    },
    "en-US": {
        "Jenny (Female)": "en-US-JennyNeural",
        "Aria (Female)": "en-US-AriaNeural",
        "Guy (Male)": "en-US-GuyNeural",
        "Davis (Male)": "en-US-DavisNeural",
    },
    "en-GB": {
        "Sonia (Female)": "en-GB-SoniaNeural",
        "Libby (Female)": "en-GB-LibbyNeural",
        "Ryan (Male)": "en-GB-RyanNeural",
        "Thomas (Male)": "en-GB-ThomasNeural",
    },
    "es-ES": {
        "Elvira (Female)": "es-ES-ElviraNeural",
        "Alvaro (Male)": "es-ES-AlvaroNeural",
        "Ximena (Female)": "es-ES-XimenaNeural",
    },
    "fr-FR": {
        "Denise (Female)": "fr-FR-DeniseNeural",
        "Eloise (Female)": "fr-FR-EloiseNeural",
        "Henri (Male)": "fr-FR-HenriNeural",
    },
    "de-DE": {
        "Katja (Female)": "de-DE-KatjaNeural",
        "Amala (Female)": "de-DE-AmalaNeural",
        "Conrad (Male)": "de-DE-ConradNeural",
    },
    "ko-KR": {
        "SunHi (Female)": "ko-KR-SunHiNeural",
        "InJoon (Male)": "ko-KR-InJoonNeural",
    },
    "zh-CN": {
        "Xiaoxiao (Female)": "zh-CN-XiaoxiaoNeural",
        "Yunxi (Male)": "zh-CN-YunxiNeural",
        "Xiaoyi (Female)": "zh-CN-XiaoyiNeural",
    },
}

# Backward compatibility for existing imports/tests.
VOICE_OPTIONS: Final[dict[str, str]] = VOICE_OPTIONS_BY_LANGUAGE["ja-JP"]


def language_or_default(language_code: str | None) -> str:
    if language_code in VOICE_OPTIONS_BY_LANGUAGE:
        return str(language_code)
    return "ja-JP"


def voices_for_language(language_code: str | None) -> dict[str, str]:
    return VOICE_OPTIONS_BY_LANGUAGE[language_or_default(language_code)]


def first_voice_for_language(language_code: str | None) -> str:
    options = voices_for_language(language_code)
    return next(iter(options.values()))
