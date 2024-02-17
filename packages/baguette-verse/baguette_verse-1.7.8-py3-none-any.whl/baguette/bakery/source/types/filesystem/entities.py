"""
This module contains Vertex subclasses for this behavioral package.
"""

import pathlib

from .....logger import logger
from ...config import ColorSetting, SizeSetting
from ...colors import Color
from ...graph import DataVertex

__all__ = ["File", "Directory", "Handle"]





logger.info("Loading entities from {} library.".format(__name__.rpartition(".")[0].rpartition(".")[2]))

class File(DataVertex):

    """
    A file vertex. Represents a (real) file opened during execution.
    """

    __slots__ = {
        "__path" : "The path to the file in the file system",
    }

    __defining_data__ = DataVertex.__defining_data__ | {
        "path"
    }

    default_color = ColorSetting(Color(0, 255, 50))
    default_size = SizeSetting(2.5)

    deleted_file_color = ColorSetting(Color(100, 100, 100))

    def __init__(self, *, path : pathlib.PurePath) -> None:
        super().__init__(path = path)

    @property
    def path(self) -> pathlib.PurePath:
        """
        The absolute path to the file.
        """
        return self.__path

    @path.setter
    def path(self, value : str):
        from ...utils import path_factory
        self.__path = path_factory(value)
    
    @property
    def name(self) -> str:
        """
        The name of the file (tail of the path).
        """
        if self.__path is None:
            raise RuntimeError("Got a File without path.")
        return self.__path.name
    
    @property
    def extension(self) -> str:
        """
        The file extention (lowercased without '.').
        """
        if self.__path is None:
            raise RuntimeError("Got a File without path.")
        return self.__path.suffix.lower().replace(".", "")
    
    @property
    def label(self) -> str:
        """
        Returns a label for this File node.
        """
        return 'File "' + self.name + '"'
    




class Directory(DataVertex):

    """
    A directory vertex. Represents a (real) directory opened during execution.
    """

    __slots__ = {
        "__path" : "The path to the directory in the file system",
    }

    __defining_data__ = DataVertex.__defining_data__ | {
        "path"
    }
    
    default_color = ColorSetting(Color(0, 100, 0))
    default_size = SizeSetting(2.5)

    deleted_directory_color = ColorSetting(Color(100, 100, 100))

    def __init__(self, *, path : pathlib.PurePath) -> None:
        super().__init__(path = path)

    @property
    def path(self) -> pathlib.PurePath:
        """
        The absolute path to the directory.
        """
        return self.__path

    @path.setter
    def path(self, value : str):
        from ...utils import path_factory
        self.__path = path_factory(value)
    
    @property
    def name(self) -> str:
        """
        The name of the directory (tail of the path).
        """
        if self.__path is None:
            raise RuntimeError("Got a File without path.")
        return self.__path.name if self.__path.name else self.__path.drive
    
    @property
    def label(self) -> str:
        """
        Returns a label for this Directory node.
        """
        if self.__path is None:
            raise RuntimeError("Got a File without path.")
        if not self.__path.name:
            return 'Drive "' + self.name.replace(":", "") + '"'
        return 'Directory "' + self.name + '"'
    




class Handle(DataVertex):

    """
    A handle vertex. Represents a file handle, used when a program opens a file.
    """

    default_color = ColorSetting(Color(128, 255, 50))
    default_size = SizeSetting(1.5)

    def __init__(self) -> None:
        super().__init__()
    
    @property
    def file(self) -> File | Directory:
        """
        Returns the file (or directory) node that this handle is working on.
        """
        from .relations import UsesDirectory, UsesFile
        for e in self.edges:
            if isinstance(e, UsesFile | UsesDirectory):
                return e.destination
        raise RuntimeError("Got a Handle working on no File or Directory.")





del Color, ColorSetting, SizeSetting, DataVertex, logger, pathlib