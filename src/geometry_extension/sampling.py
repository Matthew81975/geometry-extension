"""Uniform sampling of planar regions."""

import math
import operator
import random
from collections.abc import Sequence

Point = tuple[float, float]


def random_points_in_region(
    vertices: Sequence[Point],
    count: int,
    radius: float = 1.0,
    *,
    rng: random.Random | None = None,
) -> list[Point]:
    """Sample uniformly inside a simple polygon or a disk.

    Supply vertices in boundary order for a polygon without holes.
    A single vertex is the disk center. Radius applies only to disks.
    """
    count = operator.index(count)
    if count < 0:
        raise ValueError("count must be nonnegative")
    if len(vertices) < 3 and len(vertices) != 1:
        raise ValueError("Provide one center or at least three polygon vertices")
    if any(not math.isfinite(x) or not math.isfinite(y) for x, y in vertices):
        raise ValueError("Vertex coordinates must be finite")

    rng = random.Random() if rng is None else rng
    points: list[Point] = []
    if len(vertices) == 1:
        if not math.isfinite(radius) or radius <= 0:
            raise ValueError("Circle radius must be finite and positive")
        cx, cy = vertices[0]
        for _ in range(count):
            angle = math.tau * rng.random()
            distance = radius * math.sqrt(rng.random())
            points.append((cx + distance * math.cos(angle), cy + distance * math.sin(angle)))
        return points

    xs, ys = zip(*vertices)
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    width, height = max_x - min_x, max_y - min_y
    if not (0 < width < math.inf and 0 < height < math.inf):
        raise ValueError("Polygon must have finite, positive width and height")

    # Normalize to avoid overflow or underflow in area and crossing calculations.
    normalized = [((x - min_x) / width, (y - min_y) / height) for x, y in vertices]
    edges = list(zip(normalized, normalized[1:] + normalized[:1]))
    if math.fsum(ax * by - bx * ay for (ax, ay), (bx, by) in edges) == 0:
        raise ValueError("Polygon must enclose a positive area")

    while len(points) < count:
        x, y = rng.random(), rng.random()
        inside = False
        for (ax, ay), (bx, by) in edges:
            if (ay > y) != (by > y):
                crossing_x = ax + ((y - ay) / (by - ay)) * (bx - ax)
                if x < crossing_x:
                    inside = not inside
        if inside:
            points.append((min_x + width * x, min_y + height * y))
    return points
