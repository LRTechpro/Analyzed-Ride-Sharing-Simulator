"""Tests for coordinate snapping and Dijkstra routing."""

from pathlib import Path

from car import Car
from graph import Graph, find_nearest_vertex
from pathfinding import find_shortest_path

MAP_FILE = Path(__file__).with_name("city_map.csv")


def load_map() -> Graph:
    graph = Graph()
    graph.load_map_data(str(MAP_FILE))
    return graph


def test_graph_loads_topology_and_geometry() -> None:
    graph = load_map()
    assert graph.node_coordinates["N00_00"] == (0.0, 0.0)
    assert ("N01_00", 10.0) in graph.adjacency_list["N00_00"]
    assert ("N00_00", 10.0) in graph.adjacency_list["N01_00"]


def test_nearest_vertex_and_shortest_path() -> None:
    graph = load_map()
    assert find_nearest_vertex((12.0, 8.0), graph.node_coordinates) == "N00_00"
    route, travel_time = find_shortest_path(graph, "N00_00", "N02_02")
    assert route is not None
    assert route[0] == "N00_00" and route[-1] == "N02_02"
    assert travel_time == 40.0


def test_car_calculate_route_uses_coordinates() -> None:
    graph = load_map()
    car = Car("CAR001", (4.0, 3.0))
    route, travel_time = car.calculate_route((295.0, 205.0), graph)
    assert route is not None
    assert route[0] == "N00_00" and route[-1] == "N03_02"
    assert travel_time == 50.0
    assert car.route == route and car.route_time == travel_time


def test_no_available_path() -> None:
    graph = Graph()
    graph.node_coordinates = {
        "A": (0.0, 0.0),
        "B": (1.0, 0.0),
        "C": (5.0, 5.0),
    }
    graph.add_edge("A", "B", 2.0, bidirectional=True)
    graph.adjacency_list.setdefault("C", [])
    assert find_shortest_path(graph, "A", "C") == (None, float("inf"))


def main() -> None:
    test_graph_loads_topology_and_geometry()
    test_nearest_vertex_and_shortest_path()
    test_car_calculate_route_uses_coordinates()
    test_no_available_path()
    print("All graph, snapping, and Dijkstra checks passed.")


if __name__ == "__main__":
    main()
