"""Dimension-independent oriented area bivectors for planar polygon faces."""
from math import sqrt, isfinite


def face_bivector(vertices):
    """Return the antisymmetric n x n area matrix for an oriented planar face.

    B[i][j] = 1/2 sum_k (u_k[i] v_k[j] - u_k[j] v_k[i]).
    Vertices are boundary ordered; the polygon must be simple and planar.
    """
    points = [tuple(p) for p in vertices]
    if len(points) < 3:
        raise ValueError("A face needs at least three vertices")
    n = len(points[0])
    if n < 2 or any(len(p) != n for p in points):
        raise ValueError("Vertex dimensions must agree and be at least two")
    if any(not isfinite(x) for p in points for x in p):
        raise ValueError("Vertices must be finite")
    origin = points[0]
    matrix = [[0.0] * n for _ in range(n)]
    for k in range(1, len(points) - 1):
        u = [points[k][i] - origin[i] for i in range(n)]
        v = [points[k + 1][i] - origin[i] for i in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                value = 0.5 * (u[i] * v[j] - u[j] * v[i])
                matrix[i][j] += value
                matrix[j][i] -= value
    return tuple(tuple(row) for row in matrix)


def face_area(vertices):
    """Unsigned planar face area, using the bivector Euclidean norm."""
    bivector = face_bivector(vertices)
    return sqrt(sum(bivector[i][j] ** 2
                    for i in range(len(bivector))
                    for j in range(i + 1, len(bivector))))


def face_normal(vertices):
    """Unit oriented normal in 3D; undefined for zero-area faces."""
    bivector = face_bivector(vertices)
    if len(bivector) != 3:
        raise ValueError("A unique normal requires 3D vertices")
    dual = (bivector[1][2], bivector[2][0], bivector[0][1])
    norm = sqrt(sum(v * v for v in dual))
    if norm == 0:
        raise ValueError("Zero-area face has no normal")
    return tuple(v / norm for v in dual)
