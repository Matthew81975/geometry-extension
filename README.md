# Geometry Extension

A lightweight Python geometry toolkit centered on numerical support mappings, directional extrema, bounding geometry, alignment operators, and progressively refined convex approximations.

## Core idea

For geometry that cannot be solved analytically, evaluate or numerically optimize the support function:

    h(n) = max(x dot n)

Rotating the direction n gives directional extrema. Orthogonal extrema produce oriented bounding boxes. Sampling many directions produces supporting half-spaces whose intersection is an outer convex approximation. Increasing angular resolution tightens that approximation.

## Current API

- support_point, support_value, directional_extrema
- oriented_box_2d, minimum_sampled_box_2d
- directions_circle, directions_sphere
- sampled_support_envelope, support_envelope_2d, support_envelope_3d
- rotation_between
- align_vector_to_vector, align_vector_to_point, align_vector_to_plane

The package currently has no runtime dependencies.
