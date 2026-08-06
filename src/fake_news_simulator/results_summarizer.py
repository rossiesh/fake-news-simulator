from dataclasses import dataclass
from statistics import mean, stdev

from fake_news_simulator.simulation import SimulationResult


@dataclass(frozen=True)
class ScenarioSummary:
    scenario_id: str

    mean_reached_accounts: float
    std_reached_accounts: float

    mean_total_shares: float
    std_total_shares: float


@dataclass(frozen=True)
class SpreadOverStepsSummary:
    scenario_id: str
    step: int

    mean_reached_accounts: float
    std_reached_accounts: float


class ResultsSummarizer:

    @staticmethod
    def summarize_scenarios(simulation_results: list[SimulationResult]) -> list[ScenarioSummary]:

        scenario_ids = set()
        for result in simulation_results:
            scenario_ids.add(result.scenario_id)
        scenario_ids = sorted(scenario_ids)

        scenario_summaries = []

        for scenario_id in scenario_ids:
            reached_accounts_values = []
            total_shares_values = []

            for result in simulation_results:
                if result.scenario_id == scenario_id:
                    reached_accounts_values.append(result.reached_accounts)
                    total_shares_values.append(result.total_shares)

            scenario_summaries.append(ScenarioSummary(scenario_id=scenario_id,
                                                      mean_reached_accounts=mean(reached_accounts_values),
                                                      std_reached_accounts=stdev(reached_accounts_values),
                                                      mean_total_shares=mean(total_shares_values),
                                                      std_total_shares=stdev(total_shares_values)))

        return scenario_summaries

    @staticmethod
    def summarize_spread_over_steps(simulation_results: list[SimulationResult]) -> list[SpreadOverStepsSummary]:
        scenario_ids = set()
        for result in simulation_results:
            scenario_ids.add(result.scenario_id)
        scenario_ids = sorted(scenario_ids)

        spread_summaries = []

        for scenario_id in scenario_ids:
            scenario_results = []

            for result in simulation_results:
                if result.scenario_id == scenario_id:
                    scenario_results.append(result)

            max_step = 0

            for result in scenario_results:
                last_step = result.spread_over_steps[-1][0]

                if last_step > max_step:
                    max_step = last_step

            for step in range(max_step + 1):
                reached_accounts_values = []

                for result in scenario_results:
                    last_reached_accounts = result.spread_over_steps[0][1]

                    for result_step, reached_accounts in result.spread_over_steps:
                        if result_step > step:
                            break

                        last_reached_accounts = reached_accounts

                    reached_accounts_values.append(last_reached_accounts)

                spread_summaries.append(SpreadOverStepsSummary(scenario_id=scenario_id, step=step,
                                                               mean_reached_accounts=mean(reached_accounts_values),
                                                               std_reached_accounts=stdev(reached_accounts_values)))

        return spread_summaries
