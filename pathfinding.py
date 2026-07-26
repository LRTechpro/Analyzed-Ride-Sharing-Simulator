"""Shortest-path algorithms for the ride-sharing simulator."""

import heapq

from graph import Graph


def find_shortest_path(
    graph: Graph,
    start_node: str,
    end_node: str,
) -> tuple[list[str] | None, float]:
    """Return the fastest path and travel time between two graph nodes.

    Dijkstra's algorithm is valid because the map uses nonnegative edge
    weights. A min-heap keeps the next closest unvisited node at the front of
    the priority queue.
    """
    adjacency_list = graph.adjacency_list

    if start_node not in adjacency_list or end_node not in adjacency_list:
        return None, float("inf")

    distances = {node: float("inf") for node in adjacency_list}
    predecessors: dict[str, str] = {}
    distances[start_node] = 0.0

    priority_queue: list[tuple[float, str]] = [(0.0, start_node)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        # Ignore an older heap entry if a faster route was found after it
        # entered the queue.
        if current_distance > distances[current_node]:
            continue

        if current_node == end_node:
            break

        for neighbor, edge_weight in adjacency_list[current_node]:
            if edge_weight < 0:
                raise ValueError("Dijkstra's algorithm requires nonnegative weights.")

            candidate_distance = current_distance + edge_weight

            if candidate_distance < distances[neighbor]:
                distances[neighbor] = candidate_distance
                predecessors[neighbor] = current_node
                heapq.heappush(
                    priority_queue,
                    (candidate_distance, neighbor),
                )

    if distances[end_node] == float("inf"):
        return None, float("inf")

    path = []
    current_node: str | None = end_node

    while current_node is not None:
        path.append(current_node)
        current_node = predecessors.get(current_node)

    path.reverse()
    return path, distances[end_node]
