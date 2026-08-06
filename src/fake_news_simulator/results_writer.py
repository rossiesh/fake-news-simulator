import csv
from datetime import datetime
from pathlib import Path

from fake_news_simulator.results_summarizer import SpreadOverStepsSummary, ScenarioSummary
from fake_news_simulator.scenario_generator import Scenario
from fake_news_simulator.simulation import SimulationResult


class ResultsWriter:
    def write(self, experiment_name: str, scenarios: list[Scenario], simulation_results: list[SimulationResult],
              scenario_summaries: list[ScenarioSummary], spread_summaries: list[SpreadOverStepsSummary]) -> Path:

        result_directory = self._create_result_directory(experiment_name)
        self._write_scenario_table(result_directory, scenarios)
        self._write_all_simulation_results(result_directory, simulation_results)
        self._write_scenario_summaries(result_directory, scenario_summaries)
        self._write_spread_summaries(result_directory, spread_summaries)

        return result_directory

    @staticmethod
    def _create_result_directory(experiment_name: str) -> Path:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        result_directory = Path("results") / f"{experiment_name}__{timestamp}"
        result_directory.mkdir(parents=True)

        return result_directory

    @staticmethod
    def _write_scenario_table(result_directory: Path, scenarios: list[Scenario]) -> None:
        path = result_directory / "scenario_table.csv"

        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["scenario_id", "number_of_nodes", "influencer_ratio",
                                                      "share_probability", "recipient_ratio", "check_probability",
                                                      "moderation_type", "moderation_threshold",
                                                      "moderation_label_reduction_factor",
                                                      "moderation_downrank_reduction_factor", "runs_per_scenario",
                                                      "max_steps_per_run"])
            writer.writeheader()

            for scenario in scenarios:
                writer.writerow({"scenario_id": scenario.scenario_id, "number_of_nodes": scenario.number_of_nodes,
                                 "influencer_ratio": scenario.influencer_ratio,
                                 "share_probability": scenario.share_probability,
                                 "recipient_ratio": scenario.recipient_ratio,
                                 "check_probability": scenario.check_probability,
                                 "moderation_type": scenario.moderation_type.value,
                                 "moderation_threshold": scenario.moderation_threshold,
                                 "moderation_label_reduction_factor": scenario.moderation_label_reduction_factor,
                                 "moderation_downrank_reduction_factor": scenario.moderation_downrank_reduction_factor,
                                 "runs_per_scenario": scenario.runs_per_scenario,
                                 "max_steps_per_run": scenario.max_steps_per_run})

    @staticmethod
    def _write_all_simulation_results(result_directory: Path, simulation_results: list[SimulationResult]) -> None:
        path = result_directory / "simulation_results.csv"

        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file,
                                    fieldnames=["scenario_id", "run_index", "reached_accounts", "total_shares", "steps",
                                                "start_node_is_influencer"])
            writer.writeheader()

            for result in simulation_results:
                writer.writerow({"scenario_id": result.scenario_id, "run_index": result.run_index,
                                 "reached_accounts": result.reached_accounts, "total_shares": result.total_shares,
                                 "steps": result.steps, "start_node_is_influencer": result.start_node_is_influencer})

    @staticmethod
    def _write_scenario_summaries(result_directory: Path, scenario_summaries: list[ScenarioSummary]) -> None:
        path = result_directory / "scenario_summaries.csv"

        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["scenario_id", "mean_reached_accounts", "std_reached_accounts",
                                                      "mean_total_shares", "std_total_shares", "mean_steps",
                                                      "std_steps"])
            writer.writeheader()

            for summary in scenario_summaries:
                writer.writerow(
                    {"scenario_id": summary.scenario_id, "mean_reached_accounts": summary.mean_reached_accounts,
                     "std_reached_accounts": summary.std_reached_accounts,
                     "mean_total_shares": summary.mean_total_shares, "std_total_shares": summary.std_total_shares,
                     "mean_steps": summary.mean_steps, "std_steps": summary.std_steps})

    @staticmethod
    def _write_spread_summaries(result_directory: Path, spread_summaries: list[SpreadOverStepsSummary]) -> None:
        path = result_directory / "spread_summaries.csv"

        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file,
                                    fieldnames=["scenario_id", "step", "mean_reached_accounts", "std_reached_accounts"])
            writer.writeheader()

            for summary in spread_summaries:
                writer.writerow({"scenario_id": summary.scenario_id, "step": summary.step,
                                 "mean_reached_accounts": summary.mean_reached_accounts,
                                 "std_reached_accounts": summary.std_reached_accounts})
