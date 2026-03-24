from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def merge_mp3_files(input_files: list[str], output_file: str, temp_dir: str) -> None:
    if not input_files:
        raise ValueError("No audio parts were generated for merge.")

    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is not installed or not in PATH.")

    concat_list = Path(temp_dir) / "concat.txt"
    with concat_list.open("w", encoding="utf-8") as file_handle:
        for path in input_files:
            safe_path = path.replace("'", "'\\''")
            file_handle.write(f"file '{safe_path}'\n")

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_list),
            "-c",
            "copy",
            output_file,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
