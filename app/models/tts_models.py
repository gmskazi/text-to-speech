from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from app.config import MAX_SPEAKERS


class SingleSpeakerRequest(BaseModel):
    text: str = Field(min_length=1)
    voice: str = Field(min_length=1)
    rate: int = Field(default=-20, ge=-80, le=80)
    output_name: str = Field(default="japanese_audio.mp3", min_length=1)


class SpeakerSetting(BaseModel):
    voice: str = Field(min_length=1)
    rate: int = Field(default=-20, ge=-80, le=80)


class DialogueRequest(BaseModel):
    speaker_count: int = Field(default=2, ge=1, le=MAX_SPEAKERS)
    dialogue_text: str = Field(min_length=1)
    speakers: dict[str, SpeakerSetting]
    output_name: str = Field(default="japanese_audio.mp3", min_length=1)

    @model_validator(mode="after")
    def validate_speaker_map(self) -> DialogueRequest:
        allowed_speakers = {chr(ord("A") + i) for i in range(self.speaker_count)}
        missing = allowed_speakers - self.speakers.keys()
        if missing:
            missing_text = ", ".join(sorted(missing))
            raise ValueError(f"Missing speaker settings for: {missing_text}")
        return self


class JobCreateResponse(BaseModel):
    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    output_name: str
    error: str | None = None
