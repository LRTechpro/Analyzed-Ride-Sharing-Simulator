"""Car model for the final ride-sharing simulator."""

from typing import TYPE_CHECKING

from graph import Graph, find_nearest_vertex
from pathfinding import find_shortest_path

if TYPE_CHECKING:
    from rider import Rider

Coordinates = tuple[float, float]


class Car:
    """Represent a vehicle and its operational metrics."""

    def __init__(self, car_id: str, location: Coordinates) -> None:
        self.id = car_id
        self.location = (float(location[0]), float(location[1]))
        self.status = "available"
        self.assigned_rider: Rider | None = None
        self.route: list[str] | None = None
        self.route_time = float("inf")
        self.busy_start_time: float | None = None
        self.total_busy_time = 0.0
        self.trips_completed = 0

    def calculate_route(
        self,
        destination: Coordinates,
        graph: Graph,
    ) -> tuple[list[str] | None, float]:
        """Snap coordinate endpoints and store their shortest road route."""
        start_vertex = find_nearest_vertex(self.location, graph.node_coordinates)
        end_vertex = find_nearest_vertex(destination, graph.node_coordinates)
        self.route, self.route_time = find_shortest_path(
            graph, start_vertex, end_vertex
        )
        return self.route, self.route_time

    def __str__(self) -> str:
        return f"Car {self.id} at {self.location} - Status: {self.status}"
