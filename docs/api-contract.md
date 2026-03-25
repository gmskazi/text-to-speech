# API Contract Draft

## Base
- Content type: `application/json` for requests.
- Successful audio response type: `audio/mpeg`.

## Endpoints

### `GET /health`
Checks service health.

Example response:
```json
{
  "status": "ok"
}
```

### `GET /tts/voices`
List curated voices for a language.

Query parameters:
- `language` (optional): language code such as `ja-JP`, `en-US`, `es-ES`.

Example response:
```json
{
  "language": "en-US",
  "language_label": "English (US)",
  "voices": [
    {"label": "Jenny (Female)", "value": "en-US-JennyNeural"},
    {"label": "Guy (Male)", "value": "en-US-GuyNeural"}
  ]
}
```

### `POST /tts/single`
Generate one MP3 from a single speaker.

Request body:
```json
{
  "text": "こんにちは。",
  "voice": "ja-JP-NanamiNeural",
  "rate": 0,
  "output_name": "single_output.mp3"
}
```

Notes:
- `rate` should be clamped to supported bounds (for example `-80` to `80`).
- `output_name` should be sanitized to filename only and end with `.mp3`.

Success response:
- HTTP 200
- Body: binary MP3 (`audio/mpeg`)

### `POST /tts/single/jobs`
Queue a single-speaker generation job.

Request body: same as `POST /tts/single`.

Success response:
```json
{
  "job_id": "9dcb3f8f8bbf4b9898f02658d34ec06f",
  "status": "queued"
}
```

### `POST /tts/dialogue/jobs`
Queue a multi-speaker generation job.

Request body: same as `POST /tts/dialogue`.

Success response:
```json
{
  "job_id": "d1f4dececf4740cc9fd91dd21682bb2c",
  "status": "queued"
}
```

### `GET /jobs/{job_id}`
Get queued/running/done/failed job state.

Success response:
```json
{
  "job_id": "9dcb3f8f8bbf4b9898f02658d34ec06f",
  "status": "done",
  "output_name": "dialogue_output.mp3",
  "error": null
}
```

### `GET /jobs/{job_id}/download`
Download the rendered MP3 once the job is complete.

Responses:
- HTTP 200 with `audio/mpeg` body when ready
- HTTP 409 if result is not ready
- HTTP 404 for unknown job ID
- Content-Disposition: attachment with final filename

### `POST /tts/dialogue`
Generate one MP3 from multi-speaker dialogue.

Request body:
```json
{
  "speaker_count": 2,
  "dialogue_text": "A: すみません。\nB: はい。",
  "speakers": {
    "A": {"voice": "ja-JP-NanamiNeural", "rate": 0},
    "B": {"voice": "ja-JP-KeitaNeural", "rate": 0}
  },
  "output_name": "dialogue_output.mp3"
}
```

Validation rules:
- `speaker_count` allowed range: `1..4`.
- Dialogue lines must include speaker prefix and text (`A: ...`).
- Allowed speaker prefixes are constrained by `speaker_count`.
- Empty lines are ignored; empty speaker text is invalid.

Success response:
- HTTP 200
- Body: binary MP3 (`audio/mpeg`)

## Error Model (Draft)
```json
{
  "error": {
    "code": "invalid_dialogue",
    "message": "Invalid speaker 'C'. Allowed speakers: A, B"
  }
}
```

Suggested common error codes:
- `validation_error`
- `invalid_dialogue`
- `ffmpeg_not_found`
- `audio_merge_failed`
- `tts_generation_failed`

## Backward Compatibility Notes
- Keep existing voice IDs where possible.
- Keep output naming behavior compatible with current Flask app.
- Preserve speaking-rate default (`0`) unless explicitly changed.
- Keep Flask app available as a migration fallback.
