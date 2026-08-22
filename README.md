# Efficient, Analyzed Ride-Sharing Simulator

This project is a deterministic discrete-event ride-sharing simulation. It
integrates a coordinate-aware road graph, Dijkstra shortest-path routing, a
Quadtree spatial index, dynamic rider generation, fleet state management,
performance metrics, and a final analytical visualization.

## Installation

Python 3.10 or newer is required.

```bash
python -m pip install -r requirements.txt
```

Matplotlib is the only third-party runtime dependency.

## Project Files

- `simulation.py`: event engine, dynamic requests, matching, metrics, CLI, and visualization
- `car.py`: coordinate-based car state and route calculation
- `rider.py`: rider state and timing fields
- `graph.py`: unified map loader, adjacency list, coordinates, and vertex snapping
- `pathfinding.py`: Dijkstra shortest-path algorithm
- `quadtree.py`: insertion, identity-based removal, and pruned k-nearest search
- `city_map.csv`: unified road topology and graph-node coordinates
- `run_tests.py`: complete repeatable verification without pytest
- `test_*.py`: focused correctness tests
- `simulation_summary.png`: generated final map, metrics, and outcome chart

## How to Run

Run the full simulation with the required default candidate count of five:

```bash
python simulation.py --max-time 200 --num-riders 25 --num-cars 100
```

Run a short video demonstration that begins with two simultaneous events:

```bash
python simulation.py --max-time 40 --num-riders 10 --num-cars 5 --simultaneous-demo
```

The event log is printed in chronological order. The completed analytical
output is saved as `simulation_summary.png`.

Run all correctness checks:

```bash
python run_tests.py
```

If pytest is installed, the test files can also be collected with:

```bash
python -m pytest -q
```

## Command-Line Options

| Option | Default | Purpose |
|---|---:|---|
| `--max-time` | `200` | Latest allowed rider-request generation time |
| `--num-riders` | `25` | Maximum riders generated |
| `--num-cars` | `100` | Initial fleet size |
| `--candidate-count` | `5` | Maximum Quadtree candidates evaluated per request |
| `--random-seed` | `549` | Makes generated inputs repeatable |
| `--mean-arrival-time` | `8` | Mean exponential rider-arrival interval |
| `--map-file` | `city_map.csv` | Unified graph and coordinate file |
| `--summary-file` | `simulation_summary.png` | Visualization output path |
| `--simultaneous-demo` | off | Schedules two initial requests at time zero |

When both generation limits are supplied, generation stops when either limit
is reached. Pickup and drop-off events already in the heap continue so active
trips finish and the metrics remain consistent.

## Unified Map Format

Every `city_map.csv` row defines one bidirectional road:

```text
start_node_id,start_x,start_y,end_node_id,end_x,end_y,weight
N00_00,0,0,N01_00,100,0,10
```

The graph stores roads in `adjacency_list` and physical node locations in
`node_coordinates`. `find_nearest_vertex()` snaps arbitrary car or rider
coordinates to the closest graph node before routing.

## Event Engine

The min-heap stores only four-field events:

```text
(timestamp, sequence_number, event_type, data)
```

Supported event types are:

- `RIDER_REQUEST`
- `PICKUP_ARRIVAL`
- `DROPOFF_ARRIVAL`

The timestamp orders events chronologically. A unique sequence number from
`itertools.count()` preserves scheduling order when timestamps match and
prevents `heapq` from comparing `Car` or `Rider` objects.

## State Transitions

Cars follow:

```text
available -> en_route_to_pickup -> en_route_to_destination -> available
```

Riders follow:

```text
waiting -> in_car -> completed
```

A rider becomes `unmatched` when no car is available or every candidate route
is unreachable. A rider becomes `unsuccessful` if the destination becomes
unreachable after pickup. The recovery path records elapsed busy time, clears
the assignment, and returns the car to availability at the pickup coordinates.
No event is scheduled at infinity.

## Quadtree-to-Dijkstra Matching

For every rider request:

1. The available-car Quadtree returns up to `k` geographically nearest cars.
2. `k` defaults to five and can be changed with `--candidate-count`.
3. Dijkstra runs for every returned candidate.
4. Unreachable candidates are skipped.
5. The reachable car with the smallest road-network travel time is selected.
6. Travel-time ties are resolved deterministically by candidate order and car ID.

The Quadtree uses recursive rectangle-distance pruning and a size-k heap. It
does not perform a full scan and sort as its primary k-nearest algorithm.

## Availability Invariant

The simulation maintains three synchronized structures:

- `available_cars`: car ID to `Car`
- `available_car_points`: car ID to the exact immutable `Point`
- `available_car_quadtree`: spatial index containing only available cars

All changes go through `add_available_car()` and `remove_available_car()`.
Dispatch removes the exact Point by object identity before changing the car's
status. The car stays absent during pickup and passenger travel. Drop-off
updates its coordinates and inserts a new Point at the destination. This also
handles multiple cars at identical coordinates correctly.

## Metrics

The simulation reports:

- total riders generated
- completed riders
- unmatched or unsuccessful riders
- average wait time: `pickup_time - request_time`
- average completed-trip duration: `dropoff_time - pickup_time`
- trips completed per car through `car.trips_completed`
- number of Dijkstra evaluations
- driver utilization

Driver utilization is defined as:

```text
sum of all car busy times / (number of cars * final processed event time)
```

The final processed event time is used because active trips may finish after
rider generation stops.

## Analytical Visualization

`simulation_summary.png` combines:

- the road network and final location of every car
- major simulation metrics
- a completed-versus-unmatched rider chart

The chronological console log remains available for debugging and the code
review demonstration.

## Complexity

- Dijkstra with an adjacency list and binary heap: `O((V + E) log V)` time
- Quadtree insertion and search: approximately `O(log N)` on balanced data,
  with `O(N)` worst-case search for highly clustered points
- Event scheduling and removal: `O(log M)` for `M` pending events
- Graph, Quadtree, fleet, rider, and event state: linear auxiliary space

## Correctness Coverage

`run_tests.py` verifies equal-timestamp ordering, four-field events, coordinate
snapping, Dijkstra routes, k-nearest ordering, nonpositive k rejection, exact
Point identity removal, fewer than five cars, no available cars, unreachable
candidates, all-unreachable candidate sets, dispatch exclusion, finite event
times, completed-trip reinsertion, availability synchronization, active-trip
completion, metrics, and PNG creation.
