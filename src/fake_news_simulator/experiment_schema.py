from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
    ConfigDict
)
from enum import StrEnum
from typing import Annotated

MIN_VALUES_PER_LIST = 2
MAX_VALUES_PER_LIST = 3
MAX_VARYING_PARAMETERS = 2

ExperimentName = Annotated[str, Field(min_length=1, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")]
NodeCount = Annotated[int, Field(ge=500, le=7000)]
RunsPerScenario = Annotated[int, Field(ge=30, le=50)]
MaxStepsPerRun = Annotated[int, Field(ge=30, le=100)]
Probability = Annotated[float, Field(ge=0.0, le=1.0)]
Factor = Annotated[float, Field(gt=0.0, le=1.0)]


class ModerationType(StrEnum):
    NONE = "none"
    LABEL = "label"
    DOWNRANK = "downrank"
    DELETE = "delete"


class ModerationConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: ModerationType | list[ModerationType]
    threshold_activation_ratio: Factor | list[Factor]
    label_reduction_factor: Factor | list[Factor]
    downrank_reduction_factor: Factor | list[Factor]


class ModelConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    number_of_nodes: NodeCount
    influencer_ratio: Probability
    share_probability: Probability | list[Probability]
    recipient_ratio: Factor
    check_probability: Probability | list[Probability]
    moderation: ModerationConfig

    @model_validator(mode="after")
    def validate_variation_rules(self):
        varying_parameters = 0
        for key, value in flatten_dict(self.model_dump()).items():
            if isinstance(value, list):
                varying_parameters += 1
                if varying_parameters > MAX_VARYING_PARAMETERS:
                    raise ValueError(f"At most {MAX_VARYING_PARAMETERS} varying parameters are allowed")
                if len(value) < MIN_VALUES_PER_LIST:
                    raise ValueError(f"{key} must contain at least {MIN_VALUES_PER_LIST} values")
                if len(value) > MAX_VALUES_PER_LIST:
                    raise ValueError(f"{key} must contain at most {MAX_VALUES_PER_LIST} values")
                if len(set(value)) != len(value):
                    raise ValueError(f"{key} must contain only unique values")

        return self


class ExecutionConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    runs_per_scenario: RunsPerScenario
    max_steps_per_run: MaxStepsPerRun


class ExperimentConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: ExperimentName
    model: ModelConfig
    execution: ExecutionConfig

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return value.lower()

    @model_validator(mode="after")
    def validate_max_steps_per_run(self):
        if self.execution.max_steps_per_run > self.model.number_of_nodes:
            raise ValueError("max_steps_per_run must be less than or equal to number_of_nodes")

        return self


def flatten_dict(nested_dict: dict, parent_key: str = "") -> dict:
    flattened_dict = {}
    for key, value in nested_dict.items():
        new_key = f"{parent_key}.{key}" if parent_key else key
        if isinstance(value, dict):
            flattened_dict.update(flatten_dict(value, new_key))
        else:
            flattened_dict[new_key] = value

    return flattened_dict
