import numpy.random

from fake_news_simulator.network_factory import NetworkFactory
from fake_news_simulator.scenario_generator import Scenario
from fake_news_simulator.simulation import Simulation, SimulationResult


class ExperimentRunner:
    def run(self, scenarios: list[Scenario]) -> list[SimulationResult]:
        network_factory = NetworkFactory()
        simulation = Simulation()
        results = []

        number_of_nodes = scenarios[0].number_of_nodes
        influencer_ratio = scenarios[0].influencer_ratio
        runs_per_scenario = scenarios[0].runs_per_scenario

        for run_index in range(1, runs_per_scenario + 1):
            base_graph = network_factory.create_graph(number_of_nodes, influencer_ratio)
            start_node = int(numpy.random.choice(list(base_graph.nodes)))

            for scenario in scenarios:
                base_graph_copy = base_graph.copy()
                scenario_result = simulation.run(scenario, run_index, base_graph_copy, start_node)
                results.append(scenario_result)

        return results
