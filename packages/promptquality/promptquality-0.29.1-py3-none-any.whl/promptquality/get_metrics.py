from typing import Any, Dict, Optional

from pydantic import UUID4

from promptquality.job_progress import job_progress
from promptquality.set_config import set_config
from promptquality.types.config import Config
from promptquality.types.run import GetMetricsRequest, PromptMetrics


def get_metrics(
    project_id: Optional[UUID4] = None,
    run_id: Optional[UUID4] = None,
    job_id: Optional[UUID4] = None,
    config: Optional[Config] = None,
) -> PromptMetrics:
    config = config or set_config()
    project_id = project_id or config.current_project_id
    run_id = run_id or config.current_run_id
    job_id = job_id or config.current_job_id
    if not project_id:
        raise ValueError("project_id must be provided")
    if not run_id:
        raise ValueError("run_id must be provided")
    if job_id:
        job_progress(job_id, config)
    metrics: Dict[str, Any] = dict()
    metrics_request = GetMetricsRequest(project_id=project_id, run_id=run_id)
    all_metrics = config.api_client.get_metrics(metrics_request)
    if all_metrics:
        for metric in all_metrics:
            if metric["key"] == "prompt_run":
                metrics.update(metrics.get("extra", dict()))
            else:
                metrics.update({metric["key"]: metric["value"]})
    return PromptMetrics.model_validate(metrics)
