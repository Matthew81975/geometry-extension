from math import isclose, pi

from geometry_extension import directional_extrema, rotation_between, support_point


def test_support_point():
    pts = [(-2, 0), (1, 3), (4, -1)]
    assert support_point(pts, (1, 0)) == (4.0, -1.0)


def test_directional_extrema():
    lo, hi = directional_extrema([(-2, 1), (3, 2), (1, 9)], (1, 0))
    assert lo[0] == -2
    assert hi[0] == 3


def test_rotation_between_quarter_turn():
    axis, angle = rotation_between((1, 0, 0), (0, 1, 0))
    assert all(isclose(a, b, abs_tol=1e-12) for a, b in zip(axis, (0, 0, 1)))
    assert isclose(angle, pi/2)
