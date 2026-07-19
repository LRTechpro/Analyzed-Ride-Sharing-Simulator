# Efficient, Analyzed Ride-Sharing Simulator

## Purpose/Design

This project is an efficient ride-sharing simulation built through progressive milestones. It uses object-oriented design to model `Car`, `Rider`, `Graph`, and `Simulation` objects as separate, reusable Python classes. Cars and riders are stored in dictionaries keyed by their unique IDs for average O(1) lookup. The weighted, directed city map is loaded from an external CSV file into a dictionary-based adjacency list.

## Project Structure

- `car.py`: Defines the `Car` class.
- `rider.py`: Defines the `Rider` class.
- `graph.py`: Defines the weighted, directed `Graph` class and CSV-loading logic.
- `map.csv`: Defines the city nodes, roads, and travel times.
- `simulation.py`: Defines the `Simulation` controller and loads the city map.
- `test_simulation.py`: Creates sample objects and demonstrates the integrated graph.

## Map Data Format

Each row in `map.csv` describes one directed road using three comma-separated values:

```text
start_node,end_node,travel_time
```

For example, `A,B,5` creates a directed road from node `A` to node `B` with a travel time of 5 units. A two-way street requires two rows: one for each direction. The loader accepts an optional header row, ignores blank rows, and converts each travel time to a numeric weight.

## How to Run

1. Open a terminal in the project folder.
2. Run:

```bash
python test_simulation.py
```

Expected output:

```text
Car CAR001 at (10, 5) - Status: available
Rider RIDER_A at (1, 2) waiting for ride to (20, 15)
Simulation with 1 car(s) and 1 rider(s)
--- City Map Adjacency List ---
A -> [(B, 5), (C, 3)]
B -> [(A, 5), (D, 4)]
C -> [(A, 3), (D, 1)]
D -> [(B, 4), (C, 1)]
-------------------------------
```

## Dependencies

None. The project uses only the Python standard library.

## Python Version

Python 3.10 or newer is recommended.
