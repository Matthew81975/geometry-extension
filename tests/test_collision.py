from geometry_extension import moving_bounds_may_collide, obb_overlap_3d, travel_oriented_box

def cube(cx=0.0):
    return [(cx+x,y,z) for x in (-1,1) for y in (-1,1) for z in (-1,1)]

def test_separated_directional_boxes_reject():
    a=travel_oriented_box(cube(0),(1,0,0))
    b=travel_oriented_box(cube(10),(-1,0,0))
    assert not obb_overlap_3d(a,b)

def test_touching_directional_boxes_overlap():
    a=travel_oriented_box(cube(0),(1,0,0))
    b=travel_oriented_box(cube(2),(1,0,0))
    assert obb_overlap_3d(a,b)

def test_sweeps_detect_possible_collision():
    assert moving_bounds_may_collide(cube(0),(5,0,0),cube(10),(-5,0,0),1.0)

def test_sweeps_reject_parallel_separated_motion():
    assert not moving_bounds_may_collide(cube(0),(5,0,0),cube(20),(5,0,0),1.0)
