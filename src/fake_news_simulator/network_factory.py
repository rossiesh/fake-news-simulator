import numpy
import networkx


class NetworkFactory:
    def create_graph(self, number_of_nodes: int, influencer_ratio: float) -> networkx.Graph:
        graph = networkx.Graph()
        self._add_nodes(graph, number_of_nodes, influencer_ratio)
        self._add_edges(graph, number_of_nodes)

        return graph

    def _add_nodes(self, graph: networkx.Graph, number_of_nodes: int, influencer_ratio: float) -> None:
        influencer_amount = int(number_of_nodes * influencer_ratio)
        influencer_node_ids = set(numpy.random.permutation(number_of_nodes)[:influencer_amount])

        for node_id in range(number_of_nodes):
            graph.add_node(
                node_id,
                is_influencer=node_id in influencer_node_ids,
                has_seen=False,
                has_shared=False)

    def _add_edges(self, graph: networkx.Graph, number_of_nodes: int) -> None:
        node_ids = list(graph.nodes)
        edges = []

        for node_id in node_ids:
            if graph.nodes[node_id]["is_influencer"]:
                connection_amount = numpy.random.randint(int(number_of_nodes * 0.09),
                                                         int(number_of_nodes * 0.20) + 1)
            else:
                connection_amount = numpy.random.randint(int(number_of_nodes * 0.02),
                                                         int(number_of_nodes * 0.04) + 1)

            possible_target_ids = node_ids.copy()
            possible_target_ids.remove(node_id)

            selected_targets = numpy.random.permutation(possible_target_ids)[:connection_amount]

            for target_id in selected_targets:
                edges.append((node_id, target_id))

        graph.add_edges_from(edges)
