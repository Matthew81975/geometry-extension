"""Broad-phase collision tests for directional oriented boxes."""
from __future__ import annotations
from math import sqrt
from .travel import OrientedBox3D, swept_travel_box

_EPS=1e-10

def _dot(a,b): return sum(x*y for x,y in zip(a,b))
def _cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def _norm(v): return sqrt(_dot(v,v))
def _sub(a,b): return tuple(x-y for x,y in zip(a,b))

def obb_overlap_3d(a: OrientedBox3D,b: OrientedBox3D,tolerance=1e-10):
    """Separating-axis test for two 3D OBBs.

    Tests the 3 axes of each box plus their 9 pairwise cross-product axes.
    """
    delta=_sub(b.center,a.center)
    axes=list(a.axes)+list(b.axes)
    for u in a.axes:
        for v in b.axes:
            c=_cross(u,v)
            n=_norm(c)
            if n>_EPS: axes.append(tuple(x/n for x in c))
    for axis in axes:
        center_distance=abs(_dot(delta,axis))
        ra=sum(h*abs(_dot(ax,axis)) for h,ax in zip(a.half_extents,a.axes))
        rb=sum(h*abs(_dot(ax,axis)) for h,ax in zip(b.half_extents,b.axes))
        if center_distance>ra+rb+tolerance:
            return False
    return True

def moving_bounds_may_collide(points_a,velocity_a,points_b,velocity_b,dt,
                              acceleration_a=(0.0,0.0,0.0),
                              acceleration_b=(0.0,0.0,0.0)):
    """Cheap conservative broad-phase query over one timestep.

    False guarantees the two swept directional boxes do not overlap.
    True means only that narrow-phase collision work may be necessary.
    """
    a=swept_travel_box(points_a,velocity_a,dt,acceleration_a)
    b=swept_travel_box(points_b,velocity_b,dt,acceleration_b)
    return obb_overlap_3d(a,b)
