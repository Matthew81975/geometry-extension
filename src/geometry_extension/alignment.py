"""Vector alignment operators in 3D."""

from __future__ import annotations
from math import acos, sqrt
from typing import Sequence

Vector3 = Sequence[float]


def _v(v: Vector3) -> tuple[float, float, float]:
    if len(v) != 3:
        raise ValueError("3D vector required")
    return tuple(map(float, v))  # type: ignore[return-value]


def _dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def _unit(v):
    v = _v(v)
    n = sqrt(_dot(v, v))
    if n == 0:
        raise ValueError("zero vector cannot be aligned")
    return tuple(x/n for x in v)


def rotation_between(source: Vector3, target: Vector3):
    """Return axis-angle (axis, radians) rotating source onto target."""
    a, b = _unit(source), _unit(target)
    c = max(-1.0, min(1.0, _dot(a, b)))
    axis = _cross(a, b)
    n = sqrt(_dot(axis, axis))
    if n < 1e-12:
        if c > 0:
            return (1.0, 0.0, 0.0), 0.0
        trial = (1.0, 0.0, 0.0) if abs(a[0]) < 0.9 else (0.0, 1.0, 0.0)
        axis = _unit(_cross(a, trial))
        return axis, acos(-1.0)
    return tuple(x/n for x in axis), acos(c)


def align_vector_to_vector(vector: Vector3, target: Vector3):
    return rotation_between(vector, target)


def align_vector_to_point(vector: Vector3, origin: Vector3, point: Vector3):
    o, p = _v(origin), _v(point)
    return rotation_between(vector, tuple(b-a for a, b in zip(o, p)))


def align_vector_to_plane(vector: Vector3, plane_normal: Vector3):
    """Return the smallest rotation placing vector parallel to a plane."""
    v, n = _unit(vector), _unit(plane_normal)
    projected = tuple(x - _dot(v, n)*y for x, y in zip(v, n))
    if sqrt(_dot(projected, projected)) < 1e-12:
        trial = (1.0, 0.0, 0.0) if abs(n[0]) < 0.9 else (0.0, 1.0, 0.0)
        projected = _cross(n, trial)
    return rotation_between(v, projected)
