"""Rider model for the final ride-sharing simulator."""

Coordinates = tuple[float, float]


class Rider:
    """Represent a ride request and its lifecycle timestamps."""

    def __init__(
        self,
        rider_id: str,
        start_location: Coordinates,
        destination: Coordinates,
        request_time: float | None = None,
    ) -> None:
        self.id = rider_id
        self.start_location = (
            float(start_location[0]),
            float(start_location[1]),
        )
        self.destination = (float(destination[0]), float(destination[1]))
        self.status = "waiting"
        self.request_time = (
            None if request_time is None else float(request_time)
        )
        self.pickup_time: float | None = None
        self.dropoff_time: float | None = None

    def __str__(self) -> str:
        return (
            f"Rider {self.id} at {self.start_location} "
            f"waiting for ride to {self.destination}"
        )
