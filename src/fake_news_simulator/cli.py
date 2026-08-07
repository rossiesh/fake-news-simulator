import json
import time

import typer
from pydantic import ValidationError

from fake_news_simulator.experiment_loader import ExperimentLoader
from fake_news_simulator.experiment_runner import ExperimentRunner
from fake_news_simulator.experiment_schema import ExperimentConfig
from fake_news_simulator.paths import EXPERIMENT_DIR
from fake_news_simulator.plot_generator import PlotGenerator
from fake_news_simulator.results_summarizer import ResultsSummarizer
from fake_news_simulator.results_writer import ResultsWriter
from fake_news_simulator.scenario_generator import ScenarioGenerator

app = typer.Typer()


@app.command(name="start")
def start_experiment(experiment_name: str):
    start_time = time.perf_counter()

    experiment = _load_experiment_or_exit(experiment_name)
    typer.echo(f"Experiment '{experiment_name}' loaded successfully")

    scenarios = ScenarioGenerator(experiment).generate()
    typer.echo(f"Generated {len(scenarios)} scenario(s)")
    simulation_results = ExperimentRunner.run(scenarios)
    scenario_summaries = ResultsSummarizer.summarize_scenarios(simulation_results)
    spread_summaries = ResultsSummarizer.summarize_spread_over_steps(simulation_results)

    result_directory = ResultsWriter().write(experiment=experiment, scenarios=scenarios,
                                             simulation_results=simulation_results,
                                             scenario_summaries=scenario_summaries, spread_summaries=spread_summaries)

    PlotGenerator().generate(result_directory, scenario_summaries, spread_summaries)

    duration = time.perf_counter() - start_time

    typer.echo(f"Simulation completed. Results written to {result_directory}")
    typer.echo(f"Took {duration:.2f} seconds")


@app.command(name="validate")
def validate_experiment(experiment_name: str):
    _load_experiment_or_exit(experiment_name)
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
            "number_of_nodes": 500,
            "influencer_ratio": 0.0,
            "share_probability": 0.0,
            "recipient_ratio": 0.1,
            "check_probability": 0.0,
            "moderation": {
                "type": "none",
                "threshold_activation_ratio": 0.1,
                "label_reduction_factor": 0.1,
                "downrank_reduction_factor": 0.1
            }
        },
        "execution": {
            "runs_per_scenario": 30,
            "max_steps_per_run": 30
        }
    }

    with path.open("w", encoding="utf-8") as file:
        json.dump(template, file, indent=2)

    typer.echo(f"Experiment '{experiment_name}' created. Path: {path}")


def _load_experiment_or_exit(experiment_name: str) -> ExperimentConfig:
    try:
        experiment = ExperimentLoader.load(experiment_name)
    except FileNotFoundError:
        typer.echo(f"Experiment '{experiment_name}' not found")
        raise typer.Exit(code=1)
    except json.JSONDecodeError:
        typer.echo(f"Experiment '{experiment_name}' contains invalid json")
        raise typer.Exit(code=1)
    except ValidationError as error:
        typer.echo(f"Experiment '{experiment_name}' is invalid")
        typer.echo(str(error))
        raise typer.Exit(code=1)
    return experiment
