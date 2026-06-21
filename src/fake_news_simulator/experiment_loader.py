from pathlib import Path
from fake_news_simulator.experiment_schema import ExperimentConfig
import json

EXPERIMENT_DIR = Path("experiments")


def load_experiment(experiment_name: str) -> ExperimentConfig:
    path = EXPERIMENT_DIR / f"{experiment_name}.json"

    with path.open("r", encoding="utf-8") as file:
        raw_data = json.load(file)

    return ExperimentConfig.model_validate(raw_data)
