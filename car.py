"""Car model for the ride-sharing simulator."""


class Car:
    """Represent a vehicle in the ride-sharing fleet."""

    def __init__(self, car_id: str, location: tuple[int, int]) -> None:
        """Initialize a car with an ID and starting location."""
        self.id = car_id
        self.location = location
        self.status = "available"
        self.destination = None

    def __str__(self) -> str:
        """Return a readable summary of the car."""
        return f"Car {self.id} at {self.location} - Status: {self.status}"
