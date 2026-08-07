from dataclasses import dataclass
from itertools import product
from typing import Any

from fake_news_simulator.experiment_schema import ExperimentConfig, ModerationType


@dataclass(frozen=True)
class Scenario:
    scenario_id: str

    number_of_nodes: int
    influencer_ratio: float
    share_probability: float
    recipient_ratio: float
    check_probability: float

    moderation_type: ModerationType
    moderation_threshold_activation_ratio: float
    moderation_label_reduction_factor: float
    moderation_downrank_reduction_factor: float

    runs_per_scenario: int
    max_steps_per_run: int


class ScenarioGenerator:
    def __init__(self, experiment: ExperimentConfig):
        self.experiment = experiment

    def generate(self) -> list[Scenario]:
        parameter_values = {
            "share_probability": self._convert_to_list(self.experiment.model.share_probability),
            "check_probability": self._convert_to_list(self.experiment.model.check_probability),
            "moderation_type": self._convert_to_list(self.experiment.model.moderation.type),
            "moderation_threshold_activation_ratio": self._convert_to_list(
                self.experiment.model.moderation.threshold_activation_ratio),
            "moderation_label_reduction_factor": self._convert_to_list(
                self.experiment.model.moderation.label_reduction_factor),
            "moderation_downrank_reduction_factor": self._convert_to_list(
                self.experiment.model.moderation.downrank_reduction_factor),
        }

        scenarios = []

        for index, combination in enumerate(product(*parameter_values.values()), start=1):
            values = dict(zip(parameter_values.keys(), combination))
            scenarios.append(self._create_scenario(index, values))

        return scenarios

    @staticmethod
    def _convert_to_list(value: Any) -> list[Any]:
        if isinstance(value, list):
            return value
        return [value]

    def _create_scenario(self, index: int, values: dict) -> Scenario:
        return Scenario(
            scenario_id=f"{index:02}",
            number_of_nodes=self.experiment.model.number_of_nodes,
            influencer_ratio=self.experiment.model.influencer_ratio,
            share_probability=values["share_probability"],
            recipient_ratio=self.experiment.model.recipient_ratio,
            check_probability=values["check_probability"],
            moderation_type=values["moderation_type"],
            moderation_threshold_activation_ratio=values["moderation_threshold_activation_ratio"],
            moderation_label_reduction_factor=values["moderation_label_reduction_factor"],
            moderation_downrank_reduction_factor=values["moderation_downrank_reduction_factor"],
            runs_per_scenario=self.experiment.execution.runs_per_scenario,
            max_steps_per_run=self.experiment.execution.max_steps_per_run,
        )
