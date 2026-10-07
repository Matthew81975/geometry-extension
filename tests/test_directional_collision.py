from geometry_extension import directional_collision_box_2d, directional_collision_box_3d

def test_2d_directional_box_uses_d_and_perpendicular_extrema():
    pts=[(-2,-1),(2,-1),(2,1),(-2,1)]
    box=directional_collision_box_2d(pts,(1,0))
    assert box["extrema"]==((-2.0,2.0),(-1.0,1.0))
    assert box["half_extents"]==(2.0,1.0)

def test_2d_direction_can_rotate_box():
    pts=[(-1,-1),(1,-1),(1,1),(-1,1)]
    box=directional_collision_box_2d(pts,(1,1))
    assert len(box["extrema"])==2
    assert box["axes"][0][0]>0 and box["axes"][0][1]>0

def test_3d_directional_box_has_three_directional_half_extents():
    cube=[(x,y,z) for x in (-1,1) for y in (-1,1) for z in (-1,1)]
    box=directional_collision_box_3d(cube,(1,0,0))
    assert box.half_extents==(1.0,1.0,1.0)
