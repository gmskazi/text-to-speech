from __future__ import annotations

import asyncio
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict

from flask import (
    Flask,
    request,
    render_template_string,
    send_file,
    flash,
    redirect,
    url_for,
)
import edge_tts

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

# Japanese neural voices
VOICE_OPTIONS: Dict[str, str] = {
    "Nanami (Female)": "ja-JP-NanamiNeural",
    "Keita (Male)": "ja-JP-KeitaNeural",
    "Aoi (Female)": "ja-JP-AoiNeural",
    "Daichi (Male)": "ja-JP-DaichiNeural",
    "Mayu (Female)": "ja-JP-MayuNeural",
    "Naoki (Male)": "ja-JP-NaokiNeural",
    "Shiori (Female)": "ja-JP-ShioriNeural",
    "Masaru (Male)": "ja-JP-MasaruMultilingualNeural",
}

HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Japanese Text to Audio Generator</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      max-width: 1000px;
      margin: 40px auto;
      padding: 0 20px;
      line-height: 1.5;
      background: #f7f7f8;
      color: #222;
    }
    .card {
      background: white;
      border-radius: 14px;
      padding: 24px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.08);
      margin-bottom: 20px;
    }
    h1, h2 { margin-top: 0; }
    textarea, select, input[type="text"], input[type="number"] {
      width: 100%;
      padding: 10px;
      border: 1px solid #ccc;
      border-radius: 8px;
      box-sizing: border-box;
      margin-top: 6px;
      margin-bottom: 14px;
      font-size: 14px;
    }
    label {
      font-weight: bold;
      display: block;
      margin-top: 10px;
    }
    .row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }
    .speaker-box {
      border: 1px solid #ddd;
      border-radius: 10px;
      padding: 16px;
      margin-bottom: 14px;
      background: #fafafa;
    }
    button {
      background: #111827;
      color: white;
      border: none;
      padding: 12px 18px;
      border-radius: 10px;
      cursor: pointer;
      font-size: 15px;
    }
    button:hover { opacity: 0.95; }
    .hint {
      font-size: 13px;
      color: #555;
      margin-top: -8px;
      margin-bottom: 12px;
    }
    .flash {
      padding: 12px;
      border-radius: 8px;
      margin-bottom: 12px;
    }
    .flash.error { background: #fee2e2; color: #991b1b; }
    .flash.success { background: #dcfce7; color: #166534; }
    code {
      background: #f1f5f9;
      padding: 2px 6px;
      border-radius: 6px;
    }
  </style>
  <script>
    function toggleMode() {
      const speakerCount = parseInt(document.getElementById('speaker_count').value, 10);
      const multiSection = document.getElementById('multi-speaker-section');
      const singleSection = document.getElementById('single-speaker-section');

      if (speakerCount === 1) {
        singleSection.style.display = 'block';
        multiSection.style.display = 'none';
      } else {
        singleSection.style.display = 'none';
        multiSection.style.display = 'block';
      }
    }

    window.addEventListener('DOMContentLoaded', toggleMode);
  </script>
</head>
<body>
  <div class="card">
    <h1>Japanese Text to Audio Generator</h1>
    <p>Create MP3 audio from Japanese text using Edge TTS voices. You can use one voice or split lines between multiple speakers.</p>

    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, message in messages %}
          <div class="flash {{ category }}">{{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    <form method="post" action="{{ url_for('generate_audio') }}">
      <label for="speaker_count">How many speakers?</label>
      <select name="speaker_count" id="speaker_count" onchange="toggleMode()">
        <option value="1">1 speaker</option>
        <option value="2">2 speakers</option>
        <option value="3">3 speakers</option>
        <option value="4">4 speakers</option>
      </select>

      <div id="single-speaker-section">
        <div class="row">
          <div>
            <label for="single_voice">Voice</label>
            <select name="single_voice" id="single_voice">
              {% for label, value in voices.items() %}
                <option value="{{ value }}">{{ label }}</option>
              {% endfor %}
            </select>
          </div>
          <div>
            <label for="single_rate">Speed (%)</label>
            <input type="number" id="single_rate" name="single_rate" value="-20" min="-80" max="80" step="5">
            <div class="hint">Negative is slower. Example: <code>-20</code> = 20% slower</div>
          </div>
        </div>

        <label for="single_text">Text</label>
        <textarea id="single_text" name="single_text" rows="10" placeholder="Paste Japanese text here..."></textarea>
      </div>

      <div id="multi-speaker-section" style="display:none;">
        <p class="hint">Use one line per piece of dialogue. Prefix each line with <code>A:</code>, <code>B:</code>, <code>C:</code>, or <code>D:</code>.</p>

        {% for speaker in ['A', 'B', 'C', 'D'] %}
          <div class="speaker-box">
            <h2>Speaker {{ speaker }}</h2>
            <div class="row">
              <div>
                <label for="voice_{{ speaker }}">Voice</label>
                <select name="voice_{{ speaker }}" id="voice_{{ speaker }}">
                  {% for label, value in voices.items() %}
                    <option value="{{ value }}">{{ label }}</option>
                  {% endfor %}
                </select>
              </div>
              <div>
                <label for="rate_{{ speaker }}">Speed (%)</label>
                <input type="number" id="rate_{{ speaker }}" name="rate_{{ speaker }}" value="-20" min="-80" max="80" step="5">
              </div>
            </div>
          </div>
        {% endfor %}

        <label for="dialogue_text">Dialogue text</label>
        <textarea id="dialogue_text" name="dialogue_text" rows="12" placeholder="A: すみません。\nB: はい。\nA: きっぷうりばは どこですか。"></textarea>
      </div>

      <label for="output_name">Output filename</label>
      <input type="text" id="output_name" name="output_name" value="japanese_audio.mp3">

      <button type="submit">Generate MP3</button>
    </form>
  </div>

  <div class="card">
    <h2>Notes</h2>
    <ul>
      <li>You need <code>ffmpeg</code> installed to merge multiple speaker files.</li>
      <li>For one speaker, the app creates a single MP3 directly.</li>
      <li>For multiple speakers, each line is generated separately and merged in order.</li>
    </ul>
  </div>
</body>
</html>
"""


def ensure_mp3_name(name: str) -> str:
    name = (name or "japanese_audio.mp3").strip()
    if not name.lower().endswith(".mp3"):
        name += ".mp3"
    return Path(name).name


def to_rate_str(value: str | int | float | None) -> str:
    try:
        rate = int(value)
    except (TypeError, ValueError):
        rate = -20
    rate = max(-80, min(80, rate))
    return f"{rate:+d}%"


async def generate_single_speaker(
    text: str, voice: str, rate: str, output_file: str
) -> None:
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(output_file)


async def generate_dialogue_parts(
    lines: List[Dict[str, str]], temp_dir: str
) -> List[str]:
    output_files: List[str] = []
    for index, line in enumerate(lines):
        out_file = os.path.join(temp_dir, f"part_{index:03d}.mp3")
        communicate = edge_tts.Communicate(
            text=line["text"],
            voice=line["voice"],
            rate=line["rate"],
        )
        await communicate.save(out_file)
        output_files.append(out_file)
    return output_files


def merge_mp3_files(input_files: List[str], output_file: str, temp_dir: str) -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is not installed or not in PATH.")

    concat_list = os.path.join(temp_dir, "concat.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for path in input_files:
            safe_path = path.replace("'", "'\\''")
            f.write(f"file '{safe_path}'\n")

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            concat_list,
            "-c",
            "copy",
            output_file,
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def parse_dialogue(
    raw_text: str, speaker_count: int, speaker_settings: Dict[str, Dict[str, str]]
) -> List[Dict[str, str]]:
    allowed_speakers = [chr(ord("A") + i) for i in range(speaker_count)]
    parsed: List[Dict[str, str]] = []

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
            raise ValueError(
                f"Invalid speaker '{speaker}'. Allowed speakers: {', '.join(allowed_speakers)}"
            )
        if not text:
            raise ValueError(f"Speaker {speaker} has an empty line.")

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


@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML, voices=VOICE_OPTIONS)


@app.route("/generate", methods=["POST"])
def generate_audio():
    speaker_count = int(request.form.get("speaker_count", "1"))
    output_name = ensure_mp3_name(request.form.get("output_name", "japanese_audio.mp3"))

    try:
        if speaker_count == 1:
            text = request.form.get("single_text", "").strip()
            if not text:
                raise ValueError("Please enter some text for the single-speaker mode.")

            voice = request.form.get("single_voice", "ja-JP-NanamiNeural")
            rate = to_rate_str(request.form.get("single_rate", -20))

            temp_dir = tempfile.mkdtemp(prefix="tts_single_")
            try:
                output_path = os.path.join(temp_dir, output_name)
                asyncio.run(
                    generate_single_speaker(
                        text=text, voice=voice, rate=rate, output_file=output_path
                    )
                )
                return send_file(
                    output_path, as_attachment=True, download_name=output_name
                )
            finally:
                # send_file needs the file to still exist until response is sent, so do not remove here
                pass

        speaker_settings = {}
        for speaker in ["A", "B", "C", "D"]:
            speaker_settings[speaker] = {
                "voice": request.form.get(f"voice_{speaker}", "ja-JP-NanamiNeural"),
                "rate": to_rate_str(request.form.get(f"rate_{speaker}", -20)),
            }

        dialogue_text = request.form.get("dialogue_text", "")
        parsed_lines = parse_dialogue(dialogue_text, speaker_count, speaker_settings)

        temp_dir = tempfile.mkdtemp(prefix="tts_multi_")
        output_path = os.path.join(temp_dir, output_name)

        part_files = asyncio.run(generate_dialogue_parts(parsed_lines, temp_dir))
        merge_mp3_files(part_files, output_path, temp_dir)
        return send_file(output_path, as_attachment=True, download_name=output_name)

    except subprocess.CalledProcessError as e:
        error_text = e.stderr.strip() if e.stderr else str(e)
        flash(f"FFmpeg failed: {error_text}", "error")
        return redirect(url_for("index"))
    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
