from typing import Dict
from datetime import datetime
from enum import Enum

class IndexJobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class IndexJob:
    def __init__(self, job_id: str, path: str, incremental: bool):
        self.job_id = job_id
        self.path = path
        self.incremental = incremental
        self.status = IndexJobStatus.PENDING
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.error: str | None = None

    def update(self, status: IndexJobStatus, error: str | None = None):
        self.status = status
        self.updated_at = datetime.utcnow()
        self.error = error

class AppState:
    def __init__(self):
        self.index_jobs: Dict[str, IndexJob] = {}

state = AppState()
