"""Renderer-independent placement ghost and directional bounding shadows.

The host renderer draws fluorescent mesh edges and filled projected polygons.
All geometry is in world coordinates; no lighting or physics is required.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import sqrt
from typing import Sequence

Vec3 = tuple[float, float, float]
Face = tuple[int, ...]


def _dot(a: Vec3, b: Vec3) -> float:
    return sum(x*y for x,y in zip(a,b))


def _unit(v: Vec3) -> Vec3:
    length=sqrt(_dot(v,v))
    if length<=1e-12:
        raise ValueError("direction must be nonzero")
    return tuple(x/length for x in v)


def _hull(points: Sequence[tuple[float,float]]) -> tuple[tuple[float,float],...]:
    """Convex hull for conservative projections; collinear points collapse."""
    p=sorted(set(points))
    if len(p)<=1:
        return tuple(p)
    def cross(o,a,b):
        return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lower=[]
    for x in p:
        while len(lower)>=2 and cross(lower[-2],lower[-1],x)<=0:
            lower.pop()
        lower.append(x)
    upper=[]
    for x in reversed(p):
        while len(upper)>=2 and cross(upper[-2],upper[-1],x)<=0:
            upper.pop()
        upper.append(x)
    return tuple(lower[:-1]+upper[:-1])


@dataclass(frozen=True)
class Ghost:
    """Geometry for an unrestricted placement preview.

    vertices are object-local. faces describe the visible mesh; the original
    mesh is not mutated. The ground projection uses a conservative convex hull,
    while the camera shadow is a directional bounding rectangle.
    """
    vertices: tuple[Vec3,...]
    faces: tuple[Face,...] = ()
    position: Vec3 = (0.0,0.0,0.0)
    fluorescent_color: tuple[float,float,float] = (0.2,1.0,0.8)

    def __post_init__(self):
        if not self.vertices:
            raise ValueError("ghost requires vertices")
        if any(len(v)!=3 for v in self.vertices):
            raise ValueError("vertices must be 3D")
        if any(len(face)<2 or any(i<0 or i>=len(self.vertices) for i in face) for face in self.faces):
            raise ValueError("invalid face indices")

    def world_vertices(self) -> tuple[Vec3,...]:
        return tuple(tuple(a+b for a,b in zip(v,self.position)) for v in self.vertices)

    def mesh_edges(self) -> tuple[tuple[Vec3,Vec3],...]:
        vertices=self.world_vertices()
        pairs=set()
        for face in self.faces:
            for a,b in zip(face,face[1:]+face[:1]):
                if a!=b:
                    pairs.add(tuple(sorted((a,b))))
        return tuple((vertices[a],vertices[b]) for a,b in sorted(pairs))

    def ground_shadow(self, height: float = 0.0) -> tuple[Vec3,...]:
        """Conservative ground footprint on horizontal y=height plane."""
        outline=_hull([(x,z) for x,y,z in self.world_vertices()])
        return tuple((x,height,z) for x,z in outline)

    def camera_shadow(self, camera_direction: Vec3) -> tuple[Vec3,...]:
        """Directional bounding rectangle in a plane normal to camera view."""
        forward=_unit(camera_direction)
        reference=(0.0,1.0,0.0) if abs(forward[1])<0.9 else (1.0,0.0,0.0)
        right=_unit((reference[1]*forward[2]-reference[2]*forward[1],
                     reference[2]*forward[0]-reference[0]*forward[2],
                     reference[0]*forward[1]-reference[1]*forward[0]))
        up=(forward[1]*right[2]-forward[2]*right[1],
            forward[2]*right[0]-forward[0]*right[2],
            forward[0]*right[1]-forward[1]*right[0])
        vertices=self.world_vertices()
        origin=tuple(sum(p[i] for p in vertices)/len(vertices) for i in range(3))
        uv=[(_dot(tuple(p[i]-origin[i] for i in range(3)),right),
             _dot(tuple(p[i]-origin[i] for i in range(3)),up)) for p in vertices]
        xmin,xmax=min(x for x,y in uv),max(x for x,y in uv)
        ymin,ymax=min(y for x,y in uv),max(y for x,y in uv)
        return tuple(tuple(origin[i]+x*right[i]+y*up[i] for i in range(3))
                     for x,y in ((xmin,ymin),(xmax,ymin),(xmax,ymax),(xmin,ymax)))
