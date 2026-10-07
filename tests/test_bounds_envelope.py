from math import cos,isclose,pi,sin
from geometry_extension.bounds import minimum_sampled_box_2d,oriented_box_2d
from geometry_extension.directions import directions_circle,directions_sphere
from geometry_extension.envelope import support_envelope_3d

def test_axis_aligned_box():
    b=oriented_box_2d([(-2,-1),(2,-1),(2,1),(-2,1)])
    assert b.center==(0.0,0.0) and b.half_extents==(2.0,1.0) and isclose(b.area,8.0)

def test_minimum_sampled_rotated_rectangle():
    a=pi/4; c,s=cos(a),sin(a); base=[(-2,-1),(2,-1),(2,1),(-2,1)]
    pts=[(x*c-y*s,x*s+y*c) for x,y in base]
    assert isclose(minimum_sampled_box_2d(pts,180).area,8.0,rel_tol=1e-6)

def test_direction_samplers_are_unit():
    for d in directions_circle(17)+directions_sphere(31):
        assert isclose(sum(x*x for x in d),1.0,rel_tol=1e-12)

def test_3d_envelope_contains_cube():
    cube=[(x,y,z) for x in (-1,1) for y in (-1,1) for z in (-1,1)]
    for plane in support_envelope_3d(cube,32):
        assert all(sum(x*n for x,n in zip(p,plane.normal))<=plane.offset+1e-12 for p in cube)
