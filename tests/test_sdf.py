import math
import pytest
from geometry_extension.sdf import (
    Sphere, Box, Capsule, Union, Intersection, Difference,
    SmoothUnion, Translate, smooth_min, normal,
)


def test_sphere_signed_distance():
    s = Sphere((0, 0, 0), 2)
    assert s.distance((0, 0, 0)) == -2
    assert s.distance((2, 0, 0)) == 0
    assert s.distance((5, 0, 0)) == 3


def test_box_exact_inside_outside():
    b = Box((0, 0, 0), (1, 2, 3))
    assert b.distance((0, 0, 0)) == -1
    assert b.distance((1, 0, 0)) == 0
    assert b.distance((2, 3, 3)) == pytest.approx(math.sqrt(2))


def test_capsule_endcaps_and_degenerate_segment():
    c = Capsule((0, 0, 0), (0, 2, 0), 0.5)
    assert c.distance((0, 1, 0)) == -0.5
    assert c.distance((0, 3, 0)) == 0.5
    assert Capsule((1, 0, 0), (1, 0, 0), 1).distance((1, 0, 0)) == -1


def test_boolean_and_translation():
    a = Sphere((0, 0, 0), 2)
    b = Sphere((3, 0, 0), 2)
    p = (0, 0, 0)
    assert Union(a, b).distance(p) == -2
    assert Intersection(a, b).distance(p) == 1
    assert Difference(a, b).distance(p) == -1
    assert Translate(a, (5, 0, 0)).distance((5, 0, 0)) == -2


def test_smooth_union_and_normal():
    a = Sphere((-0.5, 0, 0), 1)
    b = Sphere((0.5, 0, 0), 1)
    assert SmoothUnion(a, b, 1).distance((0, 0, 0)) < Union(a, b).distance((0, 0, 0))
    assert normal(Sphere((0, 0, 0), 1), (1, 0, 0)) == pytest.approx((1, 0, 0))
    assert smooth_min(1, 4, 1) == 1


def test_invalid_parameters():
    with pytest.raises(ValueError):
        Sphere((0, 0, 0), -1)
    with pytest.raises(ValueError):
        smooth_min(0, 1, 0)
    with pytest.raises(ValueError):
        normal(Sphere((0, 0, 0), 1), (0, 0, 0))
