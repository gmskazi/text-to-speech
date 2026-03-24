# AGENTS.md

## Scope
- Applies to the entire repository `japanese-text-to-speech/`.
- Primary web app: `app/main.py` (FastAPI).
- Legacy web app: `flaskapp/tts_flask.py`.
- Script entrypoints: `scripts/female.py`, `scripts/female2.py`, `scripts/malefemale.py`, `scripts/malefemale2.py`.

## Repository Snapshot
- Language: Python.
- Tool version hint: Python 3.12 (`.mise.toml`).
- Runtime deps in active code: `fastapi`, `flask`, `edge-tts`, `ffmpeg` (external binary).
- Tooling in repo: `pytest`, `ruff`, `mypy`, `pre-commit`, `pyproject.toml`.

## Environment Setup
- Use local venv at `.venv/`.
- Create + activate if missing:
```bash
python3.12 -m venv .venv
source .venv/bin/activate
```
- Install runtime deps:
```bash
pip install -e .
pip install -e .[dev]
```

## Run Commands
- Start web app:
```bash
uvicorn app.main:app --reload
```
- Start legacy Flask app:
```bash
python flaskapp/tts_flask.py
```
- Run sample generators:
```bash
python scripts/female.py
python scripts/female2.py
python scripts/malefemale.py
python scripts/malefemale2.py
```

## Build / Lint / Test

### Build / Smoke (works with current repo)
- Compile all Python files:
```bash
python -m compileall .
```
- Compile one file (fast check):
```bash
python -m py_compile app/main.py
```

### Lint / Format (recommended dev tooling)
- Install optional dev tools:
```bash
pip install ruff black mypy pytest
```
- Lint whole repo:
```bash
ruff check .
```
- Lint one file:
```bash
ruff check app/main.py
```
- Format whole repo:
```bash
black .
```
- Format one file:
```bash
ruff format app/main.py
```
- Type check one file:
```bash
mypy app/main.py
```

### Tests
- Run all tests:
```bash
pytest -q
```
- Run one test file:
```bash
pytest -q tests/test_api.py
```
- Run one test function (preferred for agents):
```bash
pytest -q tests/test_api.py::test_single_tts_endpoint
```
- Run by keyword:
```bash
pytest -q -k parse_dialogue
```

## Manual Verification (important in this codebase)
- Confirm FastAPI `/` renders and form submits.
- Confirm FastAPI docs `/docs` loads.
- Confirm single-speaker MP3 download works.
- Confirm multi-speaker MP3 merge works (requires `ffmpeg`).
- Confirm malformed dialogue returns structured API errors.

## Code Style Guidelines

### Imports
- If used, keep `from __future__ import annotations` first.
- Group imports: standard library, third-party, local.
- Use explicit imports; avoid wildcard imports.
- Keep one import per line unless existing file style differs.

### Formatting
- Follow PEP 8 conventions.
- Use 4-space indentation.
- Target readable line lengths (~88 chars).
- Preserve spacing between logical blocks.
- Prefer extracting helpers over deeply nested route logic.

### Types
- Add type hints for new or edited functions.
- Always annotate return types.
- Keep type style consistent with the edited file.
- Prefer explicit container element types.
- Validate external inputs (form fields, parsed text) early.

### Naming
- `snake_case`: variables, functions, helpers.
- `UPPER_SNAKE_CASE`: constants.
- Use descriptive names (`speaker_settings`, `parsed_lines`, `output_files`).
- Keep route handlers verb-oriented (`index`, `generate_audio`).

### Error Handling
- Catch specific exceptions where possible.
- In Flask routes, convert recoverable errors to `flash(..., "error")` + redirect.
- Keep subprocess calls strict with `check=True`.
- Include stderr context for ffmpeg failures when available.
- Raise clear `ValueError` messages for user input issues.

### Async + Subprocess
- Keep TTS generation in async helpers.
- Use `asyncio.run(...)` only at sync boundaries.
- Keep ffmpeg concat behavior deterministic.
- Preserve quote-safe handling for concat list file entries.

### Paths + Files
- Sanitize output names via `Path(...).name`.
- Use temp directories for generated artifacts.
- Use explicit UTF-8 when writing text files.
- Preserve current cleanup/error semantics when editing generation flow.

### FastAPI / UI Conventions
- Keep form field names stable unless migration is intentional.
- Keep route functions orchestration-focused; push logic to helpers.
- Keep Pydantic models as source of API input constraints.
- Maintain desktop + mobile behavior when editing `app/templates/index.html`.

## Agentic Workflow Guidance
- Make minimal, targeted edits.
- Avoid introducing new dependencies unless task-critical.
- Prefer adding tests around pure helpers first (`parse_dialogue`, `to_rate_str`).
- Re-run the smallest relevant check before finishing (single-file compile/lint/test).

## Cursor / Copilot Rules
- `.cursor/rules/`: not found.
- `.cursorrules`: not found.
- `.github/copilot-instructions.md`: not found.
- No editor-specific instruction files are currently active.

## Known Repo Caveat
- `ffmpeg` must be installed on system PATH for multi-speaker merge endpoints.
- Keep Flask app available as fallback while FastAPI evolves.
