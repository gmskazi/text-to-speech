# FastAPI Migration Checklist

This checklist tracks the migration of the current text-to-speech app to FastAPI.

## 1) Project Setup
- [x] Add FastAPI runtime dependencies (`fastapi`, `uvicorn`, `pydantic`).
- [x] Add dev dependencies (`pytest`, `ruff`, `mypy`).
- [x] Define project scripts/commands for run, lint, type check, and tests.
- [x] Confirm Python runtime target is 3.12+.

## 2) Repository Structure
- [x] Create `app/` package for the new FastAPI implementation.
- [x] Add `app/main.py` as the ASGI entrypoint.
- [x] Add `app/api/routes_tts.py` for TTS HTTP endpoints.
- [x] Add `app/services/` for generation and merge logic.
- [x] Add `app/models/` for request/response models.
- [x] Remove legacy web implementation after FastAPI cutover.

## 3) Shared Core Logic Extraction
- [x] Move filename sanitization into a utility helper.
- [x] Move speaking-rate normalization into a utility helper.
- [x] Move dialogue parsing into a pure service function.
- [x] Move single-speaker generation orchestration into services.
- [x] Move multi-speaker generation and merge orchestration into services.

## 4) API Design and Endpoints
- [x] Implement `POST /tts/single`.
- [x] Implement `POST /tts/dialogue`.
- [x] Implement `GET /health`.
- [x] Return downloadable MP3 files with correct media type and filename.
- [x] Provide explicit 4xx responses for validation errors.

## 5) Validation and Models
- [x] Define Pydantic models for single-speaker requests.
- [x] Define Pydantic models for multi-speaker requests.
- [x] Validate speaker prefixes (`A`, `B`, `C`, `D`) by selected speaker count.
- [x] Validate speaking-rate bounds and defaults.
- [x] Validate output filename and `.mp3` extension behavior.

## 6) Audio Pipeline and Runtime Behavior
- [x] Verify `edge_tts` generation flow in async service methods.
- [x] Verify `ffmpeg` merge execution path and command safety.
- [x] Ensure quote-safe concat list writing for ffmpeg.
- [x] Preserve temporary file cleanup behavior.
- [x] Surface actionable errors when ffmpeg is unavailable.

## 7) Frontend Integration Plan
- [x] Keep current form-based UX initially (server-rendered page).
- [x] Wire form submissions to FastAPI endpoints.
- [x] Preserve current form field names where practical.
- [x] Keep desktop/mobile behavior equivalent to current experience.

## 8) Testing Plan
- [x] Add unit tests for rate normalization helper.
- [x] Add unit tests for dialogue parsing success and failure cases.
- [x] Add unit tests for filename sanitization.
- [x] Add API tests for `/tts/single`.
- [x] Add API tests for `/tts/dialogue`.
- [x] Add negative-path tests for malformed dialogue and invalid speakers.

## 9) Quality and Tooling
- [x] Configure Ruff for linting and formatting rules.
- [x] Configure mypy (or pyright) for static type checks.
- [x] Ensure all new functions include type hints and return annotations.
- [x] Add lightweight pre-commit hooks (optional).

## 10) Documentation Work
- [x] Update root `README.md` with FastAPI run commands.
- [x] Document migration status and rollback approach.
- [x] Document ffmpeg dependency and troubleshooting.
- [x] Document common edge-tts voice options and rate behavior.

## 11) Optional Scaling Phase
- [x] Add `BackgroundTasks` for non-blocking generation responses.
- [x] Add job IDs and status endpoint (`GET /jobs/{id}`) if needed.
- [x] Evaluate Redis + worker queue only if request volume requires it.

## 12) Acceptance Criteria
- [x] Single-speaker generation works end-to-end.
- [x] Multi-speaker generation and merge works end-to-end.
- [x] Validation errors are clear and structured.
- [x] Tests pass locally.
- [x] Lint and type checks pass locally.
- [x] Documentation is up to date.

## Status Tracking
- Owner: @aitonakajima
- Start date: 2026-03-25
- Target date: 2026-03-25
- Current phase: Completed
