# FastAPI Architecture (Target)

## Goals
- Keep behavior equivalent to current Flask app.
- Isolate core TTS logic from web framework code.
- Support clean validation and easier testability.
- Provide a clear path to background-job scaling.
- Keep Flask fallback runnable during migration and rollback windows.

## Proposed Layout
```text
app/
  main.py
  api/
    routes_tts.py
  models/
    tts_models.py
  services/
    tts_service.py
    audio_merge.py
  utils/
    text_utils.py
    file_utils.py
```

## Request Flow
1. Client submits single-speaker or dialogue request.
2. FastAPI route validates payload with Pydantic.
3. Route calls service-layer orchestration.
4. Service generates one or more MP3 parts via `edge_tts`.
5. Multi-speaker flow merges parts using `ffmpeg`.
6. Route returns MP3 file response (download).

## Responsibilities

### `app/main.py`
- App initialization.
- Router registration.
- Global exception handlers and health check wiring.

### `app/api/routes_tts.py`
- HTTP request handling.
- Input/output model binding.
- Translate service errors into HTTP responses.

### `app/models/tts_models.py`
- Request and response schemas.
- Constraints for speaker count, rate values, and output names.

### `app/services/tts_service.py`
- Core orchestration for single and multi-speaker generation.
- Temporary workspace handling.
- Deterministic part ordering.

### `app/services/audio_merge.py`
- `ffmpeg` existence checks.
- Safe concat-file writing.
- Merge execution and subprocess error handling.

### `app/utils/*`
- Parsing and normalization helpers.
- Filename sanitization.

## Error Strategy
- Validation failures: HTTP 422/400 with clear details.
- Missing ffmpeg: HTTP 500 with actionable setup guidance.
- TTS/provider failures: HTTP 502/500 with traceable error metadata.

## Runtime Notes
- Keep Python 3.12+.
- Keep `edge_tts` and external `ffmpeg` dependency.
- Start with sync download responses; add background jobs only when needed.

## Scaling Path
- Phase 1: direct request -> response file download.
- Phase 2: FastAPI `BackgroundTasks` for larger jobs.
- Phase 3: external queue (Redis + worker) for high concurrency.
