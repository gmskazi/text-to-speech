# Text to Speech App

[![CI](https://github.com/gmskazi/japanese-text-to-speech/actions/workflows/ci.yml/badge.svg)](https://github.com/gmskazi/japanese-text-to-speech/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

![App Screenshot](images/ttsapp.webp)

A multilingual text-to-speech app built with FastAPI.

It provides:

- A browser UI for quick audio generation
- A REST API for programmatic use
- Single-speaker and multi-speaker dialogue generation
- MP3 output with optional async job-based workflows

**Note: This is for local use only.**

## Table of Contents

- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start (Docker-first)](#quick-start-docker-first)
- [How to Use the Web App](#how-to-use-the-web-app)
- [API Usage](#api-usage)
- [Natural Mode and Dialogue Parsing Rules](#natural-mode-and-dialogue-parsing-rules)
- [Voice Catalog Notes](#voice-catalog-notes)
- [Local Development (without Docker)](#local-development-without-docker)
- [Quality Checks](#quality-checks)
- [Deployment (Docker-first)](#deployment-docker-first)
- [Troubleshooting](#troubleshooting)
- [Current Limitations](#current-limitations)

## Key Features

- **Single-speaker TTS**: Generate one MP3 from plain text.
- **Multi-speaker dialogue**: Merge speaker turns into one MP3 using `ffmpeg`.
- **Language-aware voice menus**: Query or select curated voices by language.
- **Natural Mode**: Optional normalization and retry behavior for more natural speech output.
- **Sync + async API**:
  - immediate generation endpoints
  - job-based endpoints with polling and download
- **FastAPI docs**: Interactive API docs at `/docs`.

## Tech Stack

- **Language**: Python 3.12+
- **Web framework**: FastAPI
- **Template engine**: Jinja2 (for web UI)
- **Speech synthesis**: edge-tts
- **Audio merge**: ffmpeg (system binary)
- **ASGI server**: uvicorn
- **Validation/models**: Pydantic
- **Lint/Type/Test**: Ruff, mypy, pytest
- **Containerization**: Docker
- **CI**: GitHub Actions (`.github/workflows/ci.yml`)

## Project Structure

```text
.
├── app/
│   ├── api/
│   │   └── routes_tts.py          # REST API endpoints
│   ├── models/
│   │   └── tts_models.py          # Pydantic request/response models
│   ├── services/
│   │   ├── tts_service.py         # TTS orchestration
│   │   ├── audio_merge.py         # ffmpeg concat merge
│   │   └── job_store.py           # in-memory async job store
│   ├── templates/
│   │   └── index.html             # web UI form
│   ├── utils/
│   │   ├── text_utils.py          # parse/normalize/rate helpers
│   │   └── file_utils.py          # filename sanitization
│   ├── config.py                  # language + voice catalogs
│   └── main.py                    # FastAPI app + web routes
├── tests/
│   ├── test_api.py
│   └── test_text_utils.py
├── Dockerfile
├── pyproject.toml
├── .mise.toml
└── .github/workflows/ci.yml
```

## Prerequisites

For Docker-first usage:

- Docker 24+

For local non-Docker usage:

- Python 3.12+
- `ffmpeg` on PATH

## Quick Start (Docker-First)

### 1) Clone

```bash
git clone https://github.com/gmskazi/-text-to-speech.git
cd japanese-text-to-speech
```

### 2) Build Image

```bash
docker build -t tts .
```

### 3) Run Container

```bash
docker run --rm -p 8000:8000 tts
```

### 4) Open App

- Web UI: `http://localhost:8000/`
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

## How to Use the Web App

1. Open `/`.
2. Set **Speaker Count** (`1` to `4`).
3. Set **Output Filename** (auto-sanitized, `.mp3` enforced).
4. For single speaker:
   - Choose language, voice, and speed rate.
   - Paste text.
   - Keep Natural Mode on/off as desired.
5. For dialogue mode:
   - Choose language.
   - Configure each speaker voice/rate.
   - Enter dialogue lines.
6. Click **Generate MP3** to download.

### Dialogue Input Examples

```text
A: こんにちは。
B: はい、どうしましたか？
```

Unlabeled lines are allowed:

```text
A: Good morning.
How was your weekend?
B: Pretty good.
```

In this case, the unlabeled line continues with the previous speaker (`A`).

## API Usage

Base URL (local): `http://localhost:8000`

### Endpoints

- `GET /health`
- `GET /tts/voices`
- `POST /tts/single`
- `POST /tts/dialogue`
- `POST /tts/single/jobs`
- `POST /tts/dialogue/jobs`
- `GET /jobs/{job_id}`
- `GET /jobs/{job_id}/download`

### 1) Health

```bash
curl -s http://localhost:8000/health
```

Expected response:

```json
{ "status": "ok" }
```

### 2) List voices by language

```bash
curl -s "http://localhost:8000/tts/voices?language=ja-JP"
```

### 3) Single-speaker generation

```bash
curl -X POST "http://localhost:8000/tts/single" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "こんにちは。今日はいい天気ですね。",
    "voice": "ja-JP-NanamiNeural",
    "rate": 0,
    "output_name": "single.mp3",
    "natural_mode": true
  }' \
  --output single.mp3
```

### 4) Dialogue generation

```bash
curl -X POST "http://localhost:8000/tts/dialogue" \
  -H "Content-Type: application/json" \
  -d '{
    "speaker_count": 2,
    "dialogue_text": "A: こんにちは。\nB: はい。",
    "speakers": {
      "A": {"voice": "ja-JP-NanamiNeural", "rate": 0},
      "B": {"voice": "ja-JP-KeitaNeural", "rate": 0}
    },
    "output_name": "dialogue.mp3",
    "natural_mode": true
  }' \
  --output dialogue.mp3
```

### 5) Async job workflow (single)

Create job:

```bash
curl -X POST "http://localhost:8000/tts/single/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is an async single-speaker request.",
    "voice": "en-US-JennyNeural",
    "rate": 0,
    "output_name": "job-single.mp3"
  }'
```

Check status:

```bash
curl -s "http://localhost:8000/jobs/<job_id>"
```

Download result when status is `done`:

```bash
curl -L "http://localhost:8000/jobs/<job_id>/download" --output job-single.mp3
```

### 6) Async job workflow (dialogue)

Create job:

```bash
curl -X POST "http://localhost:8000/tts/dialogue/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "speaker_count": 3,
    "dialogue_text": "A: Hello\nB: Hi\nC: Good to see you",
    "speakers": {
      "A": {"voice": "en-US-JennyNeural", "rate": 0},
      "B": {"voice": "en-US-GuyNeural", "rate": 0},
      "C": {"voice": "en-US-AriaNeural", "rate": 0}
    },
    "output_name": "job-dialogue.mp3"
  }'
```

Then poll `/jobs/<job_id>` and download from `/jobs/<job_id>/download`.

## Natural Mode and Dialogue Parsing Rules

### Natural Mode

- **Web UI default**: ON
- **API default**: OFF (unless `natural_mode: true` is passed)

When enabled, the app applies conservative text normalization and retries once with original text if a no-audio condition occurs.

### Dialogue parsing rules

- Valid explicit speaker labels are `A`, `B`, `C`, `D` (up to `speaker_count`).
- Both `:` and `：` are accepted after labels.
- Unlabeled lines continue with the previous speaker.
- If the first non-empty line is unlabeled, it defaults to speaker `A`.
- Empty lines are ignored.

## Voice Catalog Notes

- Voices are curated in `app/config.py` by language.
- Query runtime list via `GET /tts/voices?language=<code>`.
- In this environment, `ja-JP` includes two native voices and curated multilingual fallbacks to support 3-4 speaker scenarios.

## Local Development (without Docker)

Use `mise` for the environment creation and tool installation.

```bash
mise install
mise run run
```

`mise` handles Python tool version and virtualenv wiring from `.mise.toml`.

## Quality Checks

Run all core checks locally:

```bash
python -m compileall app tests
ruff check .
mypy app tests
pytest -q
```

Targeted runs:

```bash
pytest -q tests/test_api.py
pytest -q tests/test_text_utils.py
```

## Current Limitations

- Async job storage is in-memory only (`app/services/job_store.py`), not persistent across restarts.
- No built-in auth/rate-limiting for public API exposure.
- No object storage backend for long-lived audio artifacts.

For production-scale usage, consider adding:

- persistent job backend (Redis/Postgres)
- durable artifact storage (S3/GCS)
- API auth + request throttling
- structured logging and monitoring.
