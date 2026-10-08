"""Analytic and numerical differential queries for implicit geometry.

Analytic gradients are used where unique; discontinuities and singularities
fall back to central differences or report undefined unit normals.
"""
from __future__ import annotations

from math import sqrt
from .sdf import Sphere, Box, Capsule, Translate, Union, Intersection, Difference, DistanceField, Vec3


def gradient(field: DistanceField, point: Vec3, epsilon: float = 1e-5) -> Vec3:
    """Return the spatial derivative of a field, using analytic cases when possible."""
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")
    if isinstance(field, Sphere):
        q = tuple(p-c for p,c in zip(point, field.center))
        r = sqrt(sum(v*v for v in q))
        if r:
            return tuple(v/r for v in q)
    elif isinstance(field, Capsule):
        ba = tuple(b-a for a,b in zip(field.start,field.end))
        pa = tuple(p-a for p,a in zip(point,field.start))
        d = sum(v*v for v in ba)
        t = min(1.0,max(0.0,sum(x*y for x,y in zip(pa,ba))/d)) if d else 0.0
        q = tuple(x-t*y for x,y in zip(pa,ba))
        r = sqrt(sum(v*v for v in q))
        if r:
            return tuple(v/r for v in q)
    elif isinstance(field, Box):
        q = tuple(p-c for p,c in zip(point,field.center))
        outside = tuple(max(abs(v)-h,0.0) for v,h in zip(q,field.half_extents))
        r = sqrt(sum(v*v for v in outside))
        if r:
            return tuple((1.0 if v>0 else -1.0 if v<0 else 0.0)*o/r for v,o in zip(q,outside))
        gaps = tuple(abs(v)-h for v,h in zip(q,field.half_extents))
        axis = max(range(3),key=lambda i:gaps[i])
        if gaps.count(gaps[axis])==1 and q[axis]!=0:
            return tuple((1.0 if q[i]>0 else -1.0) if i==axis else 0.0 for i in range(3))
    elif isinstance(field, Translate):
        return gradient(field.field,tuple(p-o for p,o in zip(point,field.offset)),epsilon)
    elif isinstance(field,(Union,Intersection,Difference)):
        da,db=field.a.distance(point),field.b.distance(point)
        if isinstance(field,Difference):
            db=-db
        if da!=db:
            use_a = da<db if isinstance(field,Union) else da>db
            if use_a:
                return gradient(field.a,point,epsilon)
            g=gradient(field.b,point,epsilon)
            return tuple(-v for v in g) if isinstance(field,Difference) else g
    result=[]
    for axis in range(3):
        delta=tuple(epsilon if i==axis else 0.0 for i in range(3))
        p1=tuple(p+d for p,d in zip(point,delta))
        p0=tuple(p-d for p,d in zip(point,delta))
        result.append((field.distance(p1)-field.distance(p0))/(2*epsilon))
    return tuple(result)


def unit_normal(field: DistanceField, point: Vec3, epsilon: float = 1e-5) -> Vec3:
    """Normalized gradient; raises where the gradient vanishes."""
    g=gradient(field,point,epsilon)
    r=sqrt(sum(v*v for v in g))
    if r<=1e-12:
        raise ValueError("normal undefined at zero gradient")
    return tuple(v/r for v in g)


def laplacian(field: DistanceField, point: Vec3, epsilon: float = 1e-3) -> float:
    """Second-order central-difference Laplacian of an implicit scalar field."""
    if epsilon<=0:
        raise ValueError("epsilon must be positive")
    center=field.distance(point)
    total=0.0
    for axis in range(3):
        delta=tuple(epsilon if i==axis else 0.0 for i in range(3))
        plus=tuple(p+d for p,d in zip(point,delta))
        minus=tuple(p-d for p,d in zip(point,delta))
        total+=field.distance(plus)+field.distance(minus)-2*center
    return total/(epsilon*epsilon)
