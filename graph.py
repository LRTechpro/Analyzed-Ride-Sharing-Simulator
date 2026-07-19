"""Weighted, directed graph for the ride-sharing city map."""

import csv


class Graph:
    """Represent a city map with a dictionary-based adjacency list."""

    def __init__(self) -> None:
        """Initialize an empty adjacency list."""
        self.adjacency_list: dict[str, list[tuple[str, float]]] = {}

    def add_edge(self, start_node: str, end_node: str, weight: float) -> None:
        """Add one directed, weighted edge to the graph."""
        if start_node not in self.adjacency_list:
            self.adjacency_list[start_node] = []

        # Keep destination-only nodes visible in the map representation.
        if end_node not in self.adjacency_list:
            self.adjacency_list[end_node] = []

        self.adjacency_list[start_node].append((end_node, float(weight)))

    def load_from_file(self, filename: str) -> None:
        """Load directed edges from a start_node,end_node,travel_time CSV file."""
        with open(filename, mode="r", newline="", encoding="utf-8-sig") as map_file:
            reader = csv.reader(map_file)

            for line_number, row in enumerate(reader, start=1):
                if not row or all(not value.strip() for value in row):
                    continue

                if len(row) != 3:
                    raise ValueError(
                        f"Invalid map row {line_number}: expected 3 columns, "
                        f"received {len(row)}."
                    )

                start_node, end_node, travel_time = (value.strip() for value in row)

                # Permit an optional descriptive header without treating it as an edge.
                if line_number == 1 and [
                    start_node.lower(),
                    end_node.lower(),
                    travel_time.lower(),
                ] == ["start_node", "end_node", "travel_time"]:
                    continue

                if not start_node or not end_node:
                    raise ValueError(f"Invalid map row {line_number}: node IDs cannot be empty.")

                try:
                    weight = float(travel_time)
                except ValueError as error:
                    raise ValueError(
                        f"Invalid travel time on row {line_number}: {travel_time!r}."
                    ) from error

                if weight < 0:
                    raise ValueError(
                        f"Invalid travel time on row {line_number}: weight cannot be negative."
                    )

                self.add_edge(start_node, end_node, weight)

    def __str__(self) -> str:
        """Return a readable representation of the adjacency list."""
        lines = ["--- City Map Adjacency List ---"]
        for node, neighbors in self.adjacency_list.items():
            neighbor_text = ", ".join(
                f"({neighbor}, {weight:g})" for neighbor, weight in neighbors
            )
            lines.append(f"{node} -> [{neighbor_text}]")
        lines.append("-------------------------------")
        return "\n".join(lines)
