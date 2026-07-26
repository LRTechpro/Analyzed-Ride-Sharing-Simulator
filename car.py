"""Car model for the ride-sharing simulator."""

from graph import Graph
from pathfinding import find_shortest_path


class Car:
    """Represent a vehicle in the ride-sharing fleet."""

    def __init__(self, car_id: str, location: str) -> None:
        """Initialize a car with an ID and starting location."""
        self.id = car_id
        self.location = location
        self.status = "available"
        self.destination: str | None = None
        self.route: list[str] | None = None
        self.route_time = float("inf")

    def calculate_route(
        self,
        destination: str,
        graph: Graph,
    ) -> tuple[list[str] | None, float]:
        """Plan and remember the fastest route from the car's location."""
        self.destination = destination
        self.route, self.route_time = find_shortest_path(
            graph,
            self.location,
            destination,
        )
        return self.route, self.route_time

    def __str__(self) -> str:
        """Return a readable summary of the car."""
        return f"Car {self.id} at {self.location} - Status: {self.status}"
