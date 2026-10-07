"""Travel-aligned 3D frames and swept collision bounds."""
from __future__ import annotations
from dataclasses import dataclass
from math import sqrt

def _dot(a,b): return sum(x*y for x,y in zip(a,b))
def _cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def _unit(v):
    v=tuple(map(float,v)); n=sqrt(_dot(v,v))
    if n<=1e-15: raise ValueError("velocity/direction must be nonzero")
    return tuple(x/n for x in v)

@dataclass(frozen=True)
class TravelFrame3D:
    forward: tuple[float,float,float]
    side: tuple[float,float,float]
    up: tuple[float,float,float]

@dataclass(frozen=True)
class OrientedBox3D:
    center: tuple[float,float,float]
    axes: tuple[tuple[float,float,float],tuple[float,float,float],tuple[float,float,float]]
    half_extents: tuple[float,float,float]
    @property
    def volume(self): return 8.0*self.half_extents[0]*self.half_extents[1]*self.half_extents[2]

def travel_frame(velocity,up_hint=(0.0,0.0,1.0)):
    f=_unit(velocity); hint=_unit(up_hint)
    if abs(_dot(f,hint))>0.999:
        hint=(0.0,1.0,0.0) if abs(f[1])<0.999 else (1.0,0.0,0.0)
    side=_unit(_cross(f,hint))
    up=_unit(_cross(side,f))
    return TravelFrame3D(f,side,up)

def travel_oriented_box(points,velocity,up_hint=(0.0,0.0,1.0)):
    pts=[tuple(map(float,p)) for p in points]
    if not pts: raise ValueError("points must not be empty")
    if any(len(p)!=3 for p in pts): raise ValueError("3D points required")
    frame=travel_frame(velocity,up_hint); axes=(frame.forward,frame.side,frame.up)
    intervals=[]
    for axis in axes:
        q=[_dot(p,axis) for p in pts]; intervals.append((min(q),max(q)))
    mids=[(a+b)/2 for a,b in intervals]
    center=tuple(sum(mids[i]*axes[i][j] for i in range(3)) for j in range(3))
    half=tuple((b-a)/2 for a,b in intervals)
    return OrientedBox3D(center,axes,half)

def swept_travel_box(points,velocity,dt,acceleration=(0.0,0.0,0.0),up_hint=(0.0,0.0,1.0)):
    """OBB enclosing the object at t=0 and its predicted translated position at dt."""
    if dt<0: raise ValueError("dt must be nonnegative")
    pts=[tuple(map(float,p)) for p in points]
    v=tuple(map(float,velocity)); a=tuple(map(float,acceleration))
    if len(v)!=3 or len(a)!=3: raise ValueError("3D velocity and acceleration required")
    displacement=tuple(v[i]*dt+0.5*a[i]*dt*dt for i in range(3))
    moved=[tuple(p[i]+displacement[i] for i in range(3)) for p in pts]
    return travel_oriented_box(pts+moved,velocity,up_hint)
