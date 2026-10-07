"""Support mappings and directional extrema for sampled geometry."""

from __future__ import annotations
from math import sqrt
from typing import Iterable, Sequence

Point = Sequence[float]


def _dot(a: Point, b: Point) -> float:
    if len(a) != len(b):
        raise ValueError("vectors must have the same dimension")
    return sum(float(x) * float(y) for x, y in zip(a, b))


def _unit(v: Point) -> tuple[float, ...]:
    n = sqrt(_dot(v, v))
    if n == 0.0:
        raise ValueError("direction must be nonzero")
    return tuple(float(x) / n for x in v)


def support_point(points: Iterable[Point], direction: Point) -> tuple[float, ...]:
    """Return the point maximizing dot(point, direction)."""
    u = _unit(direction)
    pts = [tuple(map(float, p)) for p in points]
    if not pts:
        raise ValueError("points must not be empty")
    if any(len(p) != len(u) for p in pts):
        raise ValueError("point and direction dimensions must match")
    return max(pts, key=lambda p: _dot(p, u))


def support_value(points: Iterable[Point], direction: Point) -> float:
    """Return max dot(point, unit(direction))."""
    u = _unit(direction)
    p = support_point(points, u)
    return _dot(p, u)


def directional_extrema(points: Iterable[Point], direction: Point):
    """Return (minimum_point, maximum_point) along a direction."""
    u = _unit(direction)
    pts = [tuple(map(float, p)) for p in points]
    if not pts:
        raise ValueError("points must not be empty")
    if any(len(p) != len(u) for p in pts):
        raise ValueError("point and direction dimensions must match")
    return min(pts, key=lambda p: _dot(p, u)), max(pts, key=lambda p: _dot(p, u))
