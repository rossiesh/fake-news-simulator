from pydantic import BaseModel, Field
from enum import StrEnum
from typing import Annotated

ExperimentName = Annotated[str, Field(min_length=1, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")]
NodeCount = Annotated[int, Field(ge=1, le=10000)]
Probability = Annotated[float, Field(ge=0.0, le=1.0)]
PositiveInt = Annotated[int, Field(ge=1)]


class ModerationType(StrEnum):
    NONE = "none"
    LABEL = "label"
    DELETE = "delete"


class ModelConfig(BaseModel):
    number_of_nodes: NodeCount | list[NodeCount]
    influencer_ratio: Probability | list[Probability]
    share_probability: Probability | list[Probability]
    check_probability: Probability | list[Probability]
    moderation_type: ModerationType | list[ModerationType]
    moderation_threshold: PositiveInt | list[PositiveInt]


class ExecutionConfig(BaseModel):
    runs_per_scenario: PositiveInt | list[PositiveInt]
    max_steps_per_run: PositiveInt | list[PositiveInt]


class ExperimentConfig(BaseModel):
    name: ExperimentName
    model: ModelConfig
    execution: ExecutionConfig
