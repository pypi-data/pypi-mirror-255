"""
This module contains utilities to manage BAGUETTE data. For more information, look at the BaguetteRack class.
"""

from pathlib import Path
from traceback import TracebackException
from typing import Any, Literal, TypeVar

from .croutons.source.metagraph import MetaGraph
from .bakery.source.filters import Filter
from .bakery.source.graph import Graph
from .bakery.source.colors import Color

__all__ = ["BaguetteRack", "TimeoutExit"]





class TimeoutExit(SystemExit):
    """
    This exception means that a critical timeout has been reached, causing interpreter exit when raised.
    """

T = TypeVar("T", bound="BaguetteRack")

class BaguetteRack:

    """
    Baguette racks are just a utility to organize baguettes easily.
    They have MANY properties that can be changed to manage BAGUETTEs.
    Remember to export() them before deleting them, as this will write the index file.
    """

    __slots__ = {
        "__working_directory" : "The absolute path to the working directory",
        "__perf" : "A boolean indicating if a performance report should be returned",
        "__filters" : "The list if filters applied during the compilation phase",
        "__patterns" : "The list of MetaGraphs to search for during the extraction phase",
        "__skip_data_comparison" : "A boolean indicating if Data nodes were compared during compilation",
        "__skip_diff_comparison" : "A boolean indicating if Diff nodes were compared during compilation",
        "__exception" : "The last caught exception",
        "__baked" : "Indicates if the baguette has been successfully baked",
        "__toasted" : "Indicates if the baguette has been successfully toasted",
        "__verbosity" : "The verbosity level to apply when baking or toasting", 
        "__maxtime" : "The maximum amount of time to spend on this baguette",
        "__paint_color" : "The color to use to paint MetaGraph matches in the visual file",
        "__suppressed" : "Indicates if an exception should suppress the index file output",
        "__background_color" : "The color of the background for the visual graph",
        "__save_filtered_baguette" : "Indicates if the Graph has been saved after applying filters",
        "__report_type" : "The type of execution report used as a source"
    }

    __pickle_slots__ = {
        "perf",
        "filter_names",
        "pattern_names",
        "skip_data_comparison",
        "skip_diff_comparison",
        "exception",
        "baked",
        "toasted",
        "verbosity",
        "maxtime",
        "paint_color",
        "suppressed",
        "background_color",
        "save_filtered_baguette",
        "report_type"
    }

    names = {
        "working_directory" : "BAGUETTE Directory",
        "index" : "BAGUETTE Index File",
        "report" : "Cuckoo Report File",
        "baguette" : "Python BAGUETTE File",
        "visual" : "Gephi File",
        "extracted" : "Extracted MetaGraphs Python File",
    }

    def __init__(self, working_directory : str | Path) -> None:
        from pathlib import Path
        from traceback import TracebackException
        from typing import Literal
        from .bakery.source.colors import Color
        from .bakery.source.parsers import AbstractParser
        self.__working_directory : Path = Path(working_directory)
        self.__perf : bool = False
        self.__filters : list[str] = []
        self.__patterns : list[str] = []
        self.__skip_data_comparison : bool = False
        self.__skip_diff_comparison : bool = False
        self.__exception : TracebackException | None = None
        self.__baked : bool = False
        self.__toasted : bool = False
        self.__verbosity : Literal[0, 1, 2, 3] = 0
        self.__maxtime : float = float("inf")
        self.__paint_color : list[Color] | None = None
        self.__suppressed : bool = False
        self.__background_color : Color = Color.black
        self.__save_filtered_baguette : bool = False
        self.__report_type : str = AbstractParser.report_name
        if not isinstance(working_directory, str | Path):
            raise TypeError("Expected Path, got " + repr(type(working_directory).__name__))
    
    def __getstate__(self):
        return {name : getattr(self, name) for name in self.__pickle_slots__}
    
    def __setstate__(self, state : dict[str, Any]):
        self.__filters = []
        self.__patterns = []
        for name, value in state.items():
            setattr(self, name, value)

    @property
    def working_directory(self) -> Path:
        """
        The path where to find this baguette.
        """
        return self.__working_directory
    
    @property
    def index(self) -> Path:
        """
        The path to the index file which stores the paths to all parts of the baguette.
        """
        return self.working_directory / "index.pyt"
    
    @property
    def baguette(self) -> Path:
        """
        The path to the baguette file itself (the pickle of the baguette graph) (.pyt).
        """
        return self.working_directory / "baguette.pyt"

    @property
    def visual(self) -> Path:
        """
        The path to the visual representation file of the baguette (.gexf).
        """
        return self.working_directory / "visual.gexf"
    
    @property
    def extracted(self) -> Path:
        """
        The path to the metagraph search results file for this baguette (.pyt).
        """
        return self.working_directory / "extracted.pyt"
        
    @property
    def suppressed(self) -> bool:
        """
        Indicates if a raised exception should suppress the output file writing.
        """
        return self.__suppressed

    @suppressed.setter
    def suppressed(self, value : bool):
        if not isinstance(value, bool):
            raise TypeError(f"Expected bool, got '{type(value).__name__}'")
        self.__suppressed = value

    @property
    def paint_color(self) -> list[Color] | None:
        """
        The Colors in which to paint the MetaGraph matches found during toasting.
        The index of the color correspond to the index of the MetaGraph in the "patterns" attribute.
        None indicates no painting.
        """
        return self.__paint_color
    
    @paint_color.setter
    def paint_color(self, value : list[Color] | None):
        from .bakery.source.colors import Color
        if value is not None and not isinstance(value, list):
            raise TypeError("Expected None or list of Colors, got " + repr(type(value).__name__))
        if isinstance(value, list):
            for c in value:
                if not isinstance(c, Color):
                    raise TypeError("Expected list of Colors, got a " + repr(type(c).__name__))
        self.__paint_color = value

    @property
    def background_color(self) -> Color:
        """
        The background color that will be used for the visual file.
        This is used to change the color settings which are too close from the background color in order to make the visual sharper.
        """
        return self.__background_color
    
    @background_color.setter
    def background_color(self, value : Color):
        from .bakery.source.colors import Color
        if not isinstance(value, Color):
            raise TypeError(f"Expected Color, got '{type(value).__name__}'")
        self.__background_color = value

    @property
    def maxtime(self) -> float:
        """
        The maximum amount of time (in seconds) to spend on the baking or toasting process of this baguette.
        Defaults to infinity.
        """
        return self.__maxtime

    @maxtime.setter
    def maxtime(self, value : float):
        from math import isnan
        if not isinstance(value, float):
            raise TypeError("Expected float, got " + repr(type(value).__name__))
        if value <= 0 or isnan(value):
            raise ValueError("Expected positive value for timeout, got {}".format(value))
        self.__maxtime = value

    @property
    def verbosity(self) -> Literal[0, 1, 2, 3]:
        """
        The verbosity level that should be applied when baking or toasting this baguette.
        0 : Errors only (default)
        1 : Warnings
        2 : Info
        3 : Debug
        """
        return self.__verbosity

    @verbosity.setter
    def verbosity(self, value : Literal[0, 1, 2, 3]):
        if not isinstance(value, int):
            raise TypeError("Expected int, got " + repr(type(value).__name__))
        if value not in {0, 1, 2, 3}:
            raise ValueError("Verbosity should be in range(4), got {}".format(value))
        self.__verbosity = value

    @property
    def baked(self) -> bool:
        """
        Indicates if the baguette has been successfully baked.
        """
        return self.__baked
    
    @baked.setter
    def baked(self, value : bool):
        if not isinstance(value, bool):
            raise TypeError("Expected bool, got " + repr(type(value).__name__))
        self.__baked = value
    
    @property
    def toasted(self) -> bool:
        """
        Indicates if the baguette has been successfully toasted.
        """
        return self.__toasted
    
    @toasted.setter
    def toasted(self, value : bool):
        if not isinstance(value, bool):
            raise TypeError("Expected bool, got " + repr(type(value).__name__))
        self.__toasted = value
    
    @property
    def exception(self) -> TracebackException | None:
        """
        The last caught exception in the baking or toasting process if any.
        """
        return self.__exception
    
    @exception.setter
    def exception(self, value : TracebackException | None):
        from traceback import TracebackException
        if value is not None and not isinstance(value, TracebackException):
            raise TypeError("Expected TracebackException or None, got " + repr(type(value).__name__))
        self.__exception = value
        
    @property
    def perf(self) -> bool:
        """
        Indicates if the current baguette should be baked or toasted with a performance report.
        """
        return self.__perf
    
    @perf.setter
    def perf(self, value : bool):
        if not isinstance(value, bool):
            raise TypeError("Expected bool, got " + repr(type(value).__name__))
        self.__perf = value

    @property
    def patterns(self) -> list[MetaGraph]:
        """
        The MetaGraph patterns to search for during the baking of this baguette.
        """
        from .croutons import metalib
        from .croutons.source.metagraph import MetaGraph
        l = []
        for name in self.__patterns:
            p = getattr(metalib, name)
            if isinstance(p, MetaGraph):
                l.append(p)
        return l
    
    def add_pattern(self, name : str):
        """
        Adds a MetaGraph pattern from its name in the metalib.
        """
        if not isinstance(name, str):
            raise TypeError("Expected str, got " + repr(type(name).__name__))
        from .croutons import metalib
        if name not in dir(metalib):
            raise NameError("No MetaGraph named '{}'".format(name))
        self.__patterns.append(name)

    def clear_patterns(self):
        """
        Clears the MetaGraph patterns set for this baguette.
        """
        self.__patterns.clear()
    
    @property
    def pattern_names(self) -> list[str]:
        """
        The list of MetaGraphs applied to this baguette as named in the metalib.
        """
        return self.__patterns.copy()

    @pattern_names.setter
    def pattern_names(self, value : list[str]):
        if not isinstance(value, list):
            raise TypeError("Expected list, got " + repr(type(value).__name__))
        for name in value:
            if not isinstance(name, str):
                raise TypeError("Expected list of str, got a " + repr(type(name).__name__))
            
        old, self.__patterns = self.__patterns, []
        try:
            for name in value:
                self.add_pattern(name)
        except:
            self.__patterns = old
            raise

    @property
    def filters(self) -> list[Filter]:
        """
        The filters to apply/applied during the baking of this baguette.
        """
        from .bakery.source import filters
        l = []
        for name in self.__filters:
            f = getattr(filters, name)
            if isinstance(f, filters.Filter):
                l.append(f)
        return l

    def add_filter(self, name : str):
        """
        Adds a baguette filter from its name in the filters module.
        """
        if not isinstance(name, str):
            raise TypeError("Expected str, got " + repr(type(name).__name__))
        from .bakery.source import filters
        if name not in dir(filters):
            raise NameError("No Filter named '{}'".format(name))
        self.__filters.append(name)
    
    def clear_filters(self):
        """
        Clears the filters set for this baguette.
        """
        self.__filters.clear()
    
    @property
    def filter_names(self) -> list[str]:
        """
        The list of Filters applied to this baguette as named in the module filters.
        """
        return self.__filters.copy()

    @filter_names.setter
    def filter_names(self, value : list[str]):
        if not isinstance(value, list):
            raise TypeError("Expected list, got " + repr(type(value).__name__))
        for name in value:
            if not isinstance(name, str):
                raise TypeError("Expected list of str, got a " + repr(type(name).__name__))
            
        old, self.__filters = self.__filters, []
        try:
            for name in value:
                self.add_filter(name)
        except:
            self.__filters = old
            raise

    @property
    def skip_data_comparison(self) -> bool:
        """
        Indicates if Data nodes should be compared during the baking process.
        Useful for performance increase, but some information may be missing.
        """
        return self.__skip_data_comparison
    
    @skip_data_comparison.setter
    def skip_data_comparison(self, value : bool):
        if not isinstance(value, bool):
            raise TypeError("Expected bool, got " + repr(type(value).__name__))
        self.__skip_data_comparison = value

    @property
    def skip_diff_comparison(self) -> bool:
        """
        Indicates if Diff nodes should be compared during the baking process.
        Useful for performance increase, but some information may be missing.
        """
        return self.__skip_diff_comparison
    
    @skip_diff_comparison.setter
    def skip_diff_comparison(self, value : bool):
        if not isinstance(value, bool):
            raise TypeError("Expected bool, got " + repr(type(value).__name__))
        self.__skip_diff_comparison = value

    @property
    def save_filtered_baguette(self) -> bool:
        """
        Indicates if the BAGUETTE Graph was saved after the filtering phase during compilation.
        If True, the BAGUETTE file and the visual file will actually contain the same graph. Otherwise, the BAGUETTE file contains the file before filtering.
        """
        return self.__save_filtered_baguette
    
    @save_filtered_baguette.setter
    def save_filtered_baguette(self, value : bool):
        if not isinstance(value, bool):
            raise TypeError("Expected bool, got " + repr(type(value).__name__))
        self.__save_filtered_baguette = value

    @property
    def report_type(self) -> str:
        """
        The type of execution report that this BAGUETTE was compiled from.
        """
        return self.__report_type
    
    @report_type.setter
    def report_type(self, value : str):
        from .bakery.source.parsers import parsers, AbstractParser
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got '{type(value).__name__}'")
        if value not in {p.report_name for p in parsers} | {AbstractParser.report_name}:
            raise ValueError(f"Expected one of {(AbstractParser.report_name, ) + tuple(p.report_name for p in parsers)}, got '{value}'")
        self.__report_type = value
    
    @report_type.deleter
    def report_type(self):
        from .bakery.source.parsers import AbstractParser
        self.__report_type = AbstractParser.report_name
        
    def export(self):
        """
        Writes the information of this baguette to the index file.
        Does nothing if the path to the index file has not been set yet.
        """
        from pickle import dump
        self.__working_directory.mkdir(parents = True, exist_ok = True)
        with open(self.__working_directory / "index.pyt", "wb") as f:
            dump(self, f)
    
    @classmethod
    def import_from(cls : type["BaguetteRack"], path : str | Path) -> "BaguetteRack":
        """
        Loads the information on a baguette from the given index path.
        """
        from pathlib import Path
        from pickle import load, UnpicklingError
        if not isinstance(path, str | Path):
            raise TypeError("Expected Path, got " + repr(type(path).__name__))
        if isinstance(path, str):
            try:
                path = Path(path)
            except BaseException as e:
                raise e from None
        path = path.expanduser().resolve()
        try:
            with path.open("rb") as f:
                rack : BaguetteRack = load(f)
        except UnpicklingError:
            raise TypeError(f"Could not load baguette in file '{path}'")
        if not isinstance(rack, cls):
            raise TypeError(f"Object in file '{path}' is not a '{cls.__name__}'")
        rack.__working_directory = path.parent
        return rack
    
    def clean(self):
        """
        Cleans the whole baguette. This will remove all of its files and the .bag folder (working directory) if they exist.
        """
        from os import remove, rmdir
        if self.index.is_file():
            remove(self.index)
        if self.baguette.is_file():
            remove(self.baguette)
        if self.visual.is_file():
            remove(self.visual)
        if self.extracted.is_file():
            remove(self.extracted)
        if not list(self.working_directory.iterdir()):
            rmdir(self.working_directory)

    @property
    def compilation_failed(self) -> bool:
        """
        This value indicates if the compilation resulted in an Exception.
        """
        return not self.baked and self.exception != None
    
    @property
    def compilation_interrupted(self) -> bool:
        """
        This value indicates if the compilation failed because it took too long or was interrupted.
        """
        return self.compilation_failed and self.exception != None and issubclass(self.exception.exc_type, (TimeoutExit, KeyboardInterrupt))

    def exists(self) -> bool:
        """
        This method tests whether or not an index file already exist where this one should be exported to.
        """
        return self.index.exists()

    def load(self) -> Graph:
        """
        Loads and returns the baguette associated to this graph.
        """
        if not self.baguette.exists():
            raise FileNotFoundError("Baguette file does not exist")
        if not self.baguette.is_file():
            raise FileExistsError("Baguette path exists but is not a file")
        from pickle import load
        from baguette.bakery.source.graph import Graph
        with self.baguette.open("rb") as f:
            bag = load(f)
            if not isinstance(bag, Graph):
                raise RuntimeError("Given baguette file did not contain a BAGUETTE graph")
            return bag





del Path, T, TypeVar, Any, TracebackException