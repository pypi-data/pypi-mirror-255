"""
This module contains Vertex subclasses for this behavioral package.
"""

from pathlib import PurePath
from .....logger import logger
from ...config import ColorSetting, SizeSetting
from ...colors import Color
from ...graph import DataVertex

__all__ = ["Import"]





logger.info("Loading entities from {} library.".format(__name__.rpartition(".")[0].rpartition(".")[2]))

class Import(DataVertex):
    
    """
    An import vertex. Shows the use of a DLL or equivalent.
    """

    from pathlib import PurePath as __PurePath

    __slots__ = {
        "__path" : "The path to the file.",
        "__length" : "The size in bytes of the file."
    }

    __defining_data__ = DataVertex.__defining_data__ | {
        "path"
    }

    __additional_data__ = DataVertex.__additional_data__ | {
        "length",
    }

    __computable_properties__ = DataVertex.__computable_properties__ | {
        "name"
    }

    __suspicious_keyword_names = {
        "crypt",
        "advapi",
        "kernel",
        "sock"
    }

    default_color = ColorSetting(Color(150, 150, 0))
    default_size = SizeSetting(0.75)

    suspicious_import_color = ColorSetting(Color(255, 150, 0))

    def __init__(self, *, path : PurePath, length : int = 0) -> None:
        super().__init__(path = path)
        self.length = length

    @property
    def path(self) -> PurePath:
        """
        The path to the imported file.
        """
        return self.__path
    
    @path.setter
    def path(self, p : PurePath):
        if not isinstance(p, Import.__PurePath):
            raise TypeError(f"Expected PurePath, got '{type(p).__name__}'")
        self.__path = p
        self.color = self.default_color
        for kw in self.__suspicious_keyword_names:
            if kw in p.name.lower():
                self.color = self.suspicious_import_color
                break

    @property
    def length(self) -> int:
        """
        The size of the import file in bytes.
        """
        return self.__length
    
    @length.setter
    def length(self, s : int):
        if not isinstance(s, int):
            raise TypeError(f"Expected int, got '{type(s).__name__}'")
        self.__length = s

    @property
    def name(self) -> str:
        """
        The name of the imported library.
        """
        return self.path.name
    
    @property
    def label(self) -> str:
        """
        Returns a label for this Import node.
        """
        return "Import {}".format(self.name.lower())
    




del Color, ColorSetting, SizeSetting, DataVertex, logger