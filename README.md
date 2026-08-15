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
- `quadtree.py`: Implements the Quadtree spatial index and nearest-neighbor search.
- `map.csv`: Defines the city nodes, roads, and travel times.
- `simulation.py`: Implements the min-heap event engine and prototype logic.
- `test_dijkstra.py`: Verifies standalone and car-integrated pathfinding.
- `test_quadtree.py`: Validates Quadtree results against brute-force search.
- `test_simulation.py`: Demonstrates the complete object model.

## Simulation Engine Prototype

The prototype connects the `Car`, `Rider`, and `Simulation` classes in a
complete discrete-event simulation. Physical locations are represented as
`(x, y)` coordinate tuples. The prototype intentionally uses simplified
matching and navigation so the event loop and state changes can be validated
before Dijkstra pathfinding and the Quadtree are integrated.

Upcoming events are stored in a min-heap as
`(timestamp, sequence_number, event_type, data)` tuples. The timestamp keeps
events chronological, and the sequence number preserves insertion order when
two events have the same timestamp. The `run()` loop removes the earliest
event, advances the simulation clock, and sends it to the correct handler.

For each rider request, `find_closest_car_brute_force()` checks every available
car and returns the closest one. `calculate_travel_time()` uses Manhattan
distance multiplied by `TRAVEL_SPEED_FACTOR`. An `ARRIVAL` event represents
either a pickup or a dropoff. The handler distinguishes them by checking the
car's status. At pickup, the car location changes to the rider's start
coordinates. At dropoff, it changes to the rider's destination, the car becomes
available again, and the rider-car link is cleared.

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

## Quadtree Data Structure

The Quadtree is a two-dimensional spatial index for matching a rider with the
nearest available driver. Instead of scanning every driver in the fleet, it
recursively divides the 1000-by-1000 map into northwest, northeast, southwest,
and southeast regions. Each `QuadtreeNode` holds up to four points before it
subdivides and redistributes those points among its children.

`Quadtree.find_nearest(query_point)` performs a best-first recursive search.
Child regions are ordered by their minimum possible distance from the rider.
Once the search finds a candidate driver, any region whose closest boundary is
farther than that driver is pruned. Every driver in a pruned branch is skipped.
Squared distances are used during comparisons to avoid unnecessary square-root
calculations.

For a reasonably balanced tree and well-distributed points, insertion and
nearest-neighbor search are approximately `O(log N)` on average. A brute-force
nearest-neighbor search is `O(N)` because it always examines every driver.
Quadtree construction requires `O(N)` space. Highly clustered or identical
locations can produce an unbalanced tree, so worst-case search remains `O(N)`;
the implementation also uses a maximum depth to handle duplicate locations
safely.

Run the standalone 5,000-driver verification:

```bash
python test_quadtree.py
```

The script inserts 5,000 reproducible random driver points, selects a rider
location, and runs both the Quadtree and a simple brute-force search. It asserts
that both methods return the exact same `Point` object and prints their results
and observed search times. A successful run ends with:

```text
Results identical:      True

All Quadtree correctness checks passed.
```

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

Run the simulation engine prototype:

```bash
python test_simulation.py
```

The console prints every rider request, dispatch, pickup, and dropoff in
chronological order. A successful run ends with the final car locations and:

```text
All simulation engine checks passed.
```

If `pytest` is installed, the same pathfinding checks can also be collected
automatically:

```bash
python -m pytest -q
```
