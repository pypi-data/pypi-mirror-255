from enum import Enum
from types import SimpleNamespace

RunDefaults = SimpleNamespace(
    project_type="prompt_evaluation",
    job_name="prompt_run",
    prompt_evaluation_task_type=7,
    prompt_chain_task_type=12,
)


class TagType(str, Enum):
    GENERIC = "generic"
    RAG = "rag"
