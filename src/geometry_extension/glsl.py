"""Generate GLSL 330 distance functions from supported immutable SDF trees.

Uses expressions, not string evaluation. Unsupported nodes fail explicitly.
Reference: https://iquilezles.org/articles/distfunctions/
"""
from __future__ import annotations

import math
from .sdf import Sphere, Box, Capsule, Translate, Union, Intersection, Difference, SmoothUnion


def _f(value: float) -> str:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("GLSL numeric parameters must be finite")
    return format(value, ".17g") + (".0" if float(value).is_integer() else "")


def _v(point: tuple[float, float, float]) -> str:
    return "vec3(" + ", ".join(_f(v) for v in point) + ")"


def glsl_expression(field: object, point: str = "p") -> str:
    """Return a GLSL expression evaluating the field at the supplied vec3 variable."""
    if isinstance(field, Sphere):
        return f"(length(({point}) - {_v(field.center)}) - {_f(field.radius)})"
    if isinstance(field, Box):
        q = f"(abs(({point}) - {_v(field.center)}) - {_v(field.half_extents)})"
        return f"(length(max({q}, vec3(0.0))) + min(max({q}.x, max({q}.y, {q}.z)), 0.0))"
    if isinstance(field, Capsule):
        a, b = _v(field.start), _v(field.end)
        ba = f"({b} - {a})"
        pa = f"(({point}) - {a})"
        denom = sum((v-u)**2 for u, v in zip(field.start, field.end))
        if denom == 0:
            return f"(length({pa}) - {_f(field.radius)})"
        h = f"clamp(dot({pa}, {ba}) / {_f(denom)}, 0.0, 1.0)"
        return f"(length({pa} - {ba} * {h}) - {_f(field.radius)})"
    if isinstance(field, Translate):
        return glsl_expression(field.field, f"(({point}) - {_v(field.offset)})")
    if isinstance(field, (Union, Intersection, Difference, SmoothUnion)):
        a = glsl_expression(field.a, point)
        b = glsl_expression(field.b, point)
        if isinstance(field, Union):
            return f"min({a}, {b})"
        if isinstance(field, Intersection):
            return f"max({a}, {b})"
        if isinstance(field, Difference):
            return f"max({a}, -({b}))"
        k = _f(field.width)
        h = f"clamp(0.5 + 0.5 * (({b}) - ({a})) / {k}, 0.0, 1.0)"
        return f"mix(({b}), ({a}), {h}) - {k} * {h} * (1.0 - {h})"
    raise TypeError(f"Unsupported GLSL field: {type(field).__name__}")


def glsl_function(field: object, name: str = "scene_distance") -> str:
    """Emit a complete GLSL float function with a fixed, safe identifier."""
    if not name.isidentifier() or not name.isascii() or name.startswith("gl_"):
        raise ValueError("invalid GLSL function identifier")
    return f"float {name}(vec3 p) {{\n    return {glsl_expression(field)};\n}}\n"
