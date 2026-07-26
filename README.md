# Efficient, Analyzed Ride-Sharing Simulator

## Purpose and Design

This project models the core components of a ride-sharing platform with clean,
reusable Python classes. `Car`, `Rider`, `Graph`, and `Simulation` encapsulate
the actors and state of the system. Cars and riders are stored in dictionaries
by unique ID for average O(1) lookup, while the city map uses a weighted,
directed adjacency list loaded from CSV.

## Project Structure

- `car.py`: Defines the `Car` class and its route-planning method.
- `rider.py`: Defines the `Rider` class.
- `graph.py`: Defines the weighted `Graph` and CSV-loading logic.
- `pathfinding.py`: Implements Dijkstra's shortest-path algorithm.
- `map.csv`: Defines the city nodes, roads, and travel times.
- `simulation.py`: Stores cars, riders, and the city map.
- `test_dijkstra.py`: Verifies standalone and car-integrated pathfinding.
- `test_simulation.py`: Demonstrates the complete object model.

## Pathfinding with Dijkstra's Algorithm

`find_shortest_path(graph, start_node, end_node)` calculates the fastest route
through the map. It uses Python's `heapq` module as a min-priority queue. Each
heap entry is a `(distance, node)` tuple, so the closest known node is processed
first.

The algorithm maintains:

- a distance dictionary containing the best travel time found for each node;
- a predecessor dictionary used to reconstruct the final route;
- a min-heap containing nodes that may still improve the route.

For the included map, the fastest route from `A` to `D` is
`A -> C -> D`, with a total travel time of 4. If a route is unavailable, the
function returns `(None, float("inf"))`.

`Car.calculate_route(destination, graph)` starts from the car's current
`location`, calls the pathfinding function, and stores the result in the car's
`route` and `route_time` attributes.

### Complexity

With an adjacency list and a binary min-heap, Dijkstra's algorithm runs in
`O((V + E) log V)` time, commonly written as `O(E log V)` for a connected
graph. The distance and predecessor dictionaries require `O(V)` space, while
stale entries can make the heap grow to `O(E)`, giving `O(V + E)` auxiliary
space in the worst case.

## Map Data Format

Each `map.csv` row describes one directed road:

```text
start_node,end_node,travel_time
```

For example, `A,B,5` creates a road from `A` to `B` with a travel time of 5.
A two-way street requires one row for each direction. The loader accepts an
optional header, ignores blank rows, validates three-column rows, and rejects
negative weights.

## How to Run

Use Python 3.10 or newer. No third-party packages are required.

Run the required Dijkstra demonstration:

```bash
python test_dijkstra.py
```

Expected result:

```text
Standalone Dijkstra result:
  Path: ['A', 'C', 'D']
  Total travel time: 4

Car.calculate_route() result:
  Car location: A
  Destination: D
  Car route: ['A', 'C', 'D']
  Car route_time: 4

All pathfinding checks passed.
```

Run the full simulation demonstration:

```bash
python test_simulation.py
```

If `pytest` is installed, the same pathfinding checks can also be collected
automatically:

```bash
python -m pytest -q
```
