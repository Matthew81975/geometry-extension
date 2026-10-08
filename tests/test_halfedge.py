import pytest
from geometry_extension.halfedge import HalfEdgeMesh


def test_cube_outside_edges_and_corner_normal():
    vertices=((0,0,0),(1,0,0),(1,1,0),(0,1,0),(0,0,1),(1,0,1),(1,1,1),(0,1,1))
    faces=((0,3,2,1),(4,5,6,7),(0,1,5,4),(3,7,6,2),(0,4,7,3),(1,2,6,5))
    mesh=HalfEdgeMesh(vertices,faces)
    assert len(mesh.half_edges)==24
    assert all(h.twin is not None for h in mesh.half_edges)
    assert len(mesh.edges())==12
    assert all(e.classification=="convex" for e in mesh.edges())
    assert mesh.corner_normal(6)==pytest.approx((1/3**0.5,)*3)


def test_reversed_winding_changes_signed_classification():
    vertices=((0,0,0),(1,0,0),(1,1,0),(0,1,0),(0,0,1),(1,0,1),(1,1,1),(0,1,1))
    faces=((0,3,2,1),(4,5,6,7),(0,1,5,4),(3,7,6,2),(0,4,7,3),(1,2,6,5))
    mesh=HalfEdgeMesh(vertices,tuple(tuple(reversed(f)) for f in faces))
    assert all(e.classification=="concave" for e in mesh.edges())


def test_boundary_and_invalid_winding():
    m=HalfEdgeMesh(((0,0,0),(1,0,0),(0,1,0)),((0,1,2),))
    assert all(e.classification=="boundary" for e in m.edges())
    with pytest.raises(ValueError):
        HalfEdgeMesh(((0,0,0),(1,0,0),(0,1,0),(0,0,1)),((0,1,2),(0,1,3)))
