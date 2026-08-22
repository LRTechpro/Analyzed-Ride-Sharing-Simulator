# Assignment 7.2 Video Walkthrough

Target length: 3 to 5 minutes.

## 1. Introduction and Architecture

"This is my final efficient ride-sharing simulator. The completed application
integrates four primary components. The Graph stores road topology, weights,
and node coordinates. The Quadtree indexes only available cars and returns up
to five nearby candidates. Dijkstra evaluates those candidates using actual
road travel time. The Simulation class coordinates the event queue, rider and
car states, metrics, and visualization."

Show `simulation.py`, `graph.py`, `quadtree.py`, and `pathfinding.py` in the
file explorer.

## 2. Four-Field Event Queue

Show `schedule_event()` and `run()` in `simulation.py`.

"Every event is scheduled as timestamp, sequence number, event type, and data.
The timestamp keeps the min-heap chronological. The unique sequence number
from itertools.count protects the heap when timestamps match, because Python
never needs to compare Car or Rider objects. The run loop pops the earliest
event, advances current time, and calls the request, pickup, or drop-off
handler. Active trips continue after rider generation stops."

Show the three event types in `run()`:

- `RIDER_REQUEST`
- `PICKUP_ARRIVAL`
- `DROPOFF_ARRIVAL`

## 3. CLI and Dynamic Rider Requests

Show `build_argument_parser()`, `generate_rider_request()`, and
`_schedule_next_request()`.

"The command-line arguments control maximum generation time, rider count, car
count, candidate count, random seed, and map file. Rider requests are generated
dynamically with exponential arrival intervals. If either generation limit is
reached, no new request is scheduled, but events already in progress finish."

## 4. Unified Map and Matching Pipeline

Show `city_map.csv`, `Graph.load_map_data()`, and `find_nearest_vertex()`.

"The unified CSV connects graph IDs with physical coordinates and weighted
roads. Car and rider coordinates are snapped to their nearest graph vertices
before Dijkstra runs."

Show `handle_rider_request()`.

"For each request, the Quadtree returns up to five geographically close cars.
Dijkstra runs for every returned candidate. Unreachable candidates are skipped,
and the reachable car with the minimum road travel time is selected."

## 5. Availability and State Consistency

Show `add_available_car()` and `remove_available_car()`.

"These centralized methods keep the available-car dictionary, exact Point
dictionary, and Quadtree synchronized. The selected car is removed immediately
at dispatch and stays absent through pickup and passenger travel. Exact object
identity allows two cars at the same coordinates to be removed safely."

Show `handle_pickup_arrival()` and `handle_dropoff_arrival()`.

"At pickup, the car location changes to the rider's start coordinates and
Dijkstra calculates the passenger route. At drop-off, the location changes to
the destination, timing metrics and completed trips are updated, the rider link
is cleared, and a new immutable Point is inserted at the car's new location."

## 6. Live Demonstration

Run:

```bash
python simulation.py --max-time 40 --num-riders 10 --num-cars 5 --simultaneous-demo
```

Point out these first two lines:

```text
TIME 0.00: EVENT 0 RIDER_REQUEST
TIME 0.00: EVENT 1 RIDER_REQUEST
```

"These two requests have the same timestamp but different sequence numbers,
so the heap processes both deterministically without a comparison error. The
remaining log shows multiple riders, dispatches, pickups, drop-offs, and cars
being reinserted at their destinations."

Wait until the console reports that `simulation_summary.png` was saved.

## 7. Results

Open `simulation_summary.png`.

"The integrated visualization shows the road network and final car locations,
the major performance metrics, and a rider-outcome chart. Driver utilization is
total busy time divided by fleet size times the final processed event time. The
final time includes trips that completed after rider generation stopped."

Close with:

"This demonstrates the complete Quadtree-to-Dijkstra matching pipeline inside
a deterministic event-driven simulation, with validated state management,
metrics, and analytical output."
