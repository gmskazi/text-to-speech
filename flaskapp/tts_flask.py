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
    :root {
      --bg: #f5f7fa;
      --surface: #ffffff;
      --surface-alt: #f8fafc;
      --text: #1f2937;
      --muted: #5b6472;
      --border: #dbe2ea;
      --accent: #111827;
      --accent-hover: #0b1220;
      --success-bg: #e8f7ee;
      --success-text: #166534;
      --error-bg: #feeceb;
      --error-text: #991b1b;
      --shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
      --radius-lg: 20px;
      --radius-md: 14px;
      --radius-sm: 10px;
      --max-width: 1120px;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      font-family: Inter, Arial, Helvetica, sans-serif;
      background: linear-gradient(180deg, #f8fafc 0%, #f3f6f9 100%);
      color: var(--text);
      line-height: 1.6;
    }

    .page {
      width: min(var(--max-width), calc(100% - 32px));
      margin: 0 auto;
      padding: 28px 0 40px;
    }

    .hero {
      background: var(--surface);
      border: 1px solid rgba(219, 226, 234, 0.85);
      border-radius: 28px;
      box-shadow: var(--shadow);
      padding: 32px;
      margin-bottom: 22px;
    }

    .hero-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 14px;
      border-radius: 999px;
      border: 1px solid var(--border);
      background: var(--surface-alt);
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.02em;
      text-transform: uppercase;
    }

    .hero h1 {
      margin: 16px 0 12px;
      font-size: clamp(2rem, 4vw, 3rem);
      line-height: 1.1;
      letter-spacing: -0.03em;
    }

    .hero p {
      margin: 0;
      max-width: 760px;
      color: var(--muted);
      font-size: 1rem;
    }

    .layout {
      display: grid;
      grid-template-columns: minmax(0, 1.9fr) minmax(300px, 0.95fr);
      gap: 22px;
      align-items: start;
    }

    .card {
      background: var(--surface);
      border: 1px solid rgba(219, 226, 234, 0.85);
      border-radius: var(--radius-lg);
      box-shadow: var(--shadow);
      padding: 26px;
    }

    .card + .card {
      margin-top: 18px;
    }

    .card h2 {
      margin: 0 0 6px;
      font-size: 1.35rem;
      letter-spacing: -0.02em;
    }

    .section-copy {
      margin: 0 0 18px;
      color: var(--muted);
      font-size: 0.98rem;
    }

    .flash {
      padding: 14px 16px;
      border-radius: var(--radius-md);
      margin-bottom: 18px;
      font-size: 0.96rem;
      border: 1px solid transparent;
    }

    .flash.error {
      background: var(--error-bg);
      color: var(--error-text);
      border-color: #f7c7c2;
    }

    .flash.success {
      background: var(--success-bg);
      color: var(--success-text);
      border-color: #b7e2c5;
    }

    .field-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
    }

    label {
      display: block;
      font-size: 0.95rem;
      font-weight: 700;
      margin-bottom: 8px;
    }

    input[type="text"],
    input[type="number"],
    select,
    textarea {
      width: 100%;
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      background: #fff;
      color: var(--text);
      padding: 13px 14px;
      font-size: 15px;
      transition: border-color 0.2s ease, box-shadow 0.2s ease;
      appearance: none;
    }

    textarea {
      min-height: 230px;
      resize: vertical;
    }

    input:focus,
    select:focus,
    textarea:focus {
      outline: none;
      border-color: #9aa7b8;
      box-shadow: 0 0 0 4px rgba(148, 163, 184, 0.14);
    }

    .hint,
    .helper {
      color: var(--muted);
      font-size: 0.9rem;
      margin-top: 8px;
    }

    .helper {
      margin-bottom: 0;
    }

    .speaker-picker {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }

    .speaker-picker button {
      appearance: none;
      border: 1px solid var(--border);
      background: var(--surface-alt);
      color: var(--text);
      border-radius: 999px;
      padding: 12px 14px;
      font-weight: 700;
      font-size: 0.95rem;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .speaker-picker button.active {
      background: var(--accent);
      color: #fff;
      border-color: var(--accent);
    }

    .speaker-box {
      background: var(--surface-alt);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 18px;
      margin-bottom: 14px;
    }

    .speaker-box h3 {
      margin: 0 0 12px;
      font-size: 1rem;
    }

    .actions {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 14px;
      margin-top: 22px;
    }

    .primary-btn {
      appearance: none;
      border: none;
      background: var(--accent);
      color: #fff;
      border-radius: 14px;
      padding: 14px 20px;
      font-size: 15px;
      font-weight: 700;
      cursor: pointer;
      transition: background 0.2s ease, transform 0.2s ease;
      min-width: 190px;
    }

    .primary-btn:hover {
      background: var(--accent-hover);
      transform: translateY(-1px);
    }

    .subtle-note {
      color: var(--muted);
      font-size: 0.92rem;
    }

    .sidebar-list {
      display: grid;
      gap: 12px;
      margin: 0;
      padding: 0;
      list-style: none;
    }

    .sidebar-list li {
      padding: 14px 14px;
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      background: var(--surface-alt);
      color: var(--text);
    }

    .sidebar-list strong {
      display: block;
      margin-bottom: 4px;
      font-size: 0.95rem;
    }

    code {
      background: #eef2f7;
      color: #162033;
      padding: 2px 7px;
      border-radius: 8px;
      font-size: 0.9em;
    }

    .mobile-only {
      display: none;
    }

    @media (max-width: 960px) {
      .layout {
        grid-template-columns: 1fr;
      }

      .sidebar {
        order: 2;
      }
    }

    @media (max-width: 680px) {
      .page {
        width: min(100% - 20px, var(--max-width));
        padding-top: 16px;
      }

      .hero,
      .card {
        padding: 20px;
        border-radius: 22px;
      }

      .field-grid,
      .speaker-picker {
        grid-template-columns: 1fr;
      }

      .speaker-picker button {
        padding: 13px 16px;
      }

      .actions {
        flex-direction: column;
        align-items: stretch;
      }

      .primary-btn {
        width: 100%;
      }

      textarea {
        min-height: 180px;
      }
    }
  </style>
  <script>
    function setSpeakerCount(value) {
      document.getElementById('speaker_count').value = value;
      document.querySelectorAll('.speaker-picker button').forEach((button) => {
        button.classList.toggle('active', parseInt(button.dataset.value, 10) === value);
      });
      toggleMode();
    }

    function toggleMode() {
      const speakerCount = parseInt(document.getElementById('speaker_count').value, 10);
      const multiSection = document.getElementById('multi-speaker-section');
      const singleSection = document.getElementById('single-speaker-section');
      const speakerBoxes = document.querySelectorAll('.speaker-box');

      if (speakerCount === 1) {
        singleSection.style.display = 'block';
        multiSection.style.display = 'none';
      } else {
        singleSection.style.display = 'none';
        multiSection.style.display = 'block';

        speakerBoxes.forEach((box) => {
          const speaker = box.getAttribute('data-speaker');
          const speakerIndex = speaker.charCodeAt(0) - 'A'.charCodeAt(0) + 1;
          box.style.display = speakerIndex <= speakerCount ? 'block' : 'none';
        });
      }
    }

    window.addEventListener('DOMContentLoaded', () => {
      const initial = parseInt(document.getElementById('speaker_count').value, 10);
      setSpeakerCount(initial);
    });
  </script>
</head>
<body>
  <div class="page">
    <section class="hero">
      <div class="hero-badge">Made Easy IT Tool</div>
      <h1>Japanese Text to Audio Generator</h1>
      <p>Convert Japanese text into clean MP3 audio with one or multiple speakers, adjustable playback speed, and natural Japanese voices. Designed to be simple to use on desktop and mobile.</p>
    </section>

    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, message in messages %}
          <div class="flash {{ category }}">{{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    <div class="layout">
      <main>
        <form method="post" action="{{ url_for('generate_audio') }}">
          <section class="card">
            <h2>Audio Settings</h2>
            <p class="section-copy">Choose how many people are speaking, set the voice style, then generate an MP3 file ready to download.</p>

            <label for="speaker_count">How many speakers?</label>
            <input type="hidden" name="speaker_count" id="speaker_count" value="1">
            <div class="speaker-picker" role="group" aria-label="Select number of speakers">
              <button type="button" data-value="1" onclick="setSpeakerCount(1)">1 Speaker</button>
              <button type="button" data-value="2" onclick="setSpeakerCount(2)">2 Speakers</button>
              <button type="button" data-value="3" onclick="setSpeakerCount(3)">3 Speakers</button>
              <button type="button" data-value="4" onclick="setSpeakerCount(4)">4 Speakers</button>
            </div>

            <div id="single-speaker-section">
              <div class="field-grid">
                <div>
                  <label for="single_voice">Voice</label>
                  <select name="single_voice" id="single_voice">
                    {% for label, value in voices.items() %}
                      <option value="{{ value }}">{{ label }}</option>
                    {% endfor %}
                  </select>
                </div>
                <div>
                  <label for="single_rate">Speaking Speed (%)</label>
                  <input type="number" id="single_rate" name="single_rate" value="-20" min="-80" max="80" step="5">
                  <p class="helper">Use negative values to slow it down. Example: <code>-20</code> = 20% slower.</p>
                </div>
              </div>

              <label for="single_text">Japanese Text</label>
              <textarea id="single_text" name="single_text" placeholder="Paste your Japanese text here..."></textarea>
            </div>

            <div id="multi-speaker-section" style="display:none;">
              <p class="section-copy">Enter one line per speaker using prefixes like <code>A:</code>, <code>B:</code>, <code>C:</code>, or <code>D:</code>. Only the speakers you selected will appear below.</p>

              {% for speaker in ['A', 'B', 'C', 'D'] %}
                <div class="speaker-box" data-speaker="{{ speaker }}">
                  <h3>Speaker {{ speaker }}</h3>
                  <div class="field-grid">
                    <div>
                      <label for="voice_{{ speaker }}">Voice</label>
                      <select name="voice_{{ speaker }}" id="voice_{{ speaker }}">
                        {% for label, value in voices.items() %}
                          <option value="{{ value }}">{{ label }}</option>
                        {% endfor %}
                      </select>
                    </div>
                    <div>
                      <label for="rate_{{ speaker }}">Speaking Speed (%)</label>
                      <input type="number" id="rate_{{ speaker }}" name="rate_{{ speaker }}" value="-20" min="-80" max="80" step="5">
                    </div>
                  </div>
                </div>
              {% endfor %}

              <label for="dialogue_text">Dialogue Text</label>
              <textarea id="dialogue_text" name="dialogue_text" placeholder="A: すみません。
B: はい。
A: きっぷうりばは どこですか。"></textarea>
            </div>

            <div class="field-grid" style="margin-top:18px;">
              <div>
                <label for="output_name">Output Filename</label>
                <input type="text" id="output_name" name="output_name" value="japanese_audio.mp3">
              </div>
            </div>

            <div class="actions">
              <button class="primary-btn" type="submit">Generate MP3</button>
              <div class="subtle-note">Fast, clean and mobile-friendly. Multi-speaker mode uses FFmpeg to merge each line in order.</div>
            </div>
          </section>
        </form>
      </main>

      <aside class="sidebar">
        <section class="card">
          <h2>How to Use</h2>
          <ul class="sidebar-list">
            <li>
              <strong>Single speaker</strong>
              Paste your full text, choose a voice, set the speed, and generate one MP3.
            </li>
            <li>
              <strong>Multiple speakers</strong>
              Select the number of speakers, assign voices, and prefix each line with <code>A:</code>, <code>B:</code>, <code>C:</code>, or <code>D:</code>.
            </li>
            <li>
              <strong>Control the pace</strong>
              Slow speech down for study and listening practice, or increase speed for faster review.
            </li>
          </ul>
        </section>

        <section class="card">
          <h2>Good For</h2>
          <ul class="sidebar-list">
            <li>
              <strong>Listening practice</strong>
              Create custom audio from textbook passages or class notes.
            </li>
            <li>
              <strong>Roleplays</strong>
              Generate station, restaurant, travel, and classroom dialogues with multiple voices.
            </li>
            <li>
              <strong>Revision</strong>
              Turn vocabulary lists and short readings into repeatable study audio.
            </li>
          </ul>
        </section>
      </aside>
    </div>
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
