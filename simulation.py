"""Simulation controller for the ride-sharing simulator."""

from car import Car
from rider import Rider


class Simulation:
    """Store and manage the current simulation state."""

    def __init__(self) -> None:
        """Initialize empty car and rider collections."""
        self.cars: dict[str, Car] = {}
        self.riders: dict[str, Rider] = {}

    def __str__(self) -> str:
        """Return a readable summary of the simulation state."""
        return (
            f"Simulation with {len(self.cars)} car(s) "
            f"and {len(self.riders)} rider(s)"
        )
