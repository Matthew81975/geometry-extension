"""Direction samplers for support-function geometry."""
from math import cos, pi, sin, sqrt

def directions_circle(count):
    if count<3: raise ValueError("count must be >= 3")
    return tuple((cos(2*pi*i/count),sin(2*pi*i/count)) for i in range(count))

def directions_sphere(count):
    if count<4: raise ValueError("count must be >= 4")
    golden_angle=pi*(3.0-sqrt(5.0)); out=[]
    for i in range(count):
        z=1.0-2.0*(i+0.5)/count; r=sqrt(max(0.0,1.0-z*z)); theta=golden_angle*i
        out.append((r*cos(theta),r*sin(theta),z))
    return tuple(out)
