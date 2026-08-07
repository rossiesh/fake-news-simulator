import matplotlib.pyplot as plotter
from pathlib import Path

from fake_news_simulator.results_summarizer import ScenarioSummary, SpreadOverStepsSummary


class PlotGenerator:
    def generate(self, result_directory: Path, scenario_summaries: list[ScenarioSummary],
                 spread_summaries: list[SpreadOverStepsSummary]) -> None:
        self._generate_reached_accounts_bar_chart(result_directory, scenario_summaries)
        self._generate_total_shares_bar_chart(result_directory, scenario_summaries)
        self._generate_spread_over_steps_chart(result_directory, spread_summaries)

    @staticmethod
    def _generate_reached_accounts_bar_chart(result_directory: Path, scenario_summaries: list[ScenarioSummary]) -> None:
        path = result_directory / "05_reached_accounts.png"

        scenario_ids = []
        mean_reached_accounts = []
        std_reached_accounts = []

        for summary in scenario_summaries:
            scenario_ids.append(summary.scenario_id)
            mean_reached_accounts.append(summary.mean_reached_accounts)
            std_reached_accounts.append(summary.std_reached_accounts)

        plotter.figure(figsize=(10, 6), dpi=200, facecolor="white")
        plotter.title("reached accounts per scenario")
        plotter.xlabel("scenario")
        plotter.ylabel("mean reached accounts")

        plotter.bar(scenario_ids, mean_reached_accounts, yerr=std_reached_accounts, capsize=5,
                    color=["#620f67", "#f0882b"], error_kw={"linewidth": 1.5, "ecolor": "gray"})
        plotter.ylim(bottom=0)
        plotter.tight_layout()

        plotter.savefig(path)
        plotter.close()

    @staticmethod
    def _generate_total_shares_bar_chart(result_directory: Path, scenario_summaries: list[ScenarioSummary]) -> None:
        path = result_directory / "06_total_shares.png"

        scenario_ids = []
        mean_total_shares = []
        std_total_shares = []

        for summary in scenario_summaries:
            scenario_ids.append(summary.scenario_id)
            mean_total_shares.append(summary.mean_total_shares)
            std_total_shares.append(summary.std_total_shares)

        plotter.figure(figsize=(10, 6), dpi=200, facecolor="white")
        plotter.title("total shares per scenario")
        plotter.xlabel("scenario")
        plotter.ylabel("mean total shares")

        plotter.bar(scenario_ids, mean_total_shares, yerr=std_total_shares, capsize=5,
                    color=["#620f67", "#f0882b"], error_kw={"linewidth": 1.5, "ecolor": "gray"})
        plotter.ylim(bottom=0)
        plotter.tight_layout()

        plotter.savefig(path)
        plotter.close()

    @staticmethod
    def _generate_spread_over_steps_chart(result_directory: Path,
                                          spread_summaries: list[SpreadOverStepsSummary]) -> None:
        path = result_directory / "07_spread_over_steps.png"

        colors = ["#620f67", "#ddff01", "#1749BF", "#f0882b", "#2CE2BE", "#BF1717", "#D4E60E", "#CA0D98", "#3A3A3A"]

        scenario_ids = set()
        for summary in spread_summaries:
            scenario_ids.add(summary.scenario_id)
        scenario_ids = sorted(scenario_ids)

        plotter.figure(figsize=(10, 6), dpi=200, facecolor="white")

        for index, scenario_id in enumerate(scenario_ids):
            steps = []
            mean_reached_accounts = []
            for summary in spread_summaries:
                if summary.scenario_id == scenario_id:
                    steps.append(summary.step)
                    mean_reached_accounts.append(summary.mean_reached_accounts)

            plotter.plot(steps, mean_reached_accounts, marker="o", markerfacecolor="gray",
                         label=f"scenario {scenario_id}", color=colors[index % len(colors)])

        plotter.title("spread over steps")
        plotter.xlabel("step")
        plotter.ylabel("mean reached accounts")
        plotter.ylim(bottom=0)
        plotter.legend()
        plotter.tight_layout()

        plotter.savefig(path)
        plotter.close()
