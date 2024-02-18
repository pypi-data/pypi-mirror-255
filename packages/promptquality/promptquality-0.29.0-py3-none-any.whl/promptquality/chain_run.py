from typing import List, Optional, Union

from promptquality.constants.run import RunDefaults
from promptquality.constants.scorers import Scorers
from promptquality.helpers import (
    create_project,
    create_run,
    ingest_chain_rows,
    upload_custom_metrics,
)
from promptquality.job_progress import job_progress
from promptquality.set_config import set_config
from promptquality.types.chains.row import NodeRow
from promptquality.types.config import Config
from promptquality.types.custom_scorer import CustomScorer
from promptquality.types.registered_scorers import RegisteredScorer
from promptquality.types.run import RunTag
from promptquality.utils.scorer import bifurcate_scorers


def chain_run(
    rows: List[NodeRow],
    project_name: Optional[str] = None,
    run_name: Optional[str] = None,
    scorers: Optional[List[Union[Scorers, CustomScorer, RegisteredScorer, str]]] = None,
    run_tags: Optional[List[RunTag]] = None,
    silent: bool = False,
    config: Optional[Config] = None,
) -> None:
    config = config or set_config()
    project = create_project(project_name, config)
    run_id = create_run(
        project.id, run_name=run_name, task_type=RunDefaults.prompt_chain_task_type, run_tags=run_tags, config=config
    )
    galileo_scorers, custom_scorers, registered_scorers = bifurcate_scorers(scorers)
    ingestion_response = ingest_chain_rows(
        rows,
        project.id,
        run_id,
        scorers=galileo_scorers,
        registered_scorers=registered_scorers,
        config=config,
    )
    job_progress(ingestion_response.job_id, config=config)
    if not silent:
        print(f"🔭 View your prompt run on the Galileo console at: {config.current_run_url}")
    if custom_scorers:
        for scorer in custom_scorers:
            upload_custom_metrics(scorer, project_id=project.id, run_id=run_id, config=config)
