"""Integrated event-driven ride-sharing simulation."""

from __future__ import annotations

import argparse
import heapq
from itertools import count
import math
import os
from pathlib import Path
import random
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-ms549")
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from car import Car
from graph import Graph, find_nearest_vertex
from pathfinding import find_shortest_path
from quadtree import Point, Quadtree, Rectangle
from rider import Rider

DEFAULT_CANDIDATE_COUNT = 5
MEAN_ARRIVAL_TIME = 8.0
Event = tuple[float, int, str, Any]


class Simulation:
    """Coordinate the graph, Quadtree, actors, events, and metrics."""

    def __init__(
        self,
        map_filename: str,
        *,
        max_time: float | None = 200.0,
        num_riders: int | None = 25,
        num_cars: int = 100,
        candidate_count: int = DEFAULT_CANDIDATE_COUNT,
        random_seed: int = 549,
        mean_arrival_time: float = MEAN_ARRIVAL_TIME,
        simultaneous_demo: bool = False,
    ) -> None:
        if candidate_count <= 0:
            raise ValueError("candidate_count must be positive.")
        if num_cars < 0:
            raise ValueError("num_cars cannot be negative.")
        if num_riders is not None and num_riders < 0:
            raise ValueError("num_riders cannot be negative.")
        if max_time is not None and max_time < 0:
            raise ValueError("max_time cannot be negative.")
        if mean_arrival_time <= 0:
            raise ValueError("mean_arrival_time must be positive.")

        self.graph = Graph()
        self.graph.load_map_data(map_filename)
        self.map = self.graph
        self.map_filename = map_filename
        self.current_time = 0.0
        self.events: list[Event] = []
        self.event_sequence = count()
        self.event_log: list[str] = []
        self.cars: dict[str, Car] = {}
        self.riders: dict[str, Rider] = {}
        self.available_cars: dict[str, Car] = {}
        self.available_car_points: dict[str, Point] = {}
        self.candidate_count = candidate_count
        self.max_time = max_time
        self.num_riders = num_riders
        self.random = random.Random(random_seed)
        self.mean_arrival_time = mean_arrival_time
        self.simultaneous_demo = simultaneous_demo
        self.generated_count = 0
        self.dijkstra_evaluations = 0

        xs = [coordinates[0] for coordinates in self.graph.node_coordinates.values()]
        ys = [coordinates[1] for coordinates in self.graph.node_coordinates.values()]
        self.minimum_x, self.maximum_x = min(xs), max(xs)
        self.minimum_y, self.maximum_y = min(ys), max(ys)
        width = max(self.maximum_x - self.minimum_x, 1.0)
        height = max(self.maximum_y - self.minimum_y, 1.0)
        self.map_boundary = Rectangle(
            self.minimum_x,
            self.minimum_y,
            width,
            height,
        )
        self.available_car_quadtree = Quadtree(self.map_boundary, capacity=4)
        self._initialize_cars(num_cars)

    def _random_location(self) -> tuple[float, float]:
        return (
            self.random.uniform(self.minimum_x, self.maximum_x),
            self.random.uniform(self.minimum_y, self.maximum_y),
        )

    def _initialize_cars(self, number_of_cars: int) -> None:
        for index in range(1, number_of_cars + 1):
            car = Car(f"CAR{index:03d}", self._random_location())
            self.cars[car.id] = car
            self.add_available_car(car)

    def schedule_event(self, timestamp: float, event_type: str, data: Any) -> None:
        """Schedule every event with a deterministic sequence tie-breaker."""
        timestamp = float(timestamp)
        if not math.isfinite(timestamp):
            raise ValueError("An event timestamp must be finite.")
        heapq.heappush(
            self.events,
            (timestamp, next(self.event_sequence), event_type, data),
        )

    def log(self, message: str) -> None:
        self.event_log.append(message)
        print(message)

    def add_available_car(self, car: Car) -> None:
        """Atomically add a car to both dictionaries and the Quadtree."""
        if car.id in self.available_cars or car.id in self.available_car_points:
            raise ValueError(f"CAR {car.id} is already available.")
        point = Point(car.location[0], car.location[1], data=car)
        if not self.available_car_quadtree.insert(point):
            raise ValueError(f"CAR {car.id} is outside the Quadtree boundary.")
        self.available_cars[car.id] = car
        self.available_car_points[car.id] = point
        car.status = "available"
        self._assert_availability_invariant()

    def remove_available_car(self, car: Car) -> None:
        """Atomically remove the exact indexed Point and dictionary entries."""
        try:
            point = self.available_car_points[car.id]
        except KeyError as error:
            raise KeyError(f"CAR {car.id} is not indexed as available.") from error
        if not self.available_car_quadtree.remove(point):
            raise RuntimeError(f"Quadtree removal failed for CAR {car.id}.")
        del self.available_car_points[car.id]
        del self.available_cars[car.id]
        self._assert_availability_invariant()

    def _assert_availability_invariant(self) -> None:
        if set(self.available_cars) != set(self.available_car_points):
            raise RuntimeError("Availability dictionaries are out of sync.")

    def generate_rider_request(self) -> Rider:
        """Create one reproducible rider request inside the map boundary."""
        if self.num_riders is not None and self.generated_count >= self.num_riders:
            raise RuntimeError("The configured rider limit has been reached.")
        self.generated_count += 1
        start = self._random_location()
        destination = self._random_location()
        while destination == start:
            destination = self._random_location()
        rider = Rider(f"RIDER{self.generated_count:03d}", start, destination)
        self.riders[rider.id] = rider
        return rider

    def _generation_allowed(self, timestamp: float) -> bool:
        rider_limit_ok = (
            self.num_riders is None or self.generated_count < self.num_riders
        )
        time_limit_ok = self.max_time is None or timestamp <= self.max_time
        return rider_limit_ok and time_limit_ok

    def _schedule_initial_requests(self) -> None:
        if not self._generation_allowed(0.0):
            return
        first = self.generate_rider_request()
        self.schedule_event(0.0, "RIDER_REQUEST", first)
        if self.simultaneous_demo and self._generation_allowed(0.0):
            second = self.generate_rider_request()
            self.schedule_event(0.0, "RIDER_REQUEST", second)

    def _schedule_next_request(self) -> None:
        if self.num_riders is not None and self.generated_count >= self.num_riders:
            return
        next_time = self.current_time + self.random.expovariate(
            1.0 / self.mean_arrival_time
        )
        if not self._generation_allowed(next_time):
            return
        rider = self.generate_rider_request()
        self.schedule_event(next_time, "RIDER_REQUEST", rider)

    def run(self) -> dict[str, float | int]:
        """Process all events, including active trips after generation stops."""
        if not self.events and self.generated_count == 0:
            self._schedule_initial_requests()
        self.log("--- Integrated Ride-Sharing Simulation ---")
        while self.events:
            timestamp, sequence_number, event_type, data = heapq.heappop(
                self.events
            )
            self.current_time = timestamp
            self.log(
                f"TIME {timestamp:.2f}: EVENT {sequence_number} {event_type}"
            )
            if event_type == "RIDER_REQUEST":
                self.handle_rider_request(data)
                self._schedule_next_request()
            elif event_type == "PICKUP_ARRIVAL":
                self.handle_pickup_arrival(data)
            elif event_type == "DROPOFF_ARRIVAL":
                self.handle_dropoff_arrival(data)
            else:
                raise ValueError(f"Unknown event type: {event_type}")
        metrics = self.calculate_metrics()
        self.log(f"--- Simulation complete at time {self.current_time:.2f} ---")
        return metrics

    def handle_rider_request(self, rider: Rider) -> None:
        if rider.request_time is None:
            rider.request_time = self.current_time
        query_point = Point(*rider.start_location)
        candidate_points = self.available_car_quadtree.find_k_nearest(
            query_point, k=self.candidate_count
        )
        if not candidate_points:
            self._mark_unmatched(rider, "no available cars")
            return

        rider_vertex = find_nearest_vertex(
            rider.start_location, self.graph.node_coordinates
        )
        reachable: list[tuple[float, int, str, Car, list[str]]] = []
        for order, point in enumerate(candidate_points):
            car: Car = point.data
            car_vertex = find_nearest_vertex(
                car.location, self.graph.node_coordinates
            )
            route, travel_time = find_shortest_path(
                self.graph, car_vertex, rider_vertex
            )
            self.dijkstra_evaluations += 1
            if route is not None and math.isfinite(travel_time):
                reachable.append((travel_time, order, car.id, car, route))
        if not reachable:
            self._mark_unmatched(rider, "all candidate routes unreachable")
            return

        pickup_time, _, _, car, route = min(reachable)
        self.remove_available_car(car)
        car.status = "en_route_to_pickup"
        car.assigned_rider = rider
        car.route = route
        car.route_time = pickup_time
        car.busy_start_time = self.current_time
        rider.status = "waiting"
        self.schedule_event(
            self.current_time + pickup_time, "PICKUP_ARRIVAL", car
        )
        self.log(
            f"TIME {self.current_time:.2f}: CAR {car.id} dispatched to "
            f"RIDER {rider.id}; {len(candidate_points)} candidates evaluated"
        )

    def _mark_unmatched(self, rider: Rider, reason: str) -> None:
        rider.status = "unmatched"
        self.log(
            f"TIME {self.current_time:.2f}: RIDER {rider.id} unmatched ({reason})"
        )

    def handle_pickup_arrival(self, car: Car) -> None:
        rider = car.assigned_rider
        if rider is None or car.status != "en_route_to_pickup":
            raise RuntimeError(f"Invalid pickup state for CAR {car.id}.")
        car.location = rider.start_location
        car.status = "en_route_to_destination"
        rider.status = "in_car"
        rider.pickup_time = self.current_time

        start_vertex = find_nearest_vertex(
            rider.start_location, self.graph.node_coordinates
        )
        end_vertex = find_nearest_vertex(
            rider.destination, self.graph.node_coordinates
        )
        route, trip_time = find_shortest_path(
            self.graph, start_vertex, end_vertex
        )
        self.dijkstra_evaluations += 1
        if route is None or not math.isfinite(trip_time):
            rider.status = "unsuccessful"
            if car.busy_start_time is not None:
                car.total_busy_time += self.current_time - car.busy_start_time
            car.busy_start_time = None
            car.assigned_rider = None
            car.route = None
            car.route_time = float("inf")
            self.add_available_car(car)
            self.log(
                f"TIME {self.current_time:.2f}: RIDER {rider.id} trip "
                "unsuccessful; car returned to availability"
            )
            return

        car.route = route
        car.route_time = trip_time
        self.schedule_event(
            self.current_time + trip_time, "DROPOFF_ARRIVAL", car
        )
        self.log(
            f"TIME {self.current_time:.2f}: CAR {car.id} picked up RIDER {rider.id}"
        )

    def handle_dropoff_arrival(self, car: Car) -> None:
        rider = car.assigned_rider
        if rider is None or car.status != "en_route_to_destination":
            raise RuntimeError(f"Invalid dropoff state for CAR {car.id}.")
        car.location = rider.destination
        rider.status = "completed"
        rider.dropoff_time = self.current_time
        car.assigned_rider = None
        if car.busy_start_time is not None:
            car.total_busy_time += self.current_time - car.busy_start_time
        car.busy_start_time = None
        car.trips_completed += 1
        self.add_available_car(car)
        self.log(
            f"TIME {self.current_time:.2f}: CAR {car.id} dropped off "
            f"RIDER {rider.id} and was reinserted at {car.location}"
        )

    def calculate_metrics(self) -> dict[str, float | int]:
        completed = [
            rider for rider in self.riders.values() if rider.status == "completed"
        ]
        unsuccessful = [
            rider
            for rider in self.riders.values()
            if rider.status in {"unmatched", "unsuccessful"}
        ]
        wait_times = [
            rider.pickup_time - rider.request_time
            for rider in completed
            if rider.pickup_time is not None and rider.request_time is not None
        ]
        trip_times = [
            rider.dropoff_time - rider.pickup_time
            for rider in completed
            if rider.dropoff_time is not None and rider.pickup_time is not None
        ]
        total_busy = sum(car.total_busy_time for car in self.cars.values())
        denominator = len(self.cars) * self.current_time
        return {
            "total_riders": len(self.riders),
            "completed_riders": len(completed),
            "unmatched_or_unsuccessful": len(unsuccessful),
            "average_wait_time": sum(wait_times) / len(wait_times) if wait_times else 0.0,
            "average_trip_duration": sum(trip_times) / len(trip_times) if trip_times else 0.0,
            "driver_utilization": total_busy / denominator if denominator else 0.0,
            "simulation_span": self.current_time,
            "dijkstra_evaluations": self.dijkstra_evaluations,
        }

    def create_visualization(self, filename: str = "simulation_summary.png") -> None:
        """Save an integrated map, metrics panel, and outcome chart."""
        metrics = self.calculate_metrics()
        figure = plt.figure(figsize=(14, 8), constrained_layout=True)
        grid = figure.add_gridspec(2, 2, width_ratios=(2.2, 1.0))
        map_axis = figure.add_subplot(grid[:, 0])
        metrics_axis = figure.add_subplot(grid[0, 1])
        chart_axis = figure.add_subplot(grid[1, 1])

        drawn_edges: set[tuple[str, str]] = set()
        for start, neighbors in self.graph.adjacency_list.items():
            for end, _ in neighbors:
                edge = tuple(sorted((start, end)))
                if edge in drawn_edges:
                    continue
                drawn_edges.add(edge)
                x1, y1 = self.graph.node_coordinates[start]
                x2, y2 = self.graph.node_coordinates[end]
                map_axis.plot((x1, x2), (y1, y2), color="#cbd5e1", linewidth=1)
        node_x = [point[0] for point in self.graph.node_coordinates.values()]
        node_y = [point[1] for point in self.graph.node_coordinates.values()]
        car_x = [car.location[0] for car in self.cars.values()]
        car_y = [car.location[1] for car in self.cars.values()]
        map_axis.scatter(node_x, node_y, s=14, color="#334155", label="Graph vertices")
        map_axis.scatter(car_x, car_y, s=30, color="#0ea5e9", label="Final car locations")
        map_axis.set(title="Final Fleet Map", xlabel="X coordinate", ylabel="Y coordinate")
        map_axis.legend(loc="best")
        map_axis.grid(alpha=0.2)

        metrics_axis.axis("off")
        metrics_axis.set_title("Simulation Metrics", fontweight="bold")
        metrics_text = (
            f"Riders generated: {metrics['total_riders']}\n"
            f"Riders completed: {metrics['completed_riders']}\n"
            f"Unmatched/unsuccessful: {metrics['unmatched_or_unsuccessful']}\n"
            f"Average wait: {metrics['average_wait_time']:.2f}\n"
            f"Average trip: {metrics['average_trip_duration']:.2f}\n"
            f"Driver utilization: {metrics['driver_utilization']:.1%}\n"
            f"Simulation span: {metrics['simulation_span']:.2f}\n"
            f"Dijkstra runs: {metrics['dijkstra_evaluations']}"
        )
        metrics_axis.text(
            0.05, 0.88, metrics_text, va="top", fontsize=12, linespacing=1.55
        )

        outcomes = [
            int(metrics["completed_riders"]),
            int(metrics["unmatched_or_unsuccessful"]),
        ]
        chart_axis.bar(
            ["Completed", "Unmatched"], outcomes, color=["#22c55e", "#ef4444"]
        )
        chart_axis.set_title("Rider Outcomes")
        chart_axis.set_ylabel("Riders")
        chart_axis.grid(axis="y", alpha=0.2)
        figure.suptitle("Efficient Ride-Sharing Simulator", fontsize=16, fontweight="bold")
        figure.savefig(filename, dpi=160)
        plt.close(figure)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--map-file",
        default=str(Path(__file__).with_name("city_map.csv")),
    )
    parser.add_argument("--max-time", type=float, default=200.0)
    parser.add_argument("--num-riders", type=int, default=25)
    parser.add_argument("--num-cars", type=int, default=100)
    parser.add_argument(
        "--candidate-count", type=int, default=DEFAULT_CANDIDATE_COUNT
    )
    parser.add_argument("--random-seed", type=int, default=549)
    parser.add_argument("--mean-arrival-time", type=float, default=MEAN_ARRIVAL_TIME)
    parser.add_argument("--simultaneous-demo", action="store_true")
    parser.add_argument("--summary-file", default="simulation_summary.png")
    return parser


def main() -> None:
    args = build_argument_parser().parse_args()
    simulation = Simulation(
        args.map_file,
        max_time=args.max_time,
        num_riders=args.num_riders,
        num_cars=args.num_cars,
        candidate_count=args.candidate_count,
        random_seed=args.random_seed,
        mean_arrival_time=args.mean_arrival_time,
        simultaneous_demo=args.simultaneous_demo,
    )
    metrics = simulation.run()
    simulation.create_visualization(args.summary_file)
    print("\nFinal metrics:")
    for name, value in metrics.items():
        print(f"  {name}: {value:.3f}" if isinstance(value, float) else f"  {name}: {value}")
    print(f"\nSaved analytical visualization: {args.summary_file}")


if __name__ == "__main__":
    main()
