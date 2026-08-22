"""Correctness tests and repeatable final-project demonstration."""

import heapq
import math
from pathlib import Path

from car import Car
from rider import Rider
from simulation import Simulation

MAP_FILE = Path(__file__).with_name("city_map.csv")


def make_simulation(**overrides: object) -> Simulation:
    options: dict[str, object] = {
        "max_time": 30.0,
        "num_riders": 8,
        "num_cars": 5,
        "candidate_count": 5,
        "random_seed": 549,
        "mean_arrival_time": 3.0,
        "simultaneous_demo": True,
    }
    options.update(overrides)
    return Simulation(str(MAP_FILE), **options)


def test_event_tuple_and_equal_timestamp_order() -> None:
    simulation = make_simulation(num_riders=0, num_cars=0)
    first = Rider("R1", (0, 0), (100, 0))
    second = Rider("R2", (0, 0), (100, 0))
    simulation.schedule_event(0, "RIDER_REQUEST", first)
    simulation.schedule_event(0, "RIDER_REQUEST", second)
    event_one = heapq.heappop(simulation.events)
    event_two = heapq.heappop(simulation.events)
    assert len(event_one) == len(event_two) == 4
    assert event_one[0] == event_two[0] == 0.0
    assert event_one[1] < event_two[1]


def test_k_candidates_and_dispatch_availability() -> None:
    simulation = make_simulation(num_riders=0)
    rider = Rider("R1", (150, 150), (300, 300), request_time=0)
    simulation.riders[rider.id] = rider
    simulation.handle_rider_request(rider)
    assigned = [car for car in simulation.cars.values() if car.assigned_rider is rider]
    assert len(assigned) == 1
    car = assigned[0]
    assert car.id not in simulation.available_cars
    assert car.id not in simulation.available_car_points
    assert simulation.dijkstra_evaluations == 5
    assert all(math.isfinite(event[0]) for event in simulation.events)


def test_fewer_than_five_and_no_available_cars() -> None:
    two_cars = make_simulation(num_riders=0, num_cars=2)
    rider = Rider("R1", (0, 0), (300, 300), request_time=0)
    two_cars.handle_rider_request(rider)
    assert two_cars.dijkstra_evaluations == 2

    no_cars = make_simulation(num_riders=0, num_cars=0)
    unmatched = Rider("R2", (0, 0), (100, 100), request_time=0)
    no_cars.handle_rider_request(unmatched)
    assert unmatched.status == "unmatched"


def test_unreachable_candidate_is_skipped() -> None:
    simulation = make_simulation(num_riders=0, num_cars=0)
    for node_id in simulation.graph.adjacency_list:
        simulation.graph.adjacency_list[node_id] = []
    simulation.graph.add_edge("N02_03", "N03_03", 10.0, bidirectional=True)
    unreachable_car = Car("CAR_A", (0, 0))
    reachable_car = Car("CAR_B", (200, 300))
    for car in (unreachable_car, reachable_car):
        simulation.cars[car.id] = car
        simulation.add_available_car(car)
    rider = Rider("R1", (300, 300), (200, 300), request_time=0)
    simulation.handle_rider_request(rider)
    assert reachable_car.assigned_rider is rider
    assert unreachable_car.status == "available"
    assert simulation.dijkstra_evaluations == 2


def test_entirely_unreachable_set_is_consistent() -> None:
    simulation = make_simulation(num_riders=0, num_cars=0)
    for node_id in simulation.graph.adjacency_list:
        simulation.graph.adjacency_list[node_id] = []
    car = Car("CAR_A", (0, 0))
    simulation.cars[car.id] = car
    simulation.add_available_car(car)
    rider = Rider("R1", (300, 300), (200, 300), request_time=0)
    simulation.handle_rider_request(rider)
    assert rider.status == "unmatched"
    assert car.status == "available"
    assert car.id in simulation.available_cars


def test_complete_run_reinserts_cars_and_finishes_active_trips(tmp_path: Path) -> None:
    simulation = make_simulation()
    metrics = simulation.run()
    assert len(simulation.events) == 0
    assert all(car.status == "available" for car in simulation.cars.values())
    assert all(car.assigned_rider is None for car in simulation.cars.values())
    assert set(simulation.available_cars) == set(simulation.available_car_points)
    assert set(simulation.available_cars) == set(simulation.cars)
    assert metrics["total_riders"] == 8
    assert metrics["completed_riders"] + metrics["unmatched_or_unsuccessful"] == 8
    assert simulation.current_time >= 0
    assert "TIME 0.00: EVENT 0 RIDER_REQUEST" in simulation.event_log
    assert "TIME 0.00: EVENT 1 RIDER_REQUEST" in simulation.event_log
    output = tmp_path / "simulation_summary.png"
    simulation.create_visualization(str(output))
    assert output.exists() and output.stat().st_size > 10_000


def main() -> None:
    simulation = make_simulation(num_riders=10)
    metrics = simulation.run()
    output = Path(__file__).with_name("simulation_summary.png")
    simulation.create_visualization(str(output))
    assert all(car.status == "available" for car in simulation.cars.values())
    assert set(simulation.available_cars) == set(simulation.cars)
    print("\nDemonstration metrics:")
    for name, value in metrics.items():
        print(f"  {name}: {value}")
    print(f"\nCreated {output.name}")
    print("All integrated simulation checks passed.")


if __name__ == "__main__":
    main()
