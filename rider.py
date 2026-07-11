"""Rider model for the ride-sharing simulator."""


class Rider:
    """Represent a customer requesting a ride."""

    def __init__(
        self,
        rider_id: str,
        start_location: tuple[int, int],
        destination: tuple[int, int],
    ) -> None:
        """Initialize a rider with pickup and dropoff locations."""
        self.id = rider_id
        self.start_location = start_location
        self.destination = destination
        self.status = "waiting"

    def __str__(self) -> str:
        """Return a readable summary of the rider."""
        return (
            f"Rider {self.id} at {self.start_location} "
            f"waiting for ride to {self.destination}"
        )
