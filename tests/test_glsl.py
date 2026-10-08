import pytest
from geometry_extension.sdf import Sphere, Box, Capsule, Translate, Union, Difference, SmoothUnion
from geometry_extension.glsl import glsl_expression, glsl_function


@pytest.mark.parametrize("field", [
    Sphere((0, 0, 0), 1),
    Box((1, 2, 3), (2, 2, 2)),
    Capsule((0, 0, 0), (0, 2, 0), 0.5),
    Capsule((0, 0, 0), (0, 0, 0), 1),
    Translate(Sphere((0, 0, 0), 1), (1, 2, 3)),
    Union(Sphere((0, 0, 0), 1), Box((0, 0, 0), (1, 1, 1))),
    Difference(Box((0, 0, 0), (2, 2, 2)), Sphere((0, 0, 0), 1)),
    SmoothUnion(Sphere((0, 0, 0), 1), Sphere((1, 0, 0), 1), 0.4),
])
def test_shader_emits_expression(field):
    expr = glsl_expression(field)
    assert expr
    assert "float scene_distance(vec3 p)" in glsl_function(field)
    assert "return " in glsl_function(field)


def test_rejects_unsupported_and_bad_identifier():
    with pytest.raises(TypeError):
        glsl_expression(object())
    with pytest.raises(ValueError):
        glsl_function(Sphere((0, 0, 0), 1), "bad;name")
    with pytest.raises(ValueError):
        glsl_function(Sphere((0, 0, 0), 1), "gl_Forbidden")
