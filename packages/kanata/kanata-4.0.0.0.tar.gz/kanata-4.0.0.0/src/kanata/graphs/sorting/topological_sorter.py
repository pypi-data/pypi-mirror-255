from kanata.exceptions import ArgumentException
from kanata.graphs import BidirectedGraph, TNode
from kanata.graphs.exceptions import CyclicGraphException, DisconnectedSubGraphException

def topological_sort(graph: BidirectedGraph[TNode], start_node: TNode) -> tuple[TNode, ...]:
    """Produces a linear ordering of the specified graph's nodes
    such that for every directed edge uv from node u to node v, u comes before v in the ordering.

    :param graph: The graph whose nodes are to be sorted.
    :type graph: BidirectedGraph[TNode]
    :param start_node: The node used as the starting point for the ordering.
    :type start_node: TNode
    :raises ArgumentException: Raised when the specified start node is not in the graph.
    :raises DisconnectedSubGraphException: Raised when a disconnected sub-graph is detected within the graph.
    :return: The sorted nodes of the specified graph.
    :rtype: tuple[TNode, ...]
    """

    if start_node not in graph:
        raise ArgumentException(
            "start_node",
            start_node,
            f"The start node '{start_node}' is not in the graph."
        )

    visited_nodes: set[TNode] = set()
    unvisited_nodes: set[TNode] = graph.nodes
    sorted_nodes: list[TNode] = []
    __visit(graph, start_node, visited_nodes, set(), sorted_nodes)
    if visited_nodes != unvisited_nodes:
        raise DisconnectedSubGraphException(tuple(str(node) for node in unvisited_nodes))
    return tuple(sorted_nodes)

def __visit(
    graph: BidirectedGraph[TNode],
    node: TNode,
    visited_nodes: set[TNode],
    currently_visiting: set[TNode],
    sorted_nodes: list[TNode]
) -> None:
    if node in visited_nodes:
        return
    if node in currently_visiting:
        raise CyclicGraphException(
            currently_visiting,
            "A directed acyclic graph (DAG) is expected."
        )

    currently_visiting.add(node)
    for out_node in {edge.target for edge in graph.get_out_edges(node)}:
        __visit(graph, out_node, visited_nodes, currently_visiting, sorted_nodes)
    currently_visiting.remove(node)

    visited_nodes.add(node)
    sorted_nodes.append(node)
