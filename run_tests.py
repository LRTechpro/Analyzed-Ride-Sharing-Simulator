"""Run the complete verification suite without requiring pytest."""

from pathlib import Path
from tempfile import TemporaryDirectory

import test_dijkstra
import test_quadtree
import test_simulation


def main() -> None:
    tests = [
        test_dijkstra.test_graph_loads_topology_and_geometry,
        test_dijkstra.test_nearest_vertex_and_shortest_path,
        test_dijkstra.test_car_calculate_route_uses_coordinates,
        test_dijkstra.test_no_available_path,
        test_quadtree.test_nearest_matches_brute_force,
        test_quadtree.test_k_nearest_matches_brute_force,
        test_quadtree.test_remove_uses_point_identity_at_duplicate_coordinates,
        test_simulation.test_event_tuple_and_equal_timestamp_order,
        test_simulation.test_k_candidates_and_dispatch_availability,
        test_simulation.test_fewer_than_five_and_no_available_cars,
        test_simulation.test_unreachable_candidate_is_skipped,
        test_simulation.test_entirely_unreachable_set_is_consistent,
    ]
    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
    with TemporaryDirectory() as folder:
        test_simulation.test_complete_run_reinserts_cars_and_finishes_active_trips(
            Path(folder)
        )
    print("PASS: test_complete_run_reinserts_cars_and_finishes_active_trips")
    print("\nAll final-project tests passed.")


if __name__ == "__main__":
    main()
