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
MAX_VALUES_PER_LIST = 4
MAX_VARYING_PARAMETERS = 2

ExperimentName = Annotated[str, Field(min_length=1, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")]
NodeCount = Annotated[int, Field(ge=1, le=10000)]
Probability = Annotated[float, Field(ge=0.0, le=1.0)]
PositiveInt = Annotated[int, Field(ge=1)]


class ModerationType(StrEnum):
    NONE = "none"
    LABEL = "label"
    DELETE = "delete"


class ModelConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    number_of_nodes: NodeCount | list[NodeCount]
    influencer_ratio: Probability | list[Probability]
    share_probability: Probability | list[Probability]
    check_probability: Probability | list[Probability]
    moderation_type: ModerationType | list[ModerationType]
    moderation_threshold: PositiveInt | list[PositiveInt]

    @model_validator(mode="after")
    def validate_moderation_threshold(self):
        if isinstance(self.number_of_nodes, list):
            number_of_nodes_values = self.number_of_nodes
        else:
            number_of_nodes_values = [self.number_of_nodes]

        if isinstance(self.moderation_threshold, list):
            moderation_threshold_values = self.moderation_threshold
        else:
            moderation_threshold_values = [self.moderation_threshold]

        min_number_of_nodes = min(number_of_nodes_values)
        max_moderation_threshold = max(moderation_threshold_values)

        if max_moderation_threshold >= min_number_of_nodes:
            raise ValueError("Moderation threshold must be less than the smallest number_of_nodes value")

        return self

    @model_validator(mode="after")
    def validate_variation_rules(self):
        varying_parameters = 0
        for key, value in self.model_dump().items():
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

    runs_per_scenario: PositiveInt
    max_steps_per_run: PositiveInt


class ExperimentConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: ExperimentName
    model: ModelConfig
    execution: ExecutionConfig

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return value.lower()
