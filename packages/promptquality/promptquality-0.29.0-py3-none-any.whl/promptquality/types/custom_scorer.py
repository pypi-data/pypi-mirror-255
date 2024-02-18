from typing import Callable, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from promptquality.types.rows import PromptRow

CustomMetricType = Union[float, int, bool, str, None]


class CustomScorer(BaseModel):
    name: str
    scorer_fn: Callable[[PromptRow], CustomMetricType] = Field(validation_alias="executor")
    aggregator_fn: Optional[Callable[[List[CustomMetricType], List[int]], Dict[str, CustomMetricType]]] = Field(
        default=None, validation_alias="aggregator"
    )

    model_config = ConfigDict(populate_by_name=True)
