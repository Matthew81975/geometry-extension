"""Reusable numerical geometry extensions."""

from .alignment import align_vector_to_plane, align_vector_to_point, align_vector_to_vector, rotation_between
from .bounds import OrientedBox2D, minimum_sampled_box_2d, oriented_box_2d
from .directions import directions_circle, directions_sphere
from .envelope import SupportPlane, sampled_support_envelope, support_envelope_2d, support_envelope_3d
from .support import directional_extrema, support_point, support_value

__all__ = [
    "OrientedBox2D", "SupportPlane",
    "align_vector_to_plane", "align_vector_to_point", "align_vector_to_vector",
    "directional_extrema", "directions_circle", "directions_sphere",
    "minimum_sampled_box_2d", "oriented_box_2d", "rotation_between",
    "sampled_support_envelope", "support_envelope_2d", "support_envelope_3d",
    "support_point", "support_value",
]
