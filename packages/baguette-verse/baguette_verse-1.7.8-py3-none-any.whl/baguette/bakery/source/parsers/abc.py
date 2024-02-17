"""
This module defines the abstract bases classes for the parsing system.
"""

from abc import ABCMeta, abstractmethod
from pathlib import Path, PurePath
from types import NotImplementedType
from typing import Any, Iterable, Literal
from dataclasses import dataclass

from .utils import Translator

__all__ = ["AbstractParser", "ProcessInfo", "ImportInfo", "ThreadInfo", "CallInfo", "MachineInfo"]





@dataclass
class ProcessInfo:

    """
    A structure to hold some generic information about a process. 
    """

    PID : int
    start : float
    stop : float
    threads : "tuple[ThreadInfo, ...]"
    command : str
    executable : PurePath
    imports : "tuple[ImportInfo, ...]"


@dataclass
class ImportInfo:

    """
    A structure to hold some generic information about a static import of a process.
    """

    path : PurePath
    size : int


@dataclass
class ThreadInfo:

    """
    A structure to hold some generic information about a thread.
    """

    TID : int
    start : float
    stop : float
    calls : "tuple[CallInfo, ...]"


@dataclass
class CallInfo:

    """
    A structure to hold the information available about a specific API call.
    """

    API : str
    status : bool
    return_value : int
    arguments : dict[str, Any]
    flags : dict[str, Any]
    time : float


@dataclass
class MachineInfo:

    """
    A structure to hold the information about a machine that appeared during the analysis.
    """

    IP : str
    hostname : str | None
    domain : str | None





class AbstractParser(metaclass = ABCMeta):

    """
    An abstract parser class for execution reports. If you want BAGUETTE to handle a new type of input report, you need to create a specialized Parser subclass.
    It should define some basic requests using the content of the report but it must in particular define the API call translation table.
    """

    __Translator = Translator
    from pathlib import Path as __Path

    def __init_subclass__(cls) -> None:
        from .. import parsers
        parsers.parsers.append(cls)

    report_name : str = "universal"        # This is the name of the report type (e.g "cuckoo", "cape", etc.)

    @staticmethod
    def match_report_type(p : Path) -> bool | NotImplementedType:
        """
        If defined, given the path to a report, this function should tell whether or not this report is appropriate for this parser class.
        It should return True (for adequate), False (for inadequate) or NotImplemented (unsure).
        """
        return False
    
    @staticmethod
    def find_parser(p : Path) -> "type[AbstractParser] | None":
        """
        Tries to find the adequate parser for the file with the given path. Returns the Parser subclass on success, None otherwise.
        """
        from . import parsers
        candidates : "list[type[AbstractParser]]" = []
        for cls in parsers:
            match cls.match_report_type(p):
                case True:
                    return cls
                case NotImplemented:
                    candidates.append(cls)
        else:
            if len(candidates) == 1:
                return candidates[0]
    
    def __init__(self, p : Path) -> None:
        """
        Implements initialization of a parser instance given the path to the report.
        """
        self.__translator : "Translator | None" = None

    @property
    def translator(self) -> Translator:
        """
        The translator for API calls present in this report. 
        """
        if self.__translator is None:
            p = AbstractParser.__Path(__file__).parent / "translators" / f"{self.report_name}.json"
            if p.is_file():
                self.__translator = AbstractParser.__Translator.import_from_file(p)
            else:
                self.__translator = AbstractParser.__Translator()
        return self.__translator
    
    @abstractmethod
    def process_tree_iterator(self) -> Iterable[tuple[ProcessInfo | None, ProcessInfo]]:
        """
        Iterates over the different processes by parent-child pairs.
        The iteration is ordered so that a child should never appear in a pair before its parent.
        If the parent is unknown, (None, <child pid>) should be yielded.
        Note that this is a costly operation as each ProcessInfo instance should contain a list of ThreadInfo instances, each containing lists of CallInfo instances.
        """
        raise NotImplementedError
    
    @abstractmethod
    def machines(self) -> Iterable[MachineInfo]:
        """
        Iterates over the machine that appeared in the analysis, host machine included.
        """
        raise NotImplementedError
    
    @abstractmethod
    def host(self) -> MachineInfo:
        """
        Returns the network information about the host machine.
        """
        raise NotImplementedError
    
    @abstractmethod
    def sample_file_path(self) -> Path:
        """
        Returns the path to the sample tested in the host machine.
        """
        raise NotImplementedError
    
    @abstractmethod
    def platform(self) -> Literal["Windows", "Unix", ]:
        """
        Returns the Operating System on which the analysis was performed.
        """
        raise NotImplementedError





del ABCMeta, abstractmethod, Path, Translator