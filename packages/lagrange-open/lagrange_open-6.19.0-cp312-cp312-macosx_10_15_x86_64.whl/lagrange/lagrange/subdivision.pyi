from typing import Any, Optional, overload, Typing, Sequence
from enum import Enum
import lagrange.subdivision

class FaceVaryingInterpolation(Enum):
    """
    <attribute '__doc__' of 'lagrange.subdivision.FaceVaryingInterpolation' objects>
    """

    All: Any
    
    Boundaries: Any
    
    CornersOnly: Any
    
    CornersPlus1: Any
    
    CornersPlus2: Any
    
    Smooth: Any
    
class InterpolatedAttributesSelection(Enum):
    """
    <attribute '__doc__' of 'lagrange.subdivision.InterpolatedAttributesSelection' objects>
    """

    All: Any
    
    Empty: Any
    
    Selected: Any
    
class SchemeType(Enum):
    """
    <attribute '__doc__' of 'lagrange.subdivision.SchemeType' objects>
    """

    Bilinear: Any
    
    CatmullClark: Any
    
    Loop: Any
    
class VertexBoundaryInterpolation(Enum):
    """
    <attribute '__doc__' of 'lagrange.subdivision.VertexBoundaryInterpolation' objects>
    """

    EdgeAndCorner: Any
    
    EdgeOnly: Any
    
    NoInterpolation: Any
    
def subdivide_mesh(mesh: lagrange.core.SurfaceMesh, num_levels: int, scheme: Optional[lagrange.subdivision.SchemeType] = None, vertex_boundary_interpolation: lagrange.subdivision.VertexBoundaryInterpolation = lagrange.subdivision.VertexBoundaryInterpolation.EdgeOnly, face_varying_interpolation: lagrange.subdivision.FaceVaryingInterpolation = lagrange.subdivision.FaceVaryingInterpolation.Smooth, use_limit_surface: bool = False, interpolated_attributes_selection: lagrange.subdivision.InterpolatedAttributesSelection = lagrange.subdivision.InterpolatedAttributesSelection.All, interpolated_smooth_attributes: Optional[list[int]] = None, interpolated_linear_attributes: Optional[list[int]] = None, edge_sharpness_attr: Optional[int] = None, vertex_sharpness_attr: Optional[int] = None, face_hole_attr: Optional[int] = None, output_limit_normals: Optional[str] = None, output_limit_tangents: Optional[str] = None, output_limit_bitangents: Optional[str] = None) -> lagrange.core.SurfaceMesh:
    """
    Evaluates the subdivision surface of a polygonal mesh.
    
    :param mesh:                  The source mesh.
    :param num_levels:            The number of levels of subdivision to apply.
    :param scheme:                The subdivision scheme to use.
    :param vertex_boundary_interpolation:  Vertex boundary interpolation rule.
    :param face_varying_interpolation:     Face-varying interpolation rule.
    :param use_limit_surface:      Interpolate all data to the limit surface.
    :param edge_sharpness_attr:    Per-edge scalar attribute denoting edge sharpness. Sharpness values must be in [0, 1] (0 means smooth, 1 means sharp).
    :param vertex_sharpness_attr:  Per-vertex scalar attribute denoting vertex sharpness (e.g. for boundary corners). Sharpness values must be in [0, 1] (0 means smooth, 1 means sharp).
    :param face_hole_attr:         Per-face integer attribute denoting face holes. A non-zero value means the facet is a hole. If a face is tagged as a hole, the limit surface will not be generated for that face.
    :param output_limit_normals:   Output name for a newly computed per-vertex attribute containing the normals to the limit surface. Skipped if left empty.
    :param output_limit_tangents:  Output name for a newly computed per-vertex attribute containing the tangents (first derivatives) to the limit surface. Skipped if left empty.
    :param output_limit_bitangents: Output name for a newly computed per-vertex attribute containing the bitangents (second derivative) to the limit surface. Skipped if left empty.
    
    :return: The subdivided mesh.
    """
    ...

