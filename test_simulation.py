"""Verification and console demonstration for the event-driven prototype."""

from pathlib import Path

from car import Car
from rider import Rider
from simulation import Simulation, calculate_travel_time

MAP_FILE = Path(__file__).with_name("map.csv")


def build_simulation() -> Simulation:
    """Create a reproducible scenario with two cars and three riders."""
    simulation = Simulation(str(MAP_FILE))

    cars = [
        Car("CAR001", (0.0, 0.0)),
        Car("CAR002", (40.0, 40.0)),
    ]
    riders = [
        Rider("RIDER_A", (5.0, 2.0), (12.0, 8.0), request_time=0.0),
        Rider("RIDER_B", (35.0, 38.0), (45.0, 42.0), request_time=3.0),
        Rider("RIDER_C", (14.0, 10.0), (20.0, 15.0), request_time=25.0),
    ]

    simulation.cars.update({car.id: car for car in cars})
    simulation.riders.update({rider.id: rider for rider in riders})
    return simulation


def verify_final_state(simulation: Simulation) -> None:
    """Confirm that all trips completed and all car state is consistent."""
    assert calculate_travel_time((0.0, 0.0), (5.0, 2.0)) == 7.0
    assert all(rider.status == "completed" for rider in simulation.riders.values())
    assert all(car.status == "available" for car in simulation.cars.values())
    assert all(car.assigned_rider is None for car in simulation.cars.values())
    assert simulation.cars["CAR001"].location == (20.0, 15.0)
    assert simulation.cars["CAR002"].location == (45.0, 42.0)
    assert simulation.current_time == 40.0


def main() -> None:
    """Run the event engine, print its log, and verify the final state."""
    simulation = build_simulation()
    simulation.run()
    verify_final_state(simulation)

    print("\nFinal fleet state:")
    for car in simulation.cars.values():
        print(f"  {car}")

    print("\nAll simulation engine checks passed.")


if __name__ == "__main__":
    main()
