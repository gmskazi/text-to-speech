from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from threading import Lock
from uuid import uuid4


@dataclass
class JobRecord:
    job_id: str
    status: str
    output_name: str
    file_path: str | None = None
    temp_dir: str | None = None
    error: str | None = None
    updated_at: datetime = datetime.now(UTC)


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, JobRecord] = {}
        self._lock = Lock()

    def create_job(self, output_name: str) -> JobRecord:
        job_id = uuid4().hex
        record = JobRecord(job_id=job_id, status="queued", output_name=output_name)
        with self._lock:
            self._jobs[job_id] = record
        return record

    def get(self, job_id: str) -> JobRecord | None:
        with self._lock:
            return self._jobs.get(job_id)

    def update(
        self,
        job_id: str,
        *,
        status: str,
        file_path: str | None = None,
        temp_dir: str | None = None,
        error: str | None = None,
    ) -> JobRecord:
        with self._lock:
            record = self._jobs[job_id]
            record.status = status
            record.file_path = file_path
            record.temp_dir = temp_dir
            record.error = error
            record.updated_at = datetime.now(UTC)
            return record


job_store = JobStore()
