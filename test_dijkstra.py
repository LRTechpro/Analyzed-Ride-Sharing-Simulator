"""Verification and console demonstration for Dijkstra pathfinding."""

from pathlib import Path

from car import Car
from graph import Graph
from pathfinding import find_shortest_path

MAP_FILE = Path(__file__).with_name("map.csv")


def load_map() -> Graph:
    """Load and return the sample city map."""
    city_map = Graph()
    city_map.load_from_file(str(MAP_FILE))
    return city_map


def test_standalone_shortest_path() -> None:
    """Verify the standalone algorithm finds the optimal A-to-D route."""
    path, travel_time = find_shortest_path(load_map(), "A", "D")

    assert path == ["A", "C", "D"]
    assert travel_time == 4.0


def test_car_calculate_route() -> None:
    """Verify a car stores its calculated route and travel time."""
    city_map = load_map()
    car = Car("CAR001", "A")

    result = car.calculate_route("D", city_map)

    assert result == (["A", "C", "D"], 4.0)
    assert car.route == ["A", "C", "D"]
    assert car.route_time == 4.0


def test_no_available_path() -> None:
    """Verify unreachable destinations use the required sentinel result."""
    city_map = Graph()
    city_map.add_edge("A", "B", 2)
    city_map.add_edge("C", "D", 3)

    assert find_shortest_path(city_map, "A", "D") == (None, float("inf"))


def main() -> None:
    """Run the checks and print the route-planning demonstration."""
    test_standalone_shortest_path()
    test_car_calculate_route()
    test_no_available_path()

    city_map = load_map()
    path, travel_time = find_shortest_path(city_map, "A", "D")
    print("Standalone Dijkstra result:")
    print(f"  Path: {path}")
    print(f"  Total travel time: {travel_time:g}")

    car = Car("CAR001", "A")
    car.calculate_route("D", city_map)
    print("\nCar.calculate_route() result:")
    print(f"  Car location: {car.location}")
    print(f"  Destination: {car.destination}")
    print(f"  Car route: {car.route}")
    print(f"  Car route_time: {car.route_time:g}")
    print("\nAll pathfinding checks passed.")


if __name__ == "__main__":
    main()
