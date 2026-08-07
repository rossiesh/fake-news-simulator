import json
import time
from json import JSONDecodeError
from pathlib import Path

import typer
from pydantic import ValidationError

from fake_news_simulator.experiment_loader import load_experiment
from fake_news_simulator.experiment_runner import ExperimentRunner
from fake_news_simulator.experiment_schema import ExperimentConfig
from fake_news_simulator.plot_generator import PlotGenerator
from fake_news_simulator.results_summarizer import ResultsSummarizer
from fake_news_simulator.results_writer import ResultsWriter
from fake_news_simulator.scenario_generator import ScenarioGenerator

app = typer.Typer()

EXPERIMENT_DIR = Path("experiments")


def load_experiment_or_exit(experiment_name: str) -> ExperimentConfig:
    try:
        experiment = load_experiment(experiment_name)
    except FileNotFoundError:
        typer.echo(f"Experiment '{experiment_name}' not found")
        raise typer.Exit(code=1)
    except JSONDecodeError:
        typer.echo(f"Experiment '{experiment_name}' contains invalid json")
        raise typer.Exit(code=1)
    except ValidationError as error:
        typer.echo(f"Experiment '{experiment_name}' is invalid")
        typer.echo(str(error))
        raise typer.Exit(code=1)
    return experiment


@app.command(name="start")
def start_experiment(experiment_name: str):
    start_time = time.perf_counter()

    experiment = load_experiment_or_exit(experiment_name)
    typer.echo(f"Experiment '{experiment_name}' loaded successfully")

    scenarios = ScenarioGenerator(experiment).generate()
    typer.echo(f"Generated {len(scenarios)} scenario(s)")
    simulation_results = ExperimentRunner.run(scenarios)
    scenario_summaries = ResultsSummarizer.summarize_scenarios(simulation_results)
    spread_summaries = ResultsSummarizer.summarize_spread_over_steps(simulation_results)

    result_directory = ResultsWriter().write(experiment_name=experiment.name, scenarios=scenarios,
                                             simulation_results=simulation_results,
                                             scenario_summaries=scenario_summaries, spread_summaries=spread_summaries)

    PlotGenerator().generate(result_directory, scenario_summaries, spread_summaries)

    duration = time.perf_counter() - start_time

    typer.echo(f"Simulation completed. Results written to {result_directory}")
    typer.echo(f"Took {duration:.2f} seconds")


@app.command(name="validate")
def validate_experiment(experiment_name: str):
    load_experiment_or_exit(experiment_name)
    typer.echo(f"Experiment '{experiment_name}' is valid")


@app.command(name="list")
def list_experiment():
    index = 1
    for path in EXPERIMENT_DIR.glob("*.json"):
        typer.echo(f"{index}: '{path.stem}'")
        index += 1


@app.command(name="init")
def init_experiment(experiment_name: str):
    path = EXPERIMENT_DIR / f"{experiment_name}.json"

    if path.exists():
        typer.echo(f"Experiment '{experiment_name}' already exists")
        raise typer.Exit(code=1)

    EXPERIMENT_DIR.mkdir(exist_ok=True)

    template = {
        "name": experiment_name,
        "model": {
            "number_of_nodes": 0,
            "influencer_ratio": 0,
            "share_probability": 0.0,
            "recipient_ratio": 0.0,
            "check_probability": 0.0,
            "moderation": {
                "type": "none",
                "threshold": 0,
                "label_reduction_factor": 0.0,
                "downrank_reduction_factor": 0.0
            }
        },
        "execution": {
            "runs_per_scenario": 0,
            "max_steps_per_run": 0
        }
    }

    with path.open("w", encoding="utf-8") as file:
        json.dump(template, file, indent=2)

    typer.echo(f"Experiment '{experiment_name}' created. Path: {path}")
