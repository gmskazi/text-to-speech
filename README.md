# Text to Speech App

[![CI](https://github.com/gmskazi/text-to-speech/actions/workflows/ci.yml/badge.svg?branch=main&event=push)](https://github.com/gmskazi/text-to-speech/actions/workflows/ci.yml?query=branch%3Amain)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

![App Screenshot](images/ttsapp.webp)

Multilingual text-to-speech app built with FastAPI.

- Browser UI for quick audio generation
- REST API for programmatic use
- Single-speaker and multi-speaker dialogue generation
- MP3 output with optional async job-based workflows

**Note: This project is currently optimized for personal/local use.**

## Table of Contents

- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start (Docker)](#quick-start-docker)
- [Local Development (mise)](#local-development-mise)
- [Checks and Linting](#checks-and-linting)
- [How to Use the Web App](#how-to-use-the-web-app)
- [API Usage](#api-usage)
- [Natural Mode and Dialogue Rules](#natural-mode-and-dialogue-rules)
- [CI and Security Notes](#ci-and-security-notes)
- [Deployment Plan](#deployment-plan)
- [Current Limitations](#current-limitations)

## Key Features

- **Single-speaker TTS**: Generate one MP3 from plain text.
- **Multi-speaker dialogue**: Merge speaker turns into one MP3 with `ffmpeg`.
- **Language-aware voice menus**: Query or select curated voices by language.
- **Natural mode**: Optional normalization and retry behavior.
- **Sync + async API**:
  - immediate generation endpoints
  - job-based endpoints with polling and download
- **FastAPI docs**: Interactive API docs at `/docs`.

## Tech Stack

- **Language**: Python 3.12+
- **Web framework**: FastAPI
- **Template engine**: Jinja2
- **Speech synthesis**: `edge-tts`
- **Audio merge**: `ffmpeg` (system binary)
- **ASGI server**: uvicorn
- **Validation/models**: Pydantic
- **Lint/Type/Test**: Ruff, mypy, pytest, pip-audit
- **Task runner**: mise (optional Makefile wrapper)
- **CI**: GitHub Actions (`.github/workflows/ci.yml`)

## Project Structure

```text
.
├── app/
│   ├── api/
│   │   └── routes_tts.py
│   ├── models/
│   │   └── tts_models.py
│   ├── services/
│   │   ├── tts_service.py
│   │   ├── audio_merge.py
│   │   └── job_store.py
│   ├── templates/
│   │   └── index.html
│   ├── utils/
│   │   ├── text_utils.py
│   │   └── file_utils.py
│   ├── config.py
│   └── main.py
├── docs/
│   └── public-repo-cicd-checklist.md
├── tests/
│   ├── test_api.py
│   └── test_text_utils.py
├── .github/workflows/
│   ├── ci.yml
│   └── docs-check.yml
├── Dockerfile
├── Makefile
├── pyproject.toml
└── .mise.toml
```

## Prerequisites

- Python 3.12+
- `ffmpeg` on PATH
- Docker (optional for container runs)
- mise (optional, for task execution)

## Quick Start (Docker)

```bash
git clone https://github.com/gmskazi/text-to-speech.git
cd text-to-speech
docker build -t tts .
docker run --rm -p 8000:8000 tts
```

Open:

- Web UI: `http://localhost:8000/`
- API docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

## Local Development (mise)

```bash
mise install
mise run run
```

This uses the Python version and venv setup from `.mise.toml`.

## Checks and Linting

Using mise:

```bash
mise run check
mise run check-docs
```

Using Makefile wrappers:

```bash
make
make all
make check
make check-docs
```

`make` and `make all` run both check targets sequentially.

`check` includes compile, lint, type checks, tests, dependency audit,
and Docker build smoke test.

## How to Use the Web App

1. Open `/`.
2. Set **Speaker Count** (`1` to `4`).
3. Set **Output Filename** (`.mp3` enforced and sanitized).
4. For single-speaker mode:
   - Choose language, voice, and speed.
   - Paste text.
5. For dialogue mode:
   - Choose language.
   - Configure each speaker voice/rate.
   - Enter dialogue lines.
6. Click **Generate MP3**.

Example dialogue input:

```text
A: こんにちは。
B: はい、どうしましたか？
```

Unlabeled lines continue with the previous speaker.

## API Usage

Base URL (local): `http://localhost:8000`

Endpoints:

- `GET /health`
- `GET /tts/voices`
- `POST /tts/single`
- `POST /tts/dialogue`
- `POST /tts/single/jobs`
- `POST /tts/dialogue/jobs`
- `GET /jobs/{job_id}`
- `GET /jobs/{job_id}/download`

Health check example:

```bash
curl -s http://localhost:8000/health
```

Expected response:

```json
{ "status": "ok" }
```

## Natural Mode and Dialogue Rules

Natural mode behavior:

- Web UI default: ON
- API default: OFF (unless `natural_mode: true` is passed)
- On no-audio conditions, the app retries with original text.

Dialogue parsing rules:

- Speaker labels: `A`, `B`, `C`, `D` (up to `speaker_count`)
- `:` and `：` are accepted
- Unlabeled lines continue previous speaker
- First unlabeled line defaults to `A`
- Empty lines are ignored

## CI and Security Notes

Current CI behavior:

- Runs on GitHub-hosted runner (`ubuntu-latest`)
- Path-filtered triggers (runs only on relevant code/workflow changes)
- Includes:
  - gitleaks
  - ruff
  - mypy
  - pytest
  - pip-audit
  - Docker build smoke test (conditional on Docker-related changes)

Dependency audit note:

- `CVE-2026-4539` for `pygments` is temporarily ignored in CI and
  local checks because no upstream fix version is published yet.
- Revisit and remove the ignore once a fixed release is available.

## Deployment Plan

For the current public-repo-safe deployment checklist, see:

- `docs/public-repo-cicd-checklist.md`

Current direction:

- keep CI on GitHub-hosted runners
- avoid self-hosted GitHub runners for public PR risk
- use local server build-and-deploy with Cloudflare Tunnel access

## Current Limitations

- Async job storage is in-memory (`app/services/job_store.py`)
  and is not persistent across restarts.
- No built-in auth/rate limiting for public API exposure.
- No durable object storage backend for long-lived artifacts.
