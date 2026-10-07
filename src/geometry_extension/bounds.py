"""Bounding geometry built from directional extrema."""
from __future__ import annotations
from dataclasses import dataclass
from math import cos, pi, sin
from .support import directional_extrema

@dataclass(frozen=True)
class OrientedBox2D:
    center: tuple[float,float]
    axis_u: tuple[float,float]
    axis_v: tuple[float,float]
    half_extents: tuple[float,float]
    angle: float
    @property
    def area(self): return 4.0*self.half_extents[0]*self.half_extents[1]
    @property
    def corners(self):
        cx,cy=self.center; ux,uy=self.axis_u; vx,vy=self.axis_v; hu,hv=self.half_extents
        return tuple((cx+su*hu*ux+sv*hv*vx,cy+su*hu*uy+sv*hv*vy) for su,sv in ((-1,-1),(1,-1),(1,1),(-1,1)))

def oriented_box_2d(points, angle=0.0):
    pts=[tuple(map(float,p)) for p in points]
    if not pts: raise ValueError("points must not be empty")
    if any(len(p)!=2 for p in pts): raise ValueError("2D points required")
    u=(cos(angle),sin(angle)); v=(-sin(angle),cos(angle))
    u0,u1=directional_extrema(pts,u); v0,v1=directional_extrema(pts,v)
    pu0=sum(a*b for a,b in zip(u0,u)); pu1=sum(a*b for a,b in zip(u1,u))
    pv0=sum(a*b for a,b in zip(v0,v)); pv1=sum(a*b for a,b in zip(v1,v))
    cu,cv=(pu0+pu1)/2,(pv0+pv1)/2
    return OrientedBox2D((cu*u[0]+cv*v[0],cu*u[1]+cv*v[1]),u,v,((pu1-pu0)/2,(pv1-pv0)/2),angle)

def minimum_sampled_box_2d(points, angular_samples=180):
    if angular_samples<1: raise ValueError("angular_samples must be >= 1")
    pts=list(points)
    return min((oriented_box_2d(pts,(pi/2)*i/angular_samples) for i in range(angular_samples)),key=lambda b:b.area)
