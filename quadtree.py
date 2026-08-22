"""Spatial index for efficient nearest-driver searches.

The public ``Quadtree`` class owns the map boundary and delegates storage and
recursive searching to ``QuadtreeNode`` objects.  Points may represent drivers,
riders, or any other object with two-dimensional coordinates.
"""

from __future__ import annotations

from dataclasses import dataclass
import heapq
from itertools import count
from math import inf
from typing import Any


@dataclass(frozen=True, slots=True)
class Point:
    """Represent a location and its optional application payload."""

    x: float
    y: float
    data: Any = None

    def __repr__(self) -> str:
        label = f", data={self.data!r}" if self.data is not None else ""
        return f"Point(x={self.x:.2f}, y={self.y:.2f}{label})"


@dataclass(frozen=True, slots=True)
class Rectangle:
    """Represent an axis-aligned rectangular map region."""

    x: float
    y: float
    width: float
    height: float

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Rectangle width and height must be positive.")

    def contains(self, point: Point) -> bool:
        """Return whether *point* lies inside or on this rectangle."""
        return (
            self.x <= point.x <= self.x + self.width
            and self.y <= point.y <= self.y + self.height
        )

    def distance_squared_to(self, point: Point) -> float:
        """Return the squared shortest distance from *point* to this region."""
        dx = max(0.0, self.x - point.x, point.x - (self.x + self.width))
        dy = max(0.0, self.y - point.y, point.y - (self.y + self.height))
        return dx * dx + dy * dy


