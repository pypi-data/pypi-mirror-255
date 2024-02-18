from typing import Any, Optional, overload, Typing, Sequence
from enum import Enum
import lagrange.io

class FileEncoding(Enum):
    """
    <attribute '__doc__' of 'FileEncoding' objects>
    """

    Ascii: Any
    
    Binary: Any
    
class FileFormat(Enum):
    """
    <attribute '__doc__' of 'FileFormat' objects>
    """

    Gltf: Any
    
    Msh: Any
    
    Obj: Any
    
    Ply: Any
    
    Unknown: Any
    
class LoadOptions:
    """
    None
    """

    def __init__(self) -> None:
        ...
    
    @property
    def load_materials(self) -> bool:
        ...
    @load_materials.setter
    def load_materials(self, arg: bool, /) -> None:
        ...
    
    @property
    def load_normals(self) -> bool:
        ...
    @load_normals.setter
    def load_normals(self, arg: bool, /) -> None:
        ...
    
    @property
    def load_object_id(self) -> bool:
        ...
    @load_object_id.setter
    def load_object_id(self, arg: bool, /) -> None:
        ...
    
    @property
    def load_tangents(self) -> bool:
        ...
    @load_tangents.setter
    def load_tangents(self, arg: bool, /) -> None:
        ...
    
    @property
    def load_uvs(self) -> bool:
        ...
    @load_uvs.setter
    def load_uvs(self, arg: bool, /) -> None:
        ...
    
    @property
    def load_vertex_colors(self) -> bool:
        ...
    @load_vertex_colors.setter
    def load_vertex_colors(self, arg: bool, /) -> None:
        ...
    
    @property
    def load_weights(self) -> bool:
        ...
    @load_weights.setter
    def load_weights(self, arg: bool, /) -> None:
        ...
    
    @property
    def search_path(self) -> os.PathLike:
        ...
    @search_path.setter
    def search_path(self, arg: os.PathLike, /) -> None:
        ...
    
    @property
    def triangulate(self) -> bool:
        ...
    @triangulate.setter
    def triangulate(self, arg: bool, /) -> None:
        ...
    
class SaveOptions:
    """
    None
    """

    class AttributeConversionPolicy(Enum):
        """
        <attribute '__doc__' of 'AttributeConversionPolicy' objects>
        """
    
        ConvertAsNeeded: Any
        
        ExactMatchOnly: Any
        
    class OutputAttributes(Enum):
        """
        <attribute '__doc__' of 'OutputAttributes' objects>
        """
    
        All: Any
        
        SelectedOnly: Any
        
    def __init__(self) -> None:
        ...
    
    @property
    def attribute_conversion_policy(self) -> lagrange.io.SaveOptions.AttributeConversionPolicy:
        ...
    @attribute_conversion_policy.setter
    def attribute_conversion_policy(self, arg: lagrange.io.SaveOptions.AttributeConversionPolicy, /) -> None:
        ...
    
    @property
    def encoding(self) -> lagrange.io.FileEncoding:
        ...
    @encoding.setter
    def encoding(self, arg: lagrange.io.FileEncoding, /) -> None:
        ...
    
    @property
    def output_attributes(self) -> lagrange.io.SaveOptions.OutputAttributes:
        ...
    @output_attributes.setter
    def output_attributes(self, arg: lagrange.io.SaveOptions.OutputAttributes, /) -> None:
        ...
    
    @property
    def selected_attributes(self) -> list[int]:
        ...
    @selected_attributes.setter
    def selected_attributes(self, arg: list[int], /) -> None:
        ...
    
def load_mesh(filename: os.PathLike, triangulate: bool = False) -> lagrange.core.SurfaceMesh:
    """
    Load mesh from a file.
    
    :param filename:    The input file name.
    :param triangulate: Whether to triangulate the mesh if it is not already triangulated. Defaults to False.
    
    :return SurfaceMesh: The mesh object extracted from the input string.
    """
    ...

def load_scene(filename: os.PathLike, options: lagrange.io.LoadOptions = ...) -> lagrange.scene.Scene:
    """
    Load a scene.
    
    :param filename:    The input file name.
    :param options:     Load scene options. Check the class for more details.
    
    :return Scene: The loaded scene object.
    """
    ...

def load_simple_scene(filename: os.PathLike, triangulate: bool = False, search_path: Optional[os.PathLike] = None) -> lagrange.scene.SimpleScene3D:
    """
    Load a simple scene from file.
    
    :param filename:    The input file name.
    :param triangulate: Whether to triangulate the scene if it is not already triangulated. Defaults to False.
    :param search_path: Optional search path for external references (e.g. .mtl, .bin, etc.). Defaults to None.
    
    :return SimpleScene: The scene object extracted from the input string.
    """
    ...

def mesh_to_string(mesh: lagrange.core.SurfaceMesh, format: str = 'ply', binary: bool = True, exact_match: bool = True, selected_attributes: Optional[list[int]] = None) -> bytes:
    """
    Convert a mesh to a binary string based on specified format.
    
    :param mesh: The input mesh.
    :param format: Format to use. Supported formats are "obj", "ply", "gltf" and "msh".
    :param binary: Whether to save the mesh in binary format if supported. Defaults to True. Only `msh`, `ply` and `glb` support binary format.
    :param exact_match: Whether to save attributes in their exact form. Some mesh formats may not support all the attribute types. If set to False, attributes will be converted to the closest supported attribute type. Defaults to True.
    :param selected_attributes: A list of attribute ids to save. If not specified, all attributes will be saved. Defaults to None.
    
    :return str: The string representing the input mesh.
    """
    ...

def save_mesh(filename: os.PathLike, mesh: lagrange.core.SurfaceMesh, binary: bool = True, exact_match: bool = True, selected_attributes: Optional[list[int]] = None) -> None:
    """
    Save mesh to file.
    
    Filename extension determines the file format. Supported formats are: `obj`, `ply`, `msh`, `glb` and `gltf`.
    
    :param filename: The output file name.
    :param mesh: The input mesh.
    :param binary: Whether to save the mesh in binary format if supported. Defaults to True. Only `msh`, `ply` and `glb` support binary format.
    :param exact_match: Whether to save attributes in their exact form. Some mesh formats may not support all the attribute types. If set to False, attributes will be converted to the closest supported attribute type. Defaults to True.
    :param selected_attributes: A list of attribute ids to save. If not specified, all attributes will be saved. Defaults to None.
    """
    ...

def save_scene(filename: os.PathLike, scene: lagrange.scene.Scene, options: lagrange.io.SaveOptions = ...) -> None:
    """
    Save a scene.
    
    :param filename:    The output file name.
    :param scene:       The scene to save.
    :param options:     Save options. Check the class for more details.
    """
    ...

def save_simple_scene(filename: os.PathLike, scene: lagrange.scene.SimpleScene3D, binary: bool = True) -> None:
    """
    Save a simple scene to file.
    
    :param filename: The output file name.
    :param scene:    The input scene.
    :param binary:   Whether to save the scene in binary format if supported. Defaults to True. Only `glb` supports binary format.
    """
    ...

def string_to_mesh(data: bytes, triangulate: bool = False) -> lagrange.core.SurfaceMesh:
    """
    Convert a binary string to a mesh.
    
    The binary string should use one of the supported formats. Supported formats include `obj`, `ply`,
    `gltf`, `glb` and `msh`. Format is automatically detected.
    
    :param data:        A binary string representing the mesh data in a supported format.
    :param triangulate: Whether to triangulate the mesh if it is not already triangulated. Defaults to False.
    
    :return SurfaceMesh: The mesh object extracted from the input string.
    """
    ...

