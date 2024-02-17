"""
This module contains Edge and Arrow subclasses for this behavioral package.
"""

from .....logger import logger
from ...config import SwitchSetting
from ...colors import Color
from ...graph import Arrow, DataEdge, Edge, Vertex
from ..data.entities import Data
from ..execution.entities import Call, Process
from .entities import Connection, Host, Socket

__all__ = ["SpawnedProcess", "HasSocket", "HasConnection", "Communicates", "CreatesSocket", "Binds", "Connects", "Sends", "Receives", "Conveys", "Closes", "CloseSocket", "ListensOn", "Shutdown", "Accepts", "Duplicates"]





logger.info("Loading relations from {} library.".format(__name__.rpartition(".")[0].rpartition(".")[2]))

class SpawnedProcess(Edge):
    
    """
    This kind of edge indicates that a machine hosts a process.
    """

    source : Host
    destination : Process





class HasSocket(Edge):

    """
    This kind of edge indicates that a process opened a socket.
    """

    label : str = ""

    source : Process
    destination : Socket





class HasConnection(Edge):

    """
    This kind of edge indicates that a socket makes a connection.
    """

    label : str = ""

    source : Socket
    destination : Connection





class Communicates(Edge):

    """
    This kind of edge indicates that two hosts communicate via a connection
    """

    source : Connection
    destination : Host





class CreatesSocket(Edge):

    """
    This kind of edge indicates that a system call created a socket.
    """

    label : str = ""

    source : Call
    destination : Socket





class Binds(DataEdge):

    """
    This kind of edge indicates that a system call bound a connection to a local address.
    """

    __slots__ = {
        "__src" : "The source (local) address of the connection",
    }

    __defining_data__ = DataEdge.__defining_data__ | {
        "src"
    }

    label : str = ""

    source : Call
    destination : Connection

    def __init__(self, source: Vertex, destination: Vertex, *, auto_write: bool = True, src : tuple[str, int]) -> None:
        super().__init__(source, destination, auto_write = auto_write, src = src)

    @property
    def src(self) -> tuple[str, int]:
        """
        The local address of the connection.
        """
        return self.__src
    
    @src.setter
    def src(self, s : tuple[str, int]):
        if not isinstance(s, tuple):
            raise TypeError(f"Expected tuple, got '{type(s).__name__}'")
        if len(s) != 2:
            raise ValueError(f"Expected a length 2 tuple, got {len(s)}")
        if not isinstance(s[0], str) or not isinstance(s[1], int):
            raise TypeError(f"Expected tuple of str and int, got '{type(s[0]).__name__}' and '{type(s[1]).__name__}'")
        self.__src = s





class Connects(DataEdge):

    """
    This kind of edge indicates that a system call connected a connection to a remote address.
    """

    __slots__ = {
        "__dst" : "The destination (remote) address of the connection"
    }

    __defining_data__ = DataEdge.__defining_data__ | {
        "dst"
    }

    label : str = ""

    source : Call
    destination : Connection

    def __init__(self, source: Vertex, destination: Vertex, *, auto_write: bool = True, dst : tuple[str, int]) -> None:
        super().__init__(source, destination, auto_write = auto_write, dst = dst)

    @property
    def dst(self) -> tuple[str, int]:
        """
        The remote address of the connection.
        """
        return self.__dst
    
    @dst.setter
    def dst(self, d : tuple[str, int]):
        if not isinstance(d, tuple):
            raise TypeError(f"Expected tuple, got '{type(d).__name__}'")
        if len(d) != 2:
            raise ValueError(f"Expected a length 2 tuple, got {len(d)}")
        if not isinstance(d[0], str) or not isinstance(d[1], int):
            raise TypeError(f"Expected tuple of str and int, got '{type(d[0]).__name__}' and '{type(d[1]).__name__}'")
        self.__dst = d





class Sends(Arrow):

    """
    This kind of arrow indicates that a system call sent data through a connection.
    """

    source : Call
    destination : Data





class Receives(Arrow):

    """
    This kind of arrow indicates that a system call received data through a connection.
    """

    source : Data
    destination : Call





class Conveys(Arrow):
    
    """
    This kind of arrow indicates that a connection conveyed a message.
    """

    label : str = ""

    source : Connection | Data
    destination : Connection | Data





class Closes(Edge):

    """
    This kind of edge indicates that a system call closed a connection.
    """
    
    label : str = ""

    source : Call
    destination : Connection





class CloseSocket(Edge):

    """
    This kind of edge indicates that a system call closed a socket object.
    """

    label : str = ""

    source : Call
    destination : Socket





class ListensOn(Edge):

    """
    This kind of edge indicates that a system call set a socket to listening mode.
    """

    source : Call
    destination : Socket





class Shutdown(Edge):

    """
    This kind of edge indicates that a connection was shutdown by a system call.
    """

    label : str = ""

    source : Call
    destination : Connection





class Accepts(DataEdge):

    """
    This kind of arrow indicates that a system call accepted a connection from a remote address.
    """

    __slots__ = {
        "__dst" : "The destination (remote) address of the connection"
    }

    __defining_data__ = DataEdge.__defining_data__ | {
        "dst"
    }

    label : str = ""

    source : Call
    destination : Connection

    def __init__(self, source: Vertex, destination: Vertex, *, auto_write: bool = True, dst : tuple[str, int]) -> None:
        super().__init__(source, destination, auto_write = auto_write, dst = dst)

    @property
    def dst(self) -> tuple[str, int]:
        """
        The remote address of the connection.
        """
        return self.__dst
    
    @dst.setter
    def dst(self, d : tuple[str, int]):
        if not isinstance(d, tuple):
            raise TypeError(f"Expected tuple, got '{type(d).__name__}'")
        if len(d) != 2:
            raise ValueError(f"Expected a length 2 tuple, got {len(d)}")
        if not isinstance(d[0], str) or not isinstance(d[1], int):
            raise TypeError(f"Expected tuple of str and int, got '{type(d[0]).__name__}' and '{type(d[1]).__name__}'")
        self.__dst = d





class Duplicates(Arrow):

    """
    This kind of arrow indicates that a socket was duplicated to form a similar socket (example: after a call to accept()).
    """

    source : Socket
    destination : Socket





del Arrow, DataEdge, Call, Color, SwitchSetting, Connection, Data, Edge, Host, Process, Socket, Vertex, logger