"""
This module contains Edge and Arrow subclasses for this behavioral package.
"""

from typing import Literal
from .....logger import logger
from ...config import WeightSetting
from ...colors import Color
from ...graph import Arrow, DataEdge, Edge, Vertex
from ..filesystem.entities import File, Handle
from ..network.entities import Connection, Socket
from .entities import Data, Diff

__all__ = ["IsSimilarTo", "IsAlmostIn", "IsDiffOf", "IsReadBy", "WritesInto", "HasSimilarContent"]





logger.info("Loading relations from {} library.".format(__name__.rpartition(".")[0].rpartition(".")[2]))

class IsSimilarTo(Arrow):

    """
    This kind of arrow indicates two Data nodes have a similar content. The direction of the arrow indicates the order of apparition.
    """

    label : str = ""

    source : Data
    destination : Data





class IsAlmostIn(Arrow):

    """
    This kind of arrow indicates that a Data node's content might be contained in another's one. The direction of the arrow indicates the order of apparition.
    """

    label : str = ""

    source : Data
    destination : Data





class IsDiffOf(Edge):

    """
    This kind of edge indicates that a Diff node sums up operations performed on the destination node.
    """

    label : str = ""

    source : File | Connection | Handle | Socket
    destination : Diff





class IsReadBy(Arrow, IsDiffOf):

    """
    This kind of arrow indicates that a Diff node only read from a vector.
    """

    source : Diff
    destination : File | Connection | Handle | Socket





class WritesInto(Arrow, IsDiffOf):

    """
    This kind of arrow indicates that a Diff node only wrote to a vector.
    """

    source : File | Connection | Handle | Socket
    destination : Diff





class HasSimilarContent(DataEdge):

    """
    This kind of arrow indicates that two Diff nodes have buffers with a certain similarity rate.
    """

    __slots__ = {
        "__source_buffer" : "The name of the buffer of the source node that the similarity was computed with.",
        "__destination_buffer" : "The name of the buffer of the destination node that the similarity was computed with."
    }

    __defining_data__ = DataEdge.__defining_data__ | {
        "source_buffer",
        "destination_buffer"
    }

    label : str = ""

    source : Diff
    destination : Diff

    min_weight = WeightSetting(0.5)
    max_weight = WeightSetting(1.0)

    def __init__(self, source: Vertex, destination: Vertex, *, auto_write: bool = True, source_buffer : Literal["read_buffer", "write_buffer", "global_buffer"], destination_buffer : Literal["read_buffer", "write_buffer", "global_buffer"]) -> None:
        super().__init__(source, destination, auto_write=auto_write, source_buffer = source_buffer, destination_buffer = destination_buffer)
        
    @property
    def source_buffer(self) -> Literal["read_buffer", "write_buffer", "global_buffer"]:
        """
        Returns the name of the content selected for comparison in the source node.
        """
        return self.__source_buffer # type: ignore I don't where you decided it was just str...
    
    @source_buffer.setter
    def source_buffer(self, name : Literal["read_buffer", "write_buffer", "global_buffer"]):
        if name not in ("read_buffer", "write_buffer", "global_buffer"):
            raise ValueError("Diff node buffers can only be set to one of ('read_buffer', 'write_buffer', 'global_buffer')")
        self.__source_buffer = name
    
    @property
    def destination_buffer(self) -> Literal["read_buffer", "write_buffer", "global_buffer"]:
        """
        Returns the name of the content selected for comparison in the destination node.
        """
        return self.__destination_buffer # type: ignore
    
    @destination_buffer.setter
    def destination_buffer(self, name : Literal["read_buffer", "write_buffer", "global_buffer"]):
        if name not in ("read_buffer", "write_buffer", "global_buffer"):
            raise ValueError("Diff node buffers can only be set to one of ('read_buffer', 'write_buffer', 'global_buffer')")
        self.__destination_buffer = name





del Arrow, DataEdge, Color, WeightSetting, Connection, Data, Diff, Edge, File, Handle, Socket, Vertex, logger