"""Reusable numerical geometry extensions."""

from .alignment import (
    align_vector_to_plane,
    align_vector_to_point,
    align_vector_to_vector,
    rotation_between,
)
from .support import (
    directional_extrema,
    support_point,
    support_value,
)

__all__ = [
    "align_vector_to_plane",
    "align_vector_to_point",
    "align_vector_to_vector",
    "directional_extrema",
    "rotation_between",
    "support_point",
    "support_value",
]
