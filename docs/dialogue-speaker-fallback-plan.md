# Dialogue Speaker Fallback Plan

## Goal
Make multi-speaker dialogue parsing more forgiving by reusing the last active speaker when a line has no valid speaker prefix.

## Behavior
- If a line starts with `A:`, `B:`, `C:`, or `D:` (within `speaker_count`), use that speaker.
- If a line has no valid speaker prefix, continue with the last applied speaker.
- If the first non-empty line has no valid prefix, auto-assign speaker `A`.

## Checklist
- [x] Update parser logic in `app/utils/text_utils.py`.
- [x] Keep existing safety checks for empty text and missing speaker settings.
- [x] Update UI helper text in `app/templates/index.html`.
- [x] Update API contract docs in `docs/api-contract.md`.
- [x] Add parser tests for unlabeled continuation/default-to-A behavior.

## Verification
- [x] `ruff check .`
- [x] `mypy app tests`
- [x] `pytest -q`
