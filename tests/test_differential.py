import pytest
from geometry_extension.sdf import Sphere, Box, Capsule, Union, Translate
from geometry_extension.differential import gradient, unit_normal, laplacian


def test_sphere_analytic_gradient_and_laplacian():
    s=Sphere((0,0,0),1)
    assert gradient(s,(2,0,0))==pytest.approx((1,0,0))
    assert unit_normal(s,(0,3,0))==pytest.approx((0,1,0))
    assert laplacian(s,(2,0,0))==pytest.approx(1.0,rel=1e-4)


def test_box_outside_and_inside():
    b=Box((0,0,0),(1,2,3))
    assert gradient(b,(3,0,0))==pytest.approx((1,0,0))
    assert gradient(b,(0.5,0,0))==pytest.approx((1,0,0))


def test_capsule_and_composition():
    c=Capsule((0,0,0),(0,2,0),1)
    assert gradient(c,(2,1,0))==pytest.approx((1,0,0))
    assert gradient(Translate(c,(5,0,0)),(7,1,0))==pytest.approx((1,0,0))
    assert gradient(Union(Sphere((0,0,0),1),Sphere((10,0,0),1)),(2,0,0))==pytest.approx((1,0,0))


def test_invalid_step_and_singular_normal():
    s=Sphere((0,0,0),1)
    with pytest.raises(ValueError):
        gradient(s,(2,0,0),0)
    with pytest.raises(ValueError):
        laplacian(s,(2,0,0),0)
    with pytest.raises(ValueError):
        unit_normal(s,(0,0,0))
