# japanese-text-to-speech

Japanese text-to-speech app with:
- FastAPI (primary app)
- Flask (legacy app, kept during migration)
- `edge-tts` voice generation
- `ffmpeg` for multi-speaker merge
- Multi-language voice selection in the web UI

## Requirements

- Python 3.12+
- `ffmpeg` installed and available on PATH

## Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -e .[dev]
```

## Run

### FastAPI (primary)

```bash
uvicorn app.main:app --reload
```

- API docs: `http://127.0.0.1:8000/docs`
- Web form UI: `http://127.0.0.1:8000/`

### Flask (legacy)

```bash
python flaskapp/tts_flask.py
```

## API Endpoints (FastAPI)

- `GET /health`
- `GET /tts/voices`
- `POST /tts/single`
- `POST /tts/dialogue`
- `POST /tts/single/jobs`
- `POST /tts/dialogue/jobs`
- `GET /jobs/{job_id}`
- `GET /jobs/{job_id}/download`

See `docs/api-contract.md` for request/response examples.

## Scripts

```bash
python scripts/female.py
python scripts/female2.py
python scripts/malefemale.py
python scripts/malefemale2.py
```

## Quality Checks

```bash
ruff check .
mypy app tests
pytest
```

Run one test file:

```bash
pytest tests/test_api.py
```

Run one test function:

```bash
pytest tests/test_api.py::test_single_tts_endpoint
```
