"""Weighted city graph containing both road topology and coordinates."""

from __future__ import annotations

import csv
import math

Coordinates = tuple[float, float]


class Graph:
    """Store an undirected weighted road network and node geometry."""

    def __init__(self) -> None:
        self.adjacency_list: dict[str, list[tuple[str, float]]] = {}
        self.node_coordinates: dict[str, Coordinates] = {}

    def add_edge(
        self,
        start_node: str,
        end_node: str,
        weight: float,
        *,
        bidirectional: bool = False,
    ) -> None:
        """Add a nonnegative road edge, optionally in both directions."""
        if weight < 0:
            raise ValueError("Road weights cannot be negative.")
        self.adjacency_list.setdefault(start_node, []).append(
            (end_node, float(weight))
        )
        self.adjacency_list.setdefault(end_node, [])
        if bidirectional:
            self.adjacency_list[end_node].append((start_node, float(weight)))

    def load_map_data(self, filename: str) -> None:
        """Load seven-column roads: start ID/XY, end ID/XY, and weight."""
        self.adjacency_list.clear()
        self.node_coordinates.clear()
        with open(filename, newline="", encoding="utf-8-sig") as map_file:
            reader = csv.reader(map_file)
            for line_number, row in enumerate(reader, start=1):
                if not row or not any(value.strip() for value in row):
                    continue
                if row[0].lstrip().startswith("#"):
                    continue
                values = [value.strip() for value in row]
                if line_number == 1 and values[0].lower() == "start_node_id":
                    continue
                if len(values) != 7:
                    raise ValueError(
                        f"Invalid map row {line_number}: expected 7 columns, "
                        f"received {len(values)}."
                    )
                start_id, sx, sy, end_id, ex, ey, raw_weight = values
                try:
                    start_coordinates = (float(sx), float(sy))
                    end_coordinates = (float(ex), float(ey))
                    weight = float(raw_weight)
                except ValueError as error:
                    raise ValueError(
                        f"Invalid numeric value on map row {line_number}."
                    ) from error
                if not math.isfinite(weight) or weight < 0:
                    raise ValueError(
                        f"Invalid road weight on map row {line_number}."
                    )
                for node_id, coordinates in (
                    (start_id, start_coordinates),
                    (end_id, end_coordinates),
                ):
                    previous = self.node_coordinates.get(node_id)
                    if previous is not None and previous != coordinates:
                        raise ValueError(
                            f"Conflicting coordinates for node {node_id!r}."
                        )
                    self.node_coordinates[node_id] = coordinates
                self.add_edge(start_id, end_id, weight, bidirectional=True)
        if not self.node_coordinates:
            raise ValueError("The city map contains no graph vertices.")

    load_from_file = load_map_data

    def __str__(self) -> str:
        lines = ["--- City Map Adjacency List ---"]
        for node, neighbors in self.adjacency_list.items():
            neighbor_text = ", ".join(
                f"({neighbor}, {weight:g})" for neighbor, weight in neighbors
            )
            lines.append(f"{node} {self.node_coordinates.get(node)} -> [{neighbor_text}]")
        return "\n".join(lines)


def find_nearest_vertex(
    point: Coordinates,
    node_coordinates: dict[str, Coordinates],
) -> str:
    """Return the graph vertex nearest to a physical coordinate pair."""
    if not node_coordinates:
        raise ValueError("Cannot snap a point because no graph vertices are loaded.")
    point_x, point_y = point
    return min(
        node_coordinates,
        key=lambda node_id: (
            (node_coordinates[node_id][0] - point_x) ** 2
            + (node_coordinates[node_id][1] - point_y) ** 2,
            node_id,
        ),
    )