class QuadtreeNode:
    """Store points for one rectangular region of a Quadtree."""

    def __init__(
        self,
        boundary: Rectangle,
        capacity: int = 4,
        *,
        depth: int = 0,
        max_depth: int = 32,
    ) -> None:
        if capacity < 1:
            raise ValueError("Quadtree capacity must be at least 1.")

        self.boundary = boundary
        self.capacity = capacity
        self.points: list[Point] = []
        self.divided = False

        self.northwest: QuadtreeNode | None = None
        self.northeast: QuadtreeNode | None = None
        self.southwest: QuadtreeNode | None = None
        self.southeast: QuadtreeNode | None = None

        self._depth = depth
        self._max_depth = max_depth

    def subdivide(self) -> None:
        """Create four child nodes and redistribute this node's points."""
        if self.divided:
            return

        half_width = self.boundary.width / 2
        half_height = self.boundary.height / 2
        x = self.boundary.x
        y = self.boundary.y
        child_options = {
            "capacity": self.capacity,
            "depth": self._depth + 1,
            "max_depth": self._max_depth,
        }

        self.northwest = QuadtreeNode(
            Rectangle(x, y, half_width, half_height), **child_options
        )
        self.northeast = QuadtreeNode(
            Rectangle(x + half_width, y, half_width, half_height), **child_options
        )
        self.southwest = QuadtreeNode(
            Rectangle(x, y + half_height, half_width, half_height), **child_options
        )
        self.southeast = QuadtreeNode(
            Rectangle(
                x + half_width,
                y + half_height,
                half_width,
                half_height,
            ),
            **child_options,
        )
        self.divided = True

        existing_points = self.points
        self.points = []
        for point in existing_points:
            self._child_for(point).insert(point)

    def _children(self) -> tuple[QuadtreeNode, ...]:
        """Return all child nodes after subdivision."""
        if not self.divided:
            return ()

        assert self.northwest is not None
        assert self.northeast is not None
        assert self.southwest is not None
        assert self.southeast is not None
        return (
            self.northwest,
            self.northeast,
            self.southwest,
            self.southeast,
        )

    def _child_for(self, point: Point) -> QuadtreeNode:
        """Select exactly one child, including points on dividing lines."""
        assert self.divided
        midpoint_x = self.boundary.x + self.boundary.width / 2
        midpoint_y = self.boundary.y + self.boundary.height / 2
        west = point.x < midpoint_x
        north = point.y < midpoint_y

        if north and west:
            assert self.northwest is not None
            return self.northwest
        if north:
            assert self.northeast is not None
            return self.northeast
        if west:
            assert self.southwest is not None
            return self.southwest

        assert self.southeast is not None
        return self.southeast

    def insert(self, point: Point) -> bool:
        """Recursively insert *point* if it belongs to this region."""
        if not self.boundary.contains(point):
            return False

        if self.divided:
            return self._child_for(point).insert(point)

        # The depth limit prevents endless subdivision for duplicate locations.
        if len(self.points) < self.capacity or self._depth >= self._max_depth:
            self.points.append(point)
            return True

        self.subdivide()
        return self._child_for(point).insert(point)

    def find_nearest(
        self,
        query_point: Point,
        best_point: Point | None = None,
        minimum_distance_squared: float = inf,
    ) -> tuple[Point | None, float]:
        """Recursively return the nearest point and its squared distance."""
        # Prune the entire branch when its closest possible location is already
        # farther away than the best actual point found so far.
        if self.boundary.distance_squared_to(query_point) > minimum_distance_squared:
            return best_point, minimum_distance_squared

        for point in self.points:
            distance_squared = (
                (point.x - query_point.x) ** 2
                + (point.y - query_point.y) ** 2
            )
            if distance_squared < minimum_distance_squared:
                best_point = point
                minimum_distance_squared = distance_squared

        # Visiting the most promising region first usually finds a close point
        # early, shrinking the search radius and enabling more pruning.
        children = sorted(
            self._children(),
            key=lambda child: child.boundary.distance_squared_to(query_point),
        )
        for child in children:
            best_point, minimum_distance_squared = child.find_nearest(
                query_point,
                best_point,
                minimum_distance_squared,
            )

        return best_point, minimum_distance_squared

    def find_k_nearest(
        self,
        query_point: Point,
        k: int,
        candidates: list[tuple[float, int, Point]],
        tie_breaker: count,
    ) -> None:
        """Populate a size-k max-heap while pruning distant branches."""
        farthest = -candidates[0][0] if len(candidates) == k else inf
        if self.boundary.distance_squared_to(query_point) > farthest:
            return

        for point in self.points:
            distance_squared = (
                (point.x - query_point.x) ** 2
                + (point.y - query_point.y) ** 2
            )
            entry = (-distance_squared, -next(tie_breaker), point)
            if len(candidates) < k:
                heapq.heappush(candidates, entry)
            elif distance_squared < -candidates[0][0]:
                heapq.heapreplace(candidates, entry)

        children = sorted(
            self._children(),
            key=lambda child: child.boundary.distance_squared_to(query_point),
        )
        for child in children:
            farthest = -candidates[0][0] if len(candidates) == k else inf
            if child.boundary.distance_squared_to(query_point) <= farthest:
                child.find_k_nearest(query_point, k, candidates, tie_breaker)

    def remove(self, point: Point) -> bool:
        """Remove the exact Point object previously inserted."""
        if not self.boundary.contains(point):
            return False
        for index, stored_point in enumerate(self.points):
            if stored_point is point:
                del self.points[index]
                return True
        if self.divided:
            return self._child_for(point).remove(point)
        return False


class Quadtree:
    """Provide the public interface for a two-dimensional spatial index."""

    def __init__(
        self,
        boundary: Rectangle,
        capacity: int = 4,
        *,
        max_depth: int = 32,
    ) -> None:
        self.boundary = boundary
        self.root = QuadtreeNode(
            boundary,
            capacity,
            max_depth=max_depth,
        )

    def insert(self, point: Point) -> bool:
        """Insert a point, returning False when it is outside the map."""
        return self.root.insert(point)

    def find_nearest(self, query_point: Point) -> Point | None:
        """Return the closest stored point, or None when the tree is empty."""
        nearest, _ = self.root.find_nearest(query_point)
        return nearest

    def find_k_nearest(self, query_point: Point, k: int = 5) -> list[Point]:
        """Return up to k points in nearest-to-farthest order."""
        if k <= 0:
            raise ValueError("k must be a positive integer.")
        candidates: list[tuple[float, int, Point]] = []
        self.root.find_k_nearest(query_point, k, candidates, count())
        return [
            entry[2]
            for entry in sorted(
                candidates,
                key=lambda entry: (-entry[0], -entry[1]),
            )
        ]

    def remove(self, point: Point) -> bool:
        """Remove an inserted Point by object identity."""
        return self.root.remove(point)
