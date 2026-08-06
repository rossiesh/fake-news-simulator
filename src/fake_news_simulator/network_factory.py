import numpy
import networkx


class NetworkFactory:
    def create_graph(self, number_of_nodes: int, influencer_ratio: float) -> networkx.DiGraph:
        graph = networkx.DiGraph()
        self._add_nodes(graph, number_of_nodes, influencer_ratio)
        self._add_follow_edges(graph, number_of_nodes)

        return graph

    @staticmethod
    def _add_nodes(graph: networkx.DiGraph, number_of_nodes: int, influencer_ratio: float) -> None:
        influencer_amount = int(number_of_nodes * influencer_ratio)
        influencer_node_ids = set(numpy.random.permutation(number_of_nodes)[:influencer_amount])

        for node_id in range(number_of_nodes):
            graph.add_node(
                node_id,
                is_influencer=node_id in influencer_node_ids,
                has_seen=False,
                has_shared=False)

    @staticmethod
    def _add_follow_edges(graph: networkx.DiGraph, number_of_nodes: int) -> None:
        node_ids = list(graph.nodes)
        edges = []

        for node_id in node_ids:
            if graph.nodes[node_id]["is_influencer"]:
                following_amount = numpy.random.randint(int(number_of_nodes * 0.0005),
                                                        int(number_of_nodes * 0.015) + 1)
            else:
                following_amount = numpy.random.randint(int(number_of_nodes * 0.002),
                                                        int(number_of_nodes * 0.025) + 1)

            possible_followed_ids = node_ids.copy()
            possible_followed_ids.remove(node_id)

            weights = []

            for followed_id in possible_followed_ids:
                if graph.nodes[followed_id]["is_influencer"]:
                    weights.append(10.0)
                else:
                    weights.append(1.0)

            probabilities = numpy.array(weights) / sum(weights)

            selected_followed_ids = numpy.asarray(numpy.random.choice(possible_followed_ids,
                                                                      size=min(following_amount,
                                                                               len(possible_followed_ids)),
                                                                      replace=False,
                                                                      p=probabilities))

            for selected_followed_id in selected_followed_ids:
                edges.append((node_id, int(selected_followed_id)))

        graph.add_edges_from(edges)
