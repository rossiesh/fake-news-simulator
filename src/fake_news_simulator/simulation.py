from dataclasses import dataclass

import networkx
import numpy.random

from fake_news_simulator.experiment_schema import ModerationType
from fake_news_simulator.scenario_generator import Scenario


@dataclass(frozen=True)
class SimulationResult:
    scenario_id: str
    run_index: int
    reached_accounts: int
    total_shares: int
    spread_over_steps: list[tuple[int, int]]


class Simulation:
    def run(self, scenario: Scenario, run_index: int, graph: networkx.DiGraph, start_node: int) -> SimulationResult:
        graph.nodes[start_node]["has_seen"] = True
        graph.nodes[start_node]["has_shared"] = True

        active_nodes = {start_node}
        reached_accounts = 1
        total_shares = 1
        spread_over_steps = [(0, reached_accounts)]

        for step in range(1, scenario.max_steps_per_run + 1):
            if not active_nodes:
                break

            if self._is_delete_active(scenario, reached_accounts):
                break

            new_active_nodes = set()

            for node_id in active_nodes:
                reachable_followers = self._get_reachable_followers(graph, node_id, scenario, reached_accounts)

                for follower_id in reachable_followers:
                    if graph.nodes[follower_id]["has_seen"]:
                        continue

                    graph.nodes[follower_id]["has_seen"] = True
                    reached_accounts += 1

                    if self._should_check(scenario):
                        continue

                    if self._should_share(scenario, reached_accounts):
                        graph.nodes[follower_id]["has_shared"] = True
                        new_active_nodes.add(follower_id)
                        total_shares += 1

            active_nodes = new_active_nodes
            spread_over_steps.append((step, reached_accounts))

        return SimulationResult(
            scenario_id=scenario.scenario_id,
            run_index=run_index,
            reached_accounts=reached_accounts,
            total_shares=total_shares,
            spread_over_steps=spread_over_steps
        )

    def _get_reachable_followers(self, graph: networkx.DiGraph, node_id: int, scenario: Scenario,
                                 reached_accounts: int) -> list[int]:
        all_followers = list(graph.predecessors(node_id))
        recipient_ratio = scenario.recipient_ratio

        if self._is_downrank_active(scenario, reached_accounts):
            recipient_ratio *= (1 - scenario.moderation_downrank_reduction_factor)

        selected_followers = numpy.random.permutation(all_followers)[:int(len(all_followers) * recipient_ratio)]

        result = []
        for follower_id in selected_followers:
            result.append(int(follower_id))

        return result

    def _should_share(self, scenario: Scenario, reached_accounts: int) -> bool:
        share_probability = scenario.share_probability

        if self._is_label_active(scenario, reached_accounts):
            share_probability *= (1 - scenario.moderation_label_reduction_factor)

        return numpy.random.random() < share_probability

    @staticmethod
    def _should_check(scenario: Scenario) -> bool:
        return numpy.random.random() < scenario.check_probability

    @staticmethod
    def _is_moderation_active(scenario: Scenario, reached_accounts: int) -> bool:
        return reached_accounts >= scenario.moderation_threshold

    def _is_label_active(self, scenario: Scenario, reached_accounts: int) -> bool:
        return scenario.moderation_type == ModerationType.LABEL and self._is_moderation_active(scenario,
                                                                                               reached_accounts)

    def _is_downrank_active(self, scenario: Scenario, reached_accounts: int) -> bool:
        return scenario.moderation_type == ModerationType.DOWNRANK and self._is_moderation_active(scenario,
                                                                                                  reached_accounts)

    def _is_delete_active(self, scenario: Scenario, reached_accounts: int) -> bool:
        return scenario.moderation_type == ModerationType.DELETE and self._is_moderation_active(scenario,
                                                                                                reached_accounts)
