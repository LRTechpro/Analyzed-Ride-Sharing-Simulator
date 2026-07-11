"""Simple execution test for the ride-sharing simulator classes."""

from car import Car
from rider import Rider
from simulation import Simulation


def main() -> None:
    """Create sample objects and verify that the classes work together."""
    car = Car("CAR001", (10, 5))
    rider = Rider("RIDER_A", (1, 2), (20, 15))
    simulation = Simulation()

    # Store each object by its unique ID for average O(1) dictionary lookup.
    simulation.cars[car.id] = car
    simulation.riders[rider.id] = rider

    print(car)
    print(rider)
    print(simulation)


if __name__ == "__main__":
    main()
