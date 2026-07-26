"""Simple execution test for the ride-sharing simulator classes."""

from car import Car
from rider import Rider
from simulation import Simulation


def main() -> None:
    """Create sample objects and verify that the classes work together."""
    car = Car("CAR001", "A")
    rider = Rider("RIDER_A", "A", "D")
    simulation = Simulation("map.csv")

    # Store each object by its unique ID for average O(1) dictionary lookup.
    simulation.cars[car.id] = car
    simulation.riders[rider.id] = rider

    car.calculate_route(rider.destination, simulation.map)

    print(car)
    print(rider)
    print(simulation)
    print(simulation.map)
    print(f"Planned route: {car.route}")
    print(f"Route time: {car.route_time:g}")


if __name__ == "__main__":
    main()
