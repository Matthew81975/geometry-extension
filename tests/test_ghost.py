import pytest
from geometry_extension.ghost import Ghost


def test_ghost_projection_and_translation():
    g=Ghost(((0,0,0),(2,0,0),(2,3,1),(0,3,1)),((0,1,2,3),),(5,7,9))
    assert g.ground_shadow()==((5,0.0,9),(7,0.0,9),(7,0.0,10),(5,0.0,10))
    assert len(g.mesh_edges())==4
    assert g.vertices[0]==(0,0,0)


def test_camera_direction_bounds():
    g=Ghost(((0,0,0),(2,3,4)))
    p=g.camera_shadow((0,0,-1))
    assert len(p)==4
    assert all(abs(v[2]-2)<1e-10 for v in p)
    assert max(v[0] for v in p)-min(v[0] for v in p)==pytest.approx(2)
    assert max(v[1] for v in p)-min(v[1] for v in p)==pytest.approx(3)


def test_invalid_geometry_and_direction():
    with pytest.raises(ValueError):
        Ghost(())
    with pytest.raises(ValueError):
        Ghost(((0,0,0),),((0,2),))
    with pytest.raises(ValueError):
        Ghost(((0,0,0),)).camera_shadow((0,0,0))
