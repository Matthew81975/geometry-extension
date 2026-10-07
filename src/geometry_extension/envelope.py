"""Sampled outer convex envelopes from support half-spaces."""
from dataclasses import dataclass
from .directions import directions_circle,directions_sphere
from .support import support_point

@dataclass(frozen=True)
class SupportPlane:
    normal: tuple[float,...]
    offset: float
    contact_point: tuple[float,...]

def sampled_support_envelope(points,directions):
    pts=[tuple(map(float,p)) for p in points]
    if not pts: raise ValueError("points must not be empty")
    out=[]
    for d in directions:
        n=tuple(map(float,d)); p=support_point(pts,n)
        out.append(SupportPlane(n,sum(a*b for a,b in zip(p,n)),p))
    return tuple(out)

def support_envelope_2d(points,angular_samples=64):
    return sampled_support_envelope(points,directions_circle(angular_samples))

def support_envelope_3d(points,angular_samples=256):
    return sampled_support_envelope(points,directions_sphere(angular_samples))
