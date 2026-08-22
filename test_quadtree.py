"""Correctness and performance demonstration for the Quadtree spatial index."""

from __future__ import annotations

import random
import time

from quadtree import Point, Quadtree, Rectangle


def distance_squared(first: Point, second: Point) -> float:
    """Return the squared Euclidean distance between two points."""
    return (first.x - second.x) ** 2 + (first.y - second.y) ** 2


def brute_force_nearest(points: list[Point], query_point: Point) -> Point | None:
    """Find the nearest point by scanning the entire list in O(N) time."""
    if not points:
        return None
    return min(points, key=lambda point: distance_squared(point, query_point))


def build_test_data(
    number_of_points: int = 5_000,
) -> tuple[list[Point], Point]:
    """Create reproducible driver locations and one rider query location."""
    random_generator = random.Random(549)
    points = [
        Point(
            random_generator.uniform(0, 1000),
            random_generator.uniform(0, 1000),
            data=f"Driver-{index:04d}",
        )
        for index in range(number_of_points)
    ]
    query_point = Point(
        random_generator.uniform(0, 1000),
        random_generator.uniform(0, 1000),
        data="Rider",
    )
    return points, query_point


def test_nearest_matches_brute_force() -> None:
    """Verify Quadtree results against brute force for several queries."""
    points, first_query = build_test_data()
    quadtree = Quadtree(Rectangle(0, 0, 1000, 1000), capacity=4)
    assert all(quadtree.insert(point) for point in points)

    random_generator = random.Random(550)
    queries = [first_query]
    queries.extend(
        Point(
            random_generator.uniform(0, 1000),
            random_generator.uniform(0, 1000),
            data=f"Verification-Rider-{index}",
        )
        for index in range(25)
    )

    for query_point in queries:
        assert quadtree.find_nearest(query_point) is brute_force_nearest(
            points,
            query_point,
        )


def test_k_nearest_matches_brute_force() -> None:
    """Verify the pruned k-nearest search and its edge cases."""
    points, query = build_test_data(500)
    quadtree = Quadtree(Rectangle(0, 0, 1000, 1000), capacity=4)
    assert all(quadtree.insert(point) for point in points)
    expected = sorted(
        points,
        key=lambda point: distance_squared(point, query),
    )[:5]
    assert quadtree.find_k_nearest(query) == expected
    assert len(quadtree.find_k_nearest(query, k=900)) == 500
    try:
        quadtree.find_k_nearest(query, k=0)
    except ValueError:
        pass
    else:
        raise AssertionError("A nonpositive k must be rejected.")


def test_remove_uses_point_identity_at_duplicate_coordinates() -> None:
    """Remove one colocated car without removing another object."""
    quadtree = Quadtree(Rectangle(0, 0, 100, 100), capacity=1)
    first = Point(50, 50, data="CAR001")
    second = Point(50, 50, data="CAR002")
    assert quadtree.insert(first) and quadtree.insert(second)
    assert quadtree.remove(first) is True
    assert quadtree.remove(first) is False
    assert quadtree.find_nearest(Point(50, 50)) is second


def main() -> None:
    """Run the required 5,000-point correctness and timing comparison."""
    points, query_point = build_test_data()
    quadtree = Quadtree(Rectangle(0, 0, 1000, 1000), capacity=4)

    for point in points:
        assert quadtree.insert(point), f"Point outside boundary: {point}"

    quadtree_start = time.perf_counter()
    quadtree_result = quadtree.find_nearest(query_point)
    quadtree_elapsed = (time.perf_counter() - quadtree_start) * 1000

    brute_force_start = time.perf_counter()
    brute_force_result = brute_force_nearest(points, query_point)
    brute_force_elapsed = (time.perf_counter() - brute_force_start) * 1000

    assert quadtree_result is brute_force_result
    assert quadtree_result is not None

    test_k_nearest_matches_brute_force()
    test_remove_uses_point_identity_at_duplicate_coordinates()

    distance = distance_squared(quadtree_result, query_point) ** 0.5
    print("--- Quadtree Nearest-Neighbor Verification ---")
    print(f"Indexed driver points: {len(points):,}")
    print(f"Query point:            {query_point}")
    print(f"Quadtree result:        {quadtree_result}")
    print(f"Brute-force result:     {brute_force_result}")
    print(f"Distance:               {distance:.4f}")
    print(f"Results identical:      {quadtree_result is brute_force_result}")
    print()
    print(f"Quadtree search time:   {quadtree_elapsed:.6f} ms")
    print(f"Brute-force time:       {brute_force_elapsed:.6f} ms")
    if quadtree_elapsed > 0:
        print(
            "Observed speedup:        "
            f"{brute_force_elapsed / quadtree_elapsed:.2f}x"
        )
    print("\nAll Quadtree correctness checks passed.")


if __name__ == "__main__":
    main()
