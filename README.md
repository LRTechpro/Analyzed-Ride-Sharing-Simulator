# Efficient, Analyzed Ride-Sharing Simulator

## Purpose/Design

This project is the first milestone of an efficient ride-sharing simulation. It uses object-oriented design to model `Car`, `Rider`, and `Simulation` objects as separate, reusable Python classes. Cars and riders are stored in dictionaries keyed by their unique IDs so they can be retrieved efficiently in average O(1) time as the project grows.

## Project Structure

- `car.py`: Defines the `Car` class.
- `rider.py`: Defines the `Rider` class.
- `simulation.py`: Defines the `Simulation` controller class.
- `test_simulation.py`: Creates sample objects and confirms the classes work together.

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
```

## Dependencies

None. The project uses only the Python standard library.

## Python Version

Python 3.10 or newer is recommended.
