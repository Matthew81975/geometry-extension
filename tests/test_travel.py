from math import isclose
from geometry_extension.travel import swept_travel_box,travel_frame,travel_oriented_box

def cube():
    return [(x,y,z) for x in (-1,1) for y in (-1,1) for z in (-1,1)]

def test_travel_frame_follows_velocity():
    f=travel_frame((3,4,0))
    assert f.forward==(0.6,0.8,0.0)
    assert isclose(sum(x*x for x in f.side),1.0)

def test_travel_box_axis_is_velocity():
    b=travel_oriented_box(cube(),(10,0,0))
    assert b.axes[0]==(1.0,0.0,0.0)
    assert b.half_extents==(1.0,1.0,1.0)

def test_swept_box_extends_along_travel():
    b=swept_travel_box(cube(),(10,0,0),0.5)
    assert b.center==(2.5,0.0,0.0)
    assert b.half_extents==(3.5,1.0,1.0)

def test_acceleration_expands_sweep():
    b=swept_travel_box(cube(),(2,0,0),1.0,(4,0,0))
    assert b.center==(2.0,0.0,0.0)
    assert b.half_extents==(3.0,1.0,1.0)
