from typing import Any, Optional, overload, Typing, Sequence
from enum import Enum
import lagrange.scene

class Animation:

    def __init__(self) -> None:
        ...
    
    @property
    def name(self) -> str:
        ...
    @name.setter
    def name(self, arg: str, /) -> None:
        ...
    
class Camera:
    """
    Camera
    """

    class Type(Enum):
        """
        <attribute '__doc__' of 'Type' objects>
        """
    
        Orthographic: Any
        
        Perspective: Any
        
    def __init__(self) -> None:
        ...
    
    @property
    def aspect_ratio(self) -> float:
        ...
    @aspect_ratio.setter
    def aspect_ratio(self, arg: float, /) -> None:
        ...
    
    @property
    def far_plane(self) -> float:
        ...
    @far_plane.setter
    def far_plane(self, arg: float, /) -> None:
        ...
    
    @property
    def get_vertical_fov(self) -> float:
        ...
    
    @property
    def horizontal_fov(self) -> float:
        ...
    @horizontal_fov.setter
    def horizontal_fov(self, arg: float, /) -> None:
        ...
    
    @property
    def look_at(self) -> numpy.typing.NDArray:
        ...
    @look_at.setter
    def look_at(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    @property
    def name(self) -> str:
        ...
    @name.setter
    def name(self, arg: str, /) -> None:
        ...
    
    @property
    def near_plane(self) -> float:
        ...
    @near_plane.setter
    def near_plane(self, arg: float, /) -> None:
        ...
    
    @property
    def orthographic_width(self) -> float:
        ...
    @orthographic_width.setter
    def orthographic_width(self, arg: float, /) -> None:
        ...
    
    @property
    def position(self) -> numpy.typing.NDArray:
        ...
    @position.setter
    def position(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    @property
    def set_horizontal_fov_from_vertical_fov(self, arg: float, /) -> None:
        ...
    
    @property
    def type(self) -> lagrange.scene.Camera.Type:
        ...
    @type.setter
    def type(self, arg: lagrange.scene.Camera.Type, /) -> None:
        ...
    
    @property
    def up(self) -> numpy.typing.NDArray:
        ...
    @up.setter
    def up(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
class FacetAllocationStrategy(Enum):
    """
    <attribute '__doc__' of 'FacetAllocationStrategy' objects>
    """

    EvenSplit: Any
    
    RelativeToMeshArea: Any
    
    RelativeToNumFacets: Any
    
    Synchronized: Any
    
class ImageLegacy:
    """
    None
    """

    class Type(Enum):
        """
        <attribute '__doc__' of 'Type' objects>
        """
    
        Bmp: Any
        
        Gif: Any
        
        Jpeg: Any
        
        Png: Any
        
        Unknown: Any
        
    def __init__(self) -> None:
        ...
    
    @property
    def channel(self) -> lagrange.image.ImageChannel:
        ...
    @channel.setter
    def channel(self, arg: lagrange.image.ImageChannel, /) -> None:
        ...
    
    @property
    def data(self) -> lagrange.image.ImageStorage:
        ...
    @data.setter
    def data(self, arg: lagrange.image.ImageStorage, /) -> None:
        ...
    
    @property
    def element_size(self) -> int:
        ...
    
    @property
    def height(self) -> int:
        ...
    @height.setter
    def height(self, arg: int, /) -> None:
        ...
    
    @property
    def name(self) -> str:
        ...
    @name.setter
    def name(self, arg: str, /) -> None:
        ...
    
    @property
    def num_channels(self) -> int:
        ...
    
    @property
    def precision(self) -> lagrange.image.ImagePrecision:
        ...
    @precision.setter
    def precision(self, arg: lagrange.image.ImagePrecision, /) -> None:
        ...
    
    @property
    def type(self) -> lagrange.scene.ImageLegacy.Type:
        ...
    @type.setter
    def type(self, arg: lagrange.scene.ImageLegacy.Type, /) -> None:
        ...
    
    @property
    def uri(self) -> str:
        ...
    @uri.setter
    def uri(self, arg: str, /) -> None:
        ...
    
    @property
    def width(self) -> int:
        ...
    @width.setter
    def width(self, arg: int, /) -> None:
        ...
    
class Light:
    """
    Light
    """

    class Type(Enum):
        """
        <attribute '__doc__' of 'Type' objects>
        """
    
        Ambient: Any
        
        Area: Any
        
        Directional: Any
        
        Point: Any
        
        Spot: Any
        
        Undefined: Any
        
    def __init__(self) -> None:
        ...
    
    @property
    def angle_inner_cone(self) -> float:
        ...
    @angle_inner_cone.setter
    def angle_inner_cone(self, arg: float, /) -> None:
        ...
    
    @property
    def angle_outer_cone(self) -> float:
        ...
    @angle_outer_cone.setter
    def angle_outer_cone(self, arg: float, /) -> None:
        ...
    
    @property
    def attenuation_constant(self) -> float:
        ...
    @attenuation_constant.setter
    def attenuation_constant(self, arg: float, /) -> None:
        ...
    
    @property
    def attenuation_cubic(self) -> float:
        ...
    @attenuation_cubic.setter
    def attenuation_cubic(self, arg: float, /) -> None:
        ...
    
    @property
    def attenuation_linear(self) -> float:
        ...
    @attenuation_linear.setter
    def attenuation_linear(self, arg: float, /) -> None:
        ...
    
    @property
    def attenuation_quadratic(self) -> float:
        ...
    @attenuation_quadratic.setter
    def attenuation_quadratic(self, arg: float, /) -> None:
        ...
    
    @property
    def color_ambient(self) -> numpy.typing.NDArray:
        ...
    @color_ambient.setter
    def color_ambient(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    @property
    def color_diffuse(self) -> numpy.typing.NDArray:
        ...
    @color_diffuse.setter
    def color_diffuse(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    @property
    def color_specular(self) -> numpy.typing.NDArray:
        ...
    @color_specular.setter
    def color_specular(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    @property
    def direction(self) -> numpy.typing.NDArray:
        ...
    @direction.setter
    def direction(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    @property
    def intensity(self) -> float:
        ...
    @intensity.setter
    def intensity(self, arg: float, /) -> None:
        ...
    
    @property
    def name(self) -> str:
        ...
    @name.setter
    def name(self, arg: str, /) -> None:
        ...
    
    @property
    def position(self) -> numpy.typing.NDArray:
        ...
    @position.setter
    def position(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    @property
    def range(self) -> float:
        ...
    @range.setter
    def range(self, arg: float, /) -> None:
        ...
    
    @property
    def size(self) -> numpy.typing.NDArray:
        ...
    @size.setter
    def size(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    @property
    def type(self) -> lagrange.scene.Light.Type:
        ...
    @type.setter
    def type(self, arg: lagrange.scene.Light.Type, /) -> None:
        ...
    
    @property
    def up(self) -> numpy.typing.NDArray:
        ...
    @up.setter
    def up(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
class Material:
    """
    None
    """

    class AlphaMode(Enum):
        """
        <attribute '__doc__' of 'AlphaMode' objects>
        """
    
        Blend: Any
        
        Mask: Any
        
        Opaque: Any
        
    def __init__(self) -> None:
        ...
    
    @property
    def alpha_cutoff(self) -> float:
        ...
    @alpha_cutoff.setter
    def alpha_cutoff(self, arg: float, /) -> None:
        ...
    
    @property
    def alpha_mode(self) -> lagrange.scene.Material.AlphaMode:
        ...
    @alpha_mode.setter
    def alpha_mode(self, arg: lagrange.scene.Material.AlphaMode, /) -> None:
        ...
    
    @property
    def base_color_texture(self) -> lagrange.scene.TextureInfo:
        ...
    @base_color_texture.setter
    def base_color_texture(self, arg: lagrange.scene.TextureInfo, /) -> None:
        ...
    
    @property
    def base_color_value(self) -> numpy.typing.NDArray:
        ...
    @base_color_value.setter
    def base_color_value(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    @property
    def double_sided(self) -> bool:
        ...
    @double_sided.setter
    def double_sided(self, arg: bool, /) -> None:
        ...
    
    @property
    def emissive_texture(self) -> lagrange.scene.TextureInfo:
        ...
    @emissive_texture.setter
    def emissive_texture(self, arg: lagrange.scene.TextureInfo, /) -> None:
        ...
    
    @property
    def emissive_value(self) -> numpy.typing.NDArray:
        ...
    @emissive_value.setter
    def emissive_value(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    @property
    def metallic_roughness_texture(self) -> lagrange.scene.TextureInfo:
        ...
    @metallic_roughness_texture.setter
    def metallic_roughness_texture(self, arg: lagrange.scene.TextureInfo, /) -> None:
        ...
    
    @property
    def metallic_value(self) -> float:
        ...
    @metallic_value.setter
    def metallic_value(self, arg: float, /) -> None:
        ...
    
    @property
    def name(self) -> str:
        ...
    @name.setter
    def name(self, arg: str, /) -> None:
        ...
    
    @property
    def normal_scale(self) -> float:
        ...
    @normal_scale.setter
    def normal_scale(self, arg: float, /) -> None:
        ...
    
    @property
    def normal_texture(self) -> lagrange.scene.TextureInfo:
        ...
    @normal_texture.setter
    def normal_texture(self, arg: lagrange.scene.TextureInfo, /) -> None:
        ...
    
    @property
    def occlusion_strength(self) -> float:
        ...
    @occlusion_strength.setter
    def occlusion_strength(self, arg: float, /) -> None:
        ...
    
    @property
    def occlusion_texture(self) -> lagrange.scene.TextureInfo:
        ...
    @occlusion_texture.setter
    def occlusion_texture(self, arg: lagrange.scene.TextureInfo, /) -> None:
        ...
    
    @property
    def roughness_value(self) -> float:
        ...
    @roughness_value.setter
    def roughness_value(self, arg: float, /) -> None:
        ...
    
class MeshInstance3D:
    """
    A single mesh instance in a scene
    """

    def __init__(self) -> None:
        ...
    
    @property
    def mesh_index(self) -> int:
        ...
    @mesh_index.setter
    def mesh_index(self, arg: int, /) -> None:
        ...
    
    @property
    def transform(self) -> numpy.typing.NDArray:
        ...
    @transform.setter
    def transform(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
class Node:
    """
    None
    """

    def __init__(self) -> None:
        ...
    
    @property
    def cameras(self) -> list[int]:
        ...
    @cameras.setter
    def cameras(self, arg: list[int], /) -> None:
        ...
    
    @property
    def children(self) -> list[int]:
        ...
    @children.setter
    def children(self, arg: list[int], /) -> None:
        ...
    
    @property
    def lights(self) -> list[int]:
        ...
    @lights.setter
    def lights(self, arg: list[int], /) -> None:
        ...
    
    @property
    def meshes(self) -> list[lagrange.scene.SceneMeshInstance]:
        ...
    @meshes.setter
    def meshes(self, arg: list[lagrange.scene.SceneMeshInstance], /) -> None:
        ...
    
    @property
    def name(self) -> str:
        ...
    @name.setter
    def name(self, arg: str, /) -> None:
        ...
    
    @property
    def parent(self) -> int:
        ...
    @parent.setter
    def parent(self, arg: int, /) -> None:
        ...
    
    @property
    def transform(self) -> list[list[float]]:
        ...
    @transform.setter
    def transform(self, arg: list[list[float]], /) -> None:
        ...
    
class RemeshingOptions:
    """
    None
    """

    def __init__(self) -> None:
        ...
    
    @property
    def facet_allocation_strategy(self) -> lagrange.scene.FacetAllocationStrategy:
        ...
    @facet_allocation_strategy.setter
    def facet_allocation_strategy(self, arg: lagrange.scene.FacetAllocationStrategy, /) -> None:
        ...
    
    @property
    def min_facets(self) -> int:
        ...
    @min_facets.setter
    def min_facets(self, arg: int, /) -> None:
        ...
    
class Scene:
    """
    A 3D scene
    """

    def __init__(self) -> None:
        ...
    
    @property
    def animations(self) -> list[lagrange.scene.Animation]:
        ...
    @animations.setter
    def animations(self, arg: list[lagrange.scene.Animation], /) -> None:
        ...
    
    @property
    def cameras(self) -> list[lagrange.scene.Camera]:
        ...
    @cameras.setter
    def cameras(self, arg: list[lagrange.scene.Camera], /) -> None:
        ...
    
    @property
    def images(self) -> list[lagrange.scene.ImageLegacy]:
        ...
    @images.setter
    def images(self, arg: list[lagrange.scene.ImageLegacy], /) -> None:
        ...
    
    @property
    def lights(self) -> list[lagrange.scene.Light]:
        ...
    @lights.setter
    def lights(self, arg: list[lagrange.scene.Light], /) -> None:
        ...
    
    @property
    def materials(self) -> list[lagrange.scene.Material]:
        ...
    @materials.setter
    def materials(self, arg: list[lagrange.scene.Material], /) -> None:
        ...
    
    @property
    def meshes(self) -> list[lagrange.core.SurfaceMesh]:
        ...
    @meshes.setter
    def meshes(self, arg: list[lagrange.core.SurfaceMesh], /) -> None:
        ...
    
    @property
    def name(self) -> str:
        ...
    @name.setter
    def name(self, arg: str, /) -> None:
        ...
    
    @property
    def nodes(self) -> list[lagrange.scene.Node]:
        ...
    @nodes.setter
    def nodes(self, arg: list[lagrange.scene.Node], /) -> None:
        ...
    
    @property
    def skeletons(self) -> list[lagrange.scene.Skeleton]:
        ...
    @skeletons.setter
    def skeletons(self, arg: list[lagrange.scene.Skeleton], /) -> None:
        ...
    
    @property
    def textures(self) -> list[lagrange.scene.Texture]:
        ...
    @textures.setter
    def textures(self, arg: list[lagrange.scene.Texture], /) -> None:
        ...
    
class SceneMeshInstance:
    """
    Mesh and material index of a node
    """

    def __init__(self) -> None:
        ...
    
    @property
    def materials(self) -> list[int]:
        ...
    @materials.setter
    def materials(self, arg: list[int], /) -> None:
        ...
    
    @property
    def mesh(self) -> int:
        ...
    @mesh.setter
    def mesh(self, arg: int, /) -> None:
        ...
    
class SimpleScene3D:
    """
    Simple scene container for instanced meshes
    """

    def __init__(self) -> None:
        ...
    
    def add_instance(self, instance: lagrange.scene.MeshInstance3D) -> int:
        ...
    
    def add_mesh(self, mesh: lagrange.core.SurfaceMesh) -> int:
        ...
    
    def get_instance(self, mesh_index: int, instance_index: int) -> lagrange.scene.MeshInstance3D:
        ...
    
    def get_mesh(self, mesh_index: int) -> lagrange.core.SurfaceMesh:
        ...
    
    def num_instances(self, mesh_index: int) -> int:
        ...
    
    @property
    def num_meshes(self) -> int:
        """
        Number of meshes in the scene
        """
        ...
    
    def ref_mesh(self, mesh_index: int) -> lagrange.core.SurfaceMesh:
        ...
    
    def reserve_instances(self, mesh_index: int, num_instances: int) -> None:
        ...
    
    def reserve_meshes(self, num_meshes: int) -> None:
        ...
    
    @property
    def total_num_instances(self) -> int:
        """
        Total number of instances for all meshes in the scene
        """
        ...
    
class Skeleton:

    def __init__(self) -> None:
        ...
    
    @property
    def meshes(self) -> list[int]:
        ...
    @meshes.setter
    def meshes(self, arg: list[int], /) -> None:
        ...
    
class Texture:
    """
    Texture
    """

    class TextureFilter(Enum):
        """
        <attribute '__doc__' of 'TextureFilter' objects>
        """
    
        Linear: Any
        
        LinearMipmapLinear: Any
        
        LinearMipmapNearest: Any
        
        Nearest: Any
        
        NearestMimpapNearest: Any
        
        NearestMipmapLinear: Any
        
        Undefined: Any
        
    class WrapMode(Enum):
        """
        <attribute '__doc__' of 'WrapMode' objects>
        """
    
        Clamp: Any
        
        Decal: Any
        
        Mirror: Any
        
        Wrap: Any
        
    def __init__(self) -> None:
        ...
    
    @property
    def image(self) -> int:
        ...
    @image.setter
    def image(self, arg: int, /) -> None:
        ...
    
    @property
    def mag_filter(self) -> lagrange.scene.Texture.TextureFilter:
        ...
    @mag_filter.setter
    def mag_filter(self, arg: lagrange.scene.Texture.TextureFilter, /) -> None:
        ...
    
    @property
    def min_filter(self) -> lagrange.scene.Texture.TextureFilter:
        ...
    @min_filter.setter
    def min_filter(self, arg: lagrange.scene.Texture.TextureFilter, /) -> None:
        ...
    
    @property
    def name(self) -> str:
        ...
    @name.setter
    def name(self, arg: str, /) -> None:
        ...
    
    @property
    def offset(self) -> numpy.typing.NDArray:
        ...
    @offset.setter
    def offset(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    @property
    def rotation(self) -> float:
        ...
    @rotation.setter
    def rotation(self, arg: float, /) -> None:
        ...
    
    @property
    def scale(self) -> numpy.typing.NDArray:
        ...
    @scale.setter
    def scale(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    @property
    def wrap_u(self) -> lagrange.scene.Texture.WrapMode:
        ...
    @wrap_u.setter
    def wrap_u(self, arg: lagrange.scene.Texture.WrapMode, /) -> None:
        ...
    
    @property
    def wrap_v(self) -> lagrange.scene.Texture.WrapMode:
        ...
    @wrap_v.setter
    def wrap_v(self, arg: lagrange.scene.Texture.WrapMode, /) -> None:
        ...
    
class TextureInfo:
    """
    None
    """

    def __init__(self) -> None:
        ...
    
    @property
    def index(self) -> int:
        ...
    @index.setter
    def index(self, arg: int, /) -> None:
        ...
    
    @property
    def texcoord(self) -> int:
        ...
    @texcoord.setter
    def texcoord(self, arg: int, /) -> None:
        ...
    
def add_child(arg0: lagrange.scene.Scene, arg1: lagrange.scene.Node, arg2: lagrange.scene.Node, /) -> int:
    ...

def add_mesh(arg0: lagrange.scene.Scene, arg1: lagrange.core.SurfaceMesh, /) -> int:
    ...

def compute_global_node_transform(arg0: lagrange.scene.Scene, arg1: int, /) -> list[list[float]]:
    ...

def mesh_to_simple_scene(mesh: lagrange.core.SurfaceMesh) -> lagrange.scene.SimpleScene3D:
    """
    Converts a single mesh into a simple scene with a single identity instance of the input mesh.
    
    :param mesh: Input mesh to convert.
    
    :return: Simple scene containing the input mesh.
    """
    ...

def meshes_to_simple_scene(meshes: list[lagrange.core.SurfaceMesh]) -> lagrange.scene.SimpleScene3D:
    """
    Converts a list of meshes into a simple scene with a single identity instance of each input mesh.
    
    :param meshes: Input meshes to convert.
    
    :return: Simple scene containing the input meshes.
    """
    ...

def simple_scene_to_mesh(scene: lagrange.scene.SimpleScene3D, normalize_normals: bool = True, normalize_tangents_bitangents: bool = True, preserve_attributes: bool = True) -> lagrange.core.SurfaceMesh:
    """
    Converts a scene into a concatenated mesh with all the transforms applied.
    
    :param scene: Scene to convert.
    :param normalize_normals: If enabled, normals are normalized after transformation.
    :param normalize_tangents_bitangents: If enabled, tangents and bitangents are normalized after transformation.
    :param preserve_attributes: Preserve shared attributes and map them to the output mesh.
    
    :return: Concatenated mesh.
    """
    ...

