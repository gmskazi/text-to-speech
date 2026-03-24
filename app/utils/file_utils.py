from __future__ import annotations

from pathlib import Path


def ensure_mp3_name(name: str) -> str:
    safe_name = (name or "japanese_audio.mp3").strip()
    if not safe_name.lower().endswith(".mp3"):
        safe_name += ".mp3"
    return Path(safe_name).name
