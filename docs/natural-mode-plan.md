# Natural Mode Implementation Plan

## Goal
Make TTS output sound more natural and less robotic, with Natural Mode enabled by default for web users.

## Default Behavior
- Web form default: `natural_mode = true`
- API default: `natural_mode = false` (backward compatible)

## Progress Tracker

### 1) Model and request updates
- [x] Add `natural_mode: bool = False` to `SingleSpeakerRequest`
- [x] Add `natural_mode: bool = False` to `DialogueRequest`

### 2) Speech normalization helper
- [x] Add `normalize_for_speech(text: str, language: str) -> str` in `app/utils/text_utils.py`
- [x] Keep V1 normalization conservative (whitespace, punctuation smoothing)
- [x] Add language-aware handling for `en-*` and `ja-*` only

### 3) Backend integration
- [x] Web form path (`app/main.py`): apply normalization when Natural Mode is on
- [x] API path (`app/api/routes_tts.py`): apply normalization only when `natural_mode=true`
- [x] Keep existing output behavior unchanged when Natural Mode is off

### 4) Web UI integration
- [x] Add Natural Mode toggle to single-speaker section
- [x] Add Natural Mode toggle to multi-speaker section
- [x] Set web default to ON
- [x] Add helper text: "Improves conversational rhythm and pacing."

### 5) Rate tuning in Natural Mode
- [x] Apply mild single-speaker default bias only when user left defaults unchanged
- [x] Apply subtle per-speaker dialogue variation only when user left defaults unchanged
- [x] Do not override explicit user-provided rates

### 6) Tests
- [x] Unit tests for normalization helper
- [x] API tests for single mode with `natural_mode=true`
- [x] API tests for dialogue mode with `natural_mode=true`
- [x] Regression coverage for `natural_mode=false` or omitted field

### 7) Verification checklist
- [x] `ruff check .`
- [x] `mypy app tests`
- [x] `pytest -q`
- [x] Manual A/B check: same content with Natural Mode ON vs OFF
- [x] Manual check: Japanese text remains natural and semantically intact

## Notes
- Keep implementation SSML-free for V1 to reduce complexity.
- If quality issues appear, switch web default OFF quickly while keeping feature available.
- Manual smoke result: Natural Mode behavior is confirmed for Japanese samples. English A/B may not always produce binary-different output on short input, but output generation is stable in both modes.
