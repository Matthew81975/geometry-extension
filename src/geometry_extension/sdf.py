"""Composable signed-distance geometry inspired by Iñigo Quílez's articles.

Negative inside, zero at the boundary, positive outside.  Smooth CSG
and nonuniform transforms generally produce implicit fields rather than
exact Euclidean signed distances.
Reference: https://iquilezles.org/articles/distfunctions/
"""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Protocol, TypeAlias

Vec3: TypeAlias = tuple[float, float, float]


def _sub(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _length(v: Vec3) -> float:
    return sqrt(sum(x * x for x in v))


class DistanceField(Protocol):
    def distance(self, point: Vec3) -> float: ...


@dataclass(frozen=True)
class Sphere:
    center: Vec3
    radius: float

    def __post_init__(self) -> None:
        if self.radius < 0:
            raise ValueError("radius must be nonnegative")

    def distance(self, point: Vec3) -> float:
        return _length(_sub(point, self.center)) - self.radius


@dataclass(frozen=True)
class Box:
    center: Vec3
    half_extents: Vec3

    def __post_init__(self) -> None:
        if any(v < 0 for v in self.half_extents):
            raise ValueError("half_extents must be nonnegative")

    def distance(self, point: Vec3) -> float:
        q = tuple(abs(p - c) - h for p, c, h in zip(point, self.center, self.half_extents))
        return _length(tuple(max(v, 0.0) for v in q)) + min(max(q), 0.0)


@dataclass(frozen=True)
class Capsule:
    start: Vec3
    end: Vec3
    radius: float

    def __post_init__(self) -> None:
        if self.radius < 0:
            raise ValueError("radius must be nonnegative")

    def distance(self, point: Vec3) -> float:
        axis = _sub(self.end, self.start)
        offset = _sub(point, self.start)
        denom = sum(x*x for x in axis)
        t = max(0.0, min(1.0, sum(a*b for a, b in zip(offset, axis)) / denom)) if denom else 0.0
        return _length(tuple(a - t*b for a, b in zip(offset, axis))) - self.radius


@dataclass(frozen=True)
class Translate:
    field: DistanceField
    offset: Vec3

    def distance(self, point: Vec3) -> float:
        return self.field.distance(_sub(point, self.offset))


@dataclass(frozen=True)
class Union:
    a: DistanceField
    b: DistanceField

    def distance(self, point: Vec3) -> float:
        return min(self.a.distance(point), self.b.distance(point))


@dataclass(frozen=True)
class Intersection:
    a: DistanceField
    b: DistanceField

    def distance(self, point: Vec3) -> float:
        return max(self.a.distance(point), self.b.distance(point))


@dataclass(frozen=True)
class Difference:
    a: DistanceField
    b: DistanceField

    def distance(self, point: Vec3) -> float:
        return max(self.a.distance(point), -self.b.distance(point))


def smooth_min(a: float, b: float, k: float) -> float:
    """Polynomial smooth minimum; k is the blend width, must be positive."""
    if k <= 0:
        raise ValueError("blend width must be positive")
    h = max(0.0, min(1.0, 0.5 + 0.5 * (b - a) / k))
    return b * (1.0 - h) + a * h - k * h * (1.0 - h)


@dataclass(frozen=True)
class SmoothUnion:
    a: DistanceField
    b: DistanceField
    width: float

    def __post_init__(self) -> None:
        if self.width <= 0:
            raise ValueError("blend width must be positive")

    def distance(self, point: Vec3) -> float:
        return smooth_min(self.a.distance(point), self.b.distance(point), self.width)


def normal(field: DistanceField, point: Vec3, epsilon: float = 1e-5) -> Vec3:
    """Central-difference unit normal where the gradient is nonzero."""
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")
    components = []
    for i in range(3):
        delta = tuple(epsilon if j == i else 0.0 for j in range(3))
        plus = tuple(p + d for p, d in zip(point, delta))
        minus = tuple(p - d for p, d in zip(point, delta))
        components.append(field.distance(plus) - field.distance(minus))
    norm = sqrt(sum(v*v for v in components))
    if norm == 0:
        raise ValueError("normal undefined at a zero-gradient point")
    return tuple(v/norm for v in components)
