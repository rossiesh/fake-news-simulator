from fake_news_simulator.experiment_loader import load_experiment
from fake_news_simulator.experiment_schema import ExperimentConfig

from json import JSONDecodeError
from pydantic import ValidationError

import typer
from pathlib import Path

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
    load_experiment_or_exit(experiment_name)
    typer.echo(f"Experiment '{experiment_name}' loaded successfully")


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


'''
@app.command(name="init")
def init_experiment(experiment_name: str):
'''
