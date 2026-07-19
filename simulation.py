"""Simulation controller for the ride-sharing simulator."""

from car import Car
from graph import Graph
from rider import Rider


class Simulation:
    """Store and manage the current simulation state."""

    def __init__(self, map_filename: str) -> None:
        """Initialize the simulation and load its city map from a CSV file."""
        self.cars: dict[str, Car] = {}
        self.riders: dict[str, Rider] = {}
        self.map = Graph()
        self.map.load_from_file(map_filename)

    def __str__(self) -> str:
        """Return a readable summary of the simulation state."""
        return (
            f"Simulation with {len(self.cars)} car(s) "
            f"and {len(self.riders)} rider(s)"
        )
