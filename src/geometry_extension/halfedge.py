"""Oriented half-edge topology for consistently wound manifold meshes.

Face loops are counterclockwise when viewed from outside. A half-edge's
origin and destination follow its face loop; its twin runs in reverse.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import atan2, sqrt
from typing import Sequence

Vec3=tuple[float,float,float]


def _sub(a:Vec3,b:Vec3)->Vec3:
    return (a[0]-b[0],a[1]-b[1],a[2]-b[2])


def _cross(a:Vec3,b:Vec3)->Vec3:
    return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])


def _dot(a:Vec3,b:Vec3)->float:
    return sum(x*y for x,y in zip(a,b))


def _unit(v:Vec3)->Vec3:
    d=sqrt(_dot(v,v))
    if d<=1e-12:
        raise ValueError("degenerate geometry has no unique direction")
    return tuple(x/d for x in v)


@dataclass(frozen=True)
class HalfEdge:
    origin:int
    destination:int
    face:int
    next:int
    twin:int|None


@dataclass(frozen=True)
class EdgeGeometry:
    vertices:tuple[int,int]
    faces:tuple[int,...]
    classification:str
    signed_angle:float|None
    alignment:float|None
    representative_normal:Vec3|None


class HalfEdgeMesh:
    """Immutable vertex and face topology with explicit directed half-edges.

    For a closed orientable manifold, outward face winding makes signed-angle
    classification consistent. Boundary edges are labeled boundary.
    """
    def __init__(self,vertices:Sequence[Vec3],faces:Sequence[Sequence[int]]):
        self.vertices=tuple(tuple(map(float,v)) for v in vertices)
        self.faces=tuple(tuple(face) for face in faces)
        directed={}
        half=[]
        for fi,face in enumerate(self.faces):
            if len(face)<3 or len(set(face))!=len(face):
                raise ValueError("faces must contain at least three distinct vertices")
            if any(v<0 or v>=len(self.vertices) for v in face):
                raise ValueError("face vertex index out of range")
            start=len(half)
            for i,a in enumerate(face):
                b=face[(i+1)%len(face)]
                if (a,b) in directed:
                    raise ValueError("inconsistent winding or non-manifold directed edge")
                directed[a,b]=len(half)
                half.append((a,b,fi,start+(i+1)%len(face)))
        self.half_edges=tuple(HalfEdge(a,b,f,n,directed.get((b,a))) for a,b,f,n in half)
        counts={}
        for a,b in directed:
            key=tuple(sorted((a,b)))
            counts[key]=counts.get(key,0)+1
        if any(v>2 for v in counts.values()):
            raise ValueError("non-manifold edge")
        self.face_normals=tuple(self._face_normal(face) for face in self.faces)

    def _face_normal(self,face:tuple[int,...])->Vec3:
        # Newell normal supports convex and planar polygon faces.
        x=y=z=0.0
        for i,a in enumerate(face):
            p=self.vertices[a]
            q=self.vertices[face[(i+1)%len(face)]]
            x+=(p[1]-q[1])*(p[2]+q[2])
            y+=(p[2]-q[2])*(p[0]+q[0])
            z+=(p[0]-q[0])*(p[1]+q[1])
        return _unit((x,y,z))

    def edges(self)->tuple[EdgeGeometry,...]:
        result=[]
        visited=set()
        for h in self.half_edges:
            key=tuple(sorted((h.origin,h.destination)))
            if key in visited:
                continue
            visited.add(key)
            if h.twin is None:
                result.append(EdgeGeometry(key,(h.face,),"boundary",None,None,None))
                continue
            n1=self.face_normals[h.face]
            other=self.half_edges[h.twin]
            n2=self.face_normals[other.face]
            t=_unit(_sub(self.vertices[h.destination],self.vertices[h.origin]))
            alignment=max(-1.0,min(1.0,_dot(n1,n2)))
            angle=atan2(_dot(t,_cross(n1,n2)),alignment)
            if abs(angle)<1e-9:
                kind="flat"
            elif angle>0:
                kind="convex"
            else:
                kind="concave"
            summed=tuple(a+b for a,b in zip(n1,n2))
            try:
                normal=_unit(summed)
            except ValueError:
                normal=None
            result.append(EdgeGeometry(key,(h.face,other.face),kind,angle,alignment,normal))
        return tuple(result)

    def corner_normal(self,vertex:int)->Vec3|None:
        """Equal-weight normal of distinct incident faces."""
        if vertex<0 or vertex>=len(self.vertices):
            raise IndexError(vertex)
        ids=[i for i,face in enumerate(self.faces) if vertex in face]
        if not ids:
            return None
        s=tuple(sum(self.face_normals[i][axis] for i in ids) for axis in range(3))
        try:
            return _unit(s)
        except ValueError:
            return None
