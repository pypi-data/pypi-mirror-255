from enum import Enum


class JobStatus(str, Enum):
    unstarted = "unstarted"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"

    @staticmethod
    def is_incomplete(status: "JobStatus") -> bool:
        return status in [JobStatus.unstarted, JobStatus.in_progress]
