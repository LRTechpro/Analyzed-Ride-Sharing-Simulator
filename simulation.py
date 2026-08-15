"""Discrete-event engine for the ride-sharing simulator prototype."""

import heapq
import itertools
import math
from typing import Any

from car import Car, Coordinates
from graph import Graph
from rider import Rider

TRAVEL_SPEED_FACTOR = 1.0
Event = tuple[float, int, str, Any]


def calculate_travel_time(
    start_location: Coordinates,
    end_location: Coordinates,
) -> float:
    """Estimate travel time with Manhattan distance and a speed factor."""
    x1, y1 = start_location
    x2, y2 = end_location
    distance = abs(x1 - x2) + abs(y1 - y2)
    return distance * TRAVEL_SPEED_FACTOR


class Simulation:
    """Process rider requests and car arrivals in chronological order."""

    def __init__(self, map_filename: str) -> None:
        """Initialize the simulation and load its city map from a CSV file."""
        self.cars: dict[str, Car] = {}
        self.riders: dict[str, Rider] = {}
        self.map = Graph()
        self.map.load_from_file(map_filename)
        self.current_time = 0.0
        self.events: list[Event] = []
        self.event_log: list[str] = []
        self._sequence = itertools.count()

    def schedule_event(
        self,
        timestamp: float,
        event_type: str,
        data: Any,
    ) -> None:
        """Push one event onto the min-heap with a stable tie breaker."""
        event = (float(timestamp), next(self._sequence), event_type, data)
        heapq.heappush(self.events, event)

    def log(self, message: str) -> None:
        """Store and print an event message for testing and demonstration."""
        self.event_log.append(message)
        print(message)

    def run(self) -> None:
        """Schedule rider requests and process the event heap until empty."""
        self.current_time = 0.0
        self.events.clear()
        self.event_log.clear()
        self._sequence = itertools.count()

        for rider in self.riders.values():
            self.schedule_event(rider.request_time, "RIDER_REQUEST", rider)

        self.log("--- Simulation Engine Prototype ---")

        while self.events:
            timestamp, _, event_type, data = heapq.heappop(self.events)
            self.current_time = timestamp

            if event_type == "RIDER_REQUEST":
                self.handle_rider_request(data)
            elif event_type == "ARRIVAL":
                self.handle_arrival(data)
            else:
                raise ValueError(f"Unknown event type: {event_type}")

        self.log(f"--- Simulation complete at time {self.current_time:.2f} ---")

    def find_closest_car_brute_force(
        self,
        rider_location: Coordinates,
    ) -> Car | None:
        """Return the nearest available car using a linear search."""
        closest_car = None
        closest_distance = math.inf

        for car in self.cars.values():
            if car.status != "available":
                continue

            distance = math.dist(car.location, rider_location)
            if distance < closest_distance:
                closest_car = car
                closest_distance = distance

        return closest_car

    def handle_rider_request(self, rider: Rider) -> None:
        """Match an available car and schedule its pickup arrival."""
        self.log(
            f"TIME {self.current_time:.2f}: RIDER {rider.id} requested a ride"
        )
        car = self.find_closest_car_brute_force(rider.start_location)

        if car is None:
            self.log(
                f"TIME {self.current_time:.2f}: No available car for RIDER {rider.id}"
            )
            return

        car.assigned_rider = rider
        car.status = "en_route_to_pickup"
        rider.status = "assigned"
        pickup_duration = calculate_travel_time(
            car.location,
            rider.start_location,
        )
        self.schedule_event(
            self.current_time + pickup_duration,
            "ARRIVAL",
            car,
        )
        self.log(
            f"TIME {self.current_time:.2f}: CAR {car.id} dispatched to RIDER {rider.id}"
        )

    def handle_arrival(self, car: Car) -> None:
        """Handle a pickup or dropoff according to the car's current status."""
        rider = car.assigned_rider
        if rider is None:
            raise RuntimeError(f"CAR {car.id} arrived without an assigned rider")

        if car.status == "en_route_to_pickup":
            self.log(
                f"TIME {self.current_time:.2f}: CAR {car.id} picked up RIDER {rider.id}"
            )

            # The car is physically at the rider's pickup coordinates.
            car.location = rider.start_location
            car.status = "en_route_to_destination"
            rider.status = "in_car"

            dropoff_duration = calculate_travel_time(
                car.location,
                rider.destination,
            )
            self.schedule_event(
                self.current_time + dropoff_duration,
                "ARRIVAL",
                car,
            )

        elif car.status == "en_route_to_destination":
            self.log(
                f"TIME {self.current_time:.2f}: CAR {car.id} dropped off RIDER {rider.id}"
            )

            # The car is physically at the rider's destination coordinates.
            car.location = rider.destination
            car.status = "available"
            rider.status = "completed"
            car.assigned_rider = None

        else:
            raise RuntimeError(
                f"CAR {car.id} arrived with invalid status {car.status!r}"
            )

    def __str__(self) -> str:
        """Return a readable summary of the simulation state."""
        return (
            f"Simulation with {len(self.cars)} car(s) "
            f"and {len(self.riders)} rider(s)"
        )
