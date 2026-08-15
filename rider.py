"""Rider model for the ride-sharing simulator."""

Coordinates = tuple[float, float]


class Rider:
    """Represent a customer requesting a ride."""

    def __init__(
        self,
        rider_id: str,
        start_location: Coordinates,
        destination: Coordinates,
        request_time: float = 0.0,
    ) -> None:
        """Initialize a rider with pickup and dropoff locations."""
        self.id = rider_id
        self.start_location = start_location
        self.destination = destination
        self.request_time = float(request_time)
        self.status = "waiting"

    def __str__(self) -> str:
        """Return a readable summary of the rider."""
        return (
            f"Rider {self.id} at {self.start_location} "
            f"waiting for ride to {self.destination}"
        )
