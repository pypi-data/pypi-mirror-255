from typing import Any, Optional, overload, Typing, Sequence
from enum import Enum
import lagrange.image

class ImageChannel(Enum):
    """
    <attribute '__doc__' of 'lagrange.image.ImageChannel' objects>
    """

    four: Any
    
    one: Any
    
    three: Any
    
    unknown: Any
    
class ImagePrecision(Enum):
    """
    <attribute '__doc__' of 'lagrange.image.ImagePrecision' objects>
    """

    float16: Any
    
    float32: Any
    
    float64: Any
    
    int32: Any
    
    int8: Any
    
    uint32: Any
    
    uint8: Any
    
    unknown: Any
    
class ImageStorage:
    """
    None
    """

    def __init__(self, arg0: int, arg1: int, arg2: int, /) -> None:
        ...
    
    @property
    def data(self) -> numpy.typing.NDArray:
        ...
    
    @property
    def height(self) -> int:
        ...
    
    @property
    def stride(self) -> int:
        ...
    
    @property
    def width(self) -> int:
        ...
    
