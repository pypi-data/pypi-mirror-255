"""
This module contains Vertex subclasses for this behavioral package.
"""

from pathlib import PurePath
from typing import Hashable, Mapping
from .....logger import logger
from ...colors import Color
from ...config import ColorSetting, SizeSetting
from ...graph import DataVertex
from ...utils import chrono

__all__ = ["Process", "Thread", "Call"]





logger.info("Loading entities from {} library.".format(__name__.rpartition(".")[0].rpartition(".")[2]))

CommandTree = list[tuple[str, "CommandTree"]]

class Process(DataVertex):

    """
    A process vertex. Holds information to identify a process.
    """

    from pathlib import PurePath as __PurePath

    __slots__ = {
        "__PID" : "The PID of the process during its execution",
        "__command" : "The command that this process is running",
        "__executable" : "The file system path that the process was started in",
        "__start" : "The time at which the process was started",
        "__stop" : "The time at chich the process was stopped",
        "__sub_commands" : "The tree of commands executed by all chile processes"
    }

    __defining_data__ = DataVertex.__defining_data__ | {
        "PID",
        "command",
        "executable",
        "start",
        "stop"
    }

    __computable_properties__ = DataVertex.__computable_properties__ | {
        "sub_commands"
    }

    default_color = ColorSetting(Color(255, 255, 50))
    default_size = SizeSetting(5.0)

    def __init__(self, *, PID : int, command : str, executable : PurePath, start : float = -float("inf"), stop : float = float("inf")) -> None:
        self.executable = executable        # Sometimes, the command property will need it for its setter. Set this one first.
        super().__init__(PID = PID, command = command, executable = executable, start = start, stop = stop)

        from argparse import ArgumentParser
        from pathlib import PurePath

        from ...utils import is_path, path_factory
        from ..filesystem.integration import NewFile
        from .relations import Runs, UsesAsArgument

        def to_absolute(p : PurePath, cwd : PurePath) -> PurePath:
            if p.is_absolute():
                return p
            return cwd / p
        
        p = ArgumentParser()
        
        def link(e : NewFile):
            from ..filesystem import File
            f = e.file
            if not f.name:
                return
            # print("New file :", repr(f.path))
            # # print("Process :", repr(self.command))
            # print("Process #{} : '{}'".format(self.PID, self.executable))
            # print("Splitting command : {}".format(self.__command))
            for i, arg in enumerate(self.__command):
                if not i:
                    arg = str(self.executable)
                while arg.endswith(" "):
                    arg = arg[:-1]
                while arg.startswith(" "):
                    arg = arg[1:]
                if arg.startswith("\"") and arg.endswith("\""):
                    arg = arg[1:-1]
                if arg.startswith("'") and arg.endswith("'"):
                    arg = arg[1:-1]
                # print(">>>", f.name.lower(), arg.lower())
                if (is_path(arg) and f.name.lower() == to_absolute(path_factory(arg), path_factory(str(self.executable))).name.lower()) or f.name.lower() in arg.lower():
                # if (f.name in arg and len(f.name) / len(arg) > 0.9) or (str(f.path) in arg and len(str(f.path)) / len(arg) > 0.9):        # You need to work with a process cwd
                    if i > 0:
                        UsesAsArgument(self, f)
                        break
                    else:
                        Runs(self, f)

        NewFile.add_callback(link)

    @property
    def PID(self) -> int:
        """
        The Process IDentifier.
        """
        return self.__PID
    
    @PID.setter
    def PID(self, i : int):
        if not isinstance(i, int):
            raise TypeError(f"Expected int, got '{type(i).__name__}'")
        self.__PID = i

    @property
    def command(self) -> str:
        """
        The command ran by this Process.
        """
        return " ".join(self.__command)
    
    @command.setter
    def command(self, cmd : str):
        from ...utils import parse_command_line
        if not isinstance(cmd, str):
            raise TypeError("Expected str, got " + repr(type(cmd).__name__))
        self.__command = tuple(parse_command_line(cmd))
        if not self.__command and self.executable:
            self.__command = (str(self.executable), )

    @property
    def start(self) -> float:
        """
        The time at which this process started its execution.
        """
        return self.__start
    
    @start.setter
    def start(self, t : float):
        if not isinstance(t, float):
            raise TypeError(f"Expected float, got '{type(t).__name__}'")
        self.__start = t

    @property
    def stop(self) -> float:
        """
        The time at which this process stopped its execution.
        """
        return self.__stop
    
    @stop.setter
    def stop(self, t : float):
        if not isinstance(t, float):
            raise TypeError(f"Expected float, got '{type(t).__name__}'")
        self.__stop = t

    @property
    def executable(self) -> PurePath:
        """
        The path to the executable that the process runs.
        """
        return self.__executable
    
    @executable.setter
    def executable(self, p : PurePath):
        if not isinstance(p, Process.__PurePath):
            raise TypeError(f"Expected PurePath, got '{type(p).__name__}'")
        self.__executable = p

    @property
    def sub_commands(self) -> CommandTree:
        """
        Returns a dict structure that represents the commands executed by all child processes.
        """
        from .relations import HasChildProcess
        sc = []
        for e in self.edges:
            if isinstance(e, HasChildProcess) and e.source is self:
                sc.append((e.destination.command, e.destination.sub_commands))
        return sc
    
    @property
    def label(self) -> str:
        """
        Returns a label for the Process node.
        """
        return "Process #" + str(self.PID)
        
    @property
    def threads(self) -> list["Thread"]:
        """
        List of all the threads that this process had.
        """
        from .relations import HasThread
        return [e.destination for e in self.edges if isinstance(e, HasThread)] 
    
    @property
    def children_processes(self) -> list["Process"]:
        """
        List of all the children processes that this process created.
        """
        from .relations import HasChildProcess
        return [e.destination for e in self.edges if isinstance(e, HasChildProcess) and e.source is self]
    
    @property
    def parent_process(self) -> "Process | None":
        """
        Returns the parent process node if one exists in the graph.
        """
        from .relations import HasChildProcess
        for e in self.edges:
            if isinstance(e, HasChildProcess) and e.destination is self:
                return e.source
        
    def parsed_command(self) -> list[str]:
        """
        Returns the argument vector used for starting this process.
        """
        return list(self.__command)





class Thread(DataVertex):

    """
    A thread vertex. Holds information to identify a thread.
    """

    __slots__ = {
        "__TID" : "The TID of the thread during its execution",
        "__n_calls" : "The number of system calls that the thread made",
        "__first" : "The first system call that this thread made",
        "__last" : "the last system call that this thread made",
        "__start" : "The time at which the thread was started",
        "__stop" : "The time at chich the thread was stopped"
    }

    __defining_data__ = DataVertex.__defining_data__ | {
        "TID",
        "start",
        "stop"
    }

    __additional_data__ = DataVertex.__additional_data__ | {
        "n_calls",
        "first",
        "last"
    }

    default_color = ColorSetting(Color(255, 204, 0))
    default_size = SizeSetting(2.0)

    def __init__(self, *, TID : int, start : float, stop : float) -> None:
        super().__init__(TID = TID, start = start, stop = stop)
        self.__n_calls : int = 0
        self.__first : Call | None = None
        self.__last : Call | None = None

    @property
    def TID(self) -> int:
        """
        The Thread IDentifier.
        """
        return self.__TID
    
    @TID.setter
    def TID(self, i : int):
        if not isinstance(i, int):
            raise TypeError(f"Expected int, got '{repr(type(i).__name__)}'")
        self.__TID = i

    @property
    def start(self) -> float:
        """
        The time (in seconds since the epoch) at which the thread was started.
        """
        return self.__start
    
    @start.setter
    def start(self, t : float):
        if not isinstance(t, float):
            raise TypeError(f"Expected float, got '{type(t).__name__}'")
        self.__start = t
    
    @property
    def stop(self) -> float:
        """
        The time (in seconds since the epoch) at which the thread exited.
        """
        return self.__stop
    
    @stop.setter
    def stop(self, t : float):
        if not isinstance(t, float):
            raise TypeError(f"Expected float, got '{type(t).__name__}'")
        self.__stop = t

    @property
    def n_calls(self) -> int:
        """
        The number of API calls captured for this thread.
        """
        return self.__n_calls
    
    @n_calls.setter
    def n_calls(self, n : int):
        if not isinstance(n, int):
            raise TypeError(f"Expected int, got '{type(n).__name__}'")
        self.__n_calls = n

    @property
    def first(self) -> "Call | None":
        """
        The first API call made by this thread (if any).
        """
        return self.__first
    
    @first.setter
    def first(self, c : "Call | None"):
        if c is not None and not isinstance(c, Call):
            raise TypeError(f"Expected Call or None, got '{type(c).__name__}'")
        self.__first = c

    @property
    def last(self) -> "Call | None":
        """
        The last API call made by this thread (if any).
        """
        return self.__last
    
    @last.setter
    def last(self, c : "Call | None"):
        if c is not None and not isinstance(c, Call):
            raise TypeError(f"Expected Call or None, got '{type(c).__name__}'")
        self.__last = c

    @property
    def label(self) -> str:
        """
        Returns a label for the Thread node.
        """
        return "Thread #" + str(self.TID)
    
    @property
    def process(self) -> Process:
        """
        The Process Vertex that runs this Thread.
        """
        from .relations import HasThread
        for e in self.edges:
            if isinstance(e, HasThread):
                return e.source
        raise RuntimeError("Got a Thread without a parent Process.")





ArgumentsDict = Mapping[str, Hashable]

class Call(DataVertex):

    """
    A system call vertex. Holds information about a specific system call.
    Don't forget to call c.integrate() after setup of Call c is finished to integrate the call in the graph.
    """

    from ...record import Record as __Record
    from typing import Hashable as __Hashable

    __slots__ = {
        "__name" : "The name of the system call",
        "__arguments" : "The arguments that the call received",
        "__flags" : "The flags of the call",
        "__status" : "Indicates if the call ran succesfully",
        "__return_value" : "The value that the call returned",
        "__time" : "The timestamp at which the call was detected",
        "__thread" : "A shortcut to the Thread vertex that made this call"
    }

    __defining_data__ = DataVertex.__defining_data__ | {
        "name",
        "arguments",
        "flags",
        "status",
        "return_value",
        "time"
    }

    __additional_data__ = DataVertex.__additional_data__ | {
        "thread"
    }

    default_color = ColorSetting(Color(255, 153, 0))
    default_size = SizeSetting(0.3)

    def __init__(self, *, name : str, arguments : ArgumentsDict, flags : ArgumentsDict, status : bool, return_value : int, time : float) -> None:
        super().__init__(name = name, arguments = arguments, flags = flags, status = status, return_value = return_value, time = time)
        self.__thread : Thread | None = None

    @property
    def name(self) -> str:
        """
        The name of the API call function.
        """
        return self.__name
    
    @name.setter
    def name(self, n : str):
        if not isinstance(n, str):
            raise TypeError(f"Expected str, got '{type(n).__name__}'")
        self.__name = n

    @property
    def arguments(self) -> __Record:
        """
        The arguments passed to the API function by pairs (argument name : argument value).
        """
        return self.__arguments

    @arguments.setter
    def arguments(self, args : ArgumentsDict | __Record):
        if not isinstance(args, dict):
            raise TypeError(f"Expected dict, got '{type(args).__name__}'")
        for k in args:
            if not isinstance(k, str):
                raise TypeError(f"Expected dict with str keys, got a '{type(k).__name__} key'")
        for v in args.values():
            if not isinstance(v, Call.__Hashable):
                raise TypeError(f"Expected dict with hashable values, got a '{type(v).__name__}' value in:\n{args}")
        self.__arguments = Call.__Record(**args)

    @property
    def flags(self) -> ArgumentsDict:
        """
        The flags passed to the API call.
        """
        return self.__flags
    
    @flags.setter
    def flags(self, f : ArgumentsDict):
        if not isinstance(f, dict):
            raise TypeError(f"Expected dict, got '{type(f).__name__}'")
        for k in f:
            if not isinstance(k, str):
                raise TypeError(f"Expected dict with str keys, got a '{type(k).__name__} key'")
        for v in f.values():
            if not isinstance(v, Call.__Hashable):
                raise TypeError(f"Expected dict with hashable values, got a '{type(v).__name__}' value in:\n{f}")
        self.__flags = f

    @property
    def status(self) -> bool:
        """
        Indicates if the API call was successful.
        """
        return self.__status
    
    @status.setter
    def status(self, b : bool):
        if not isinstance(b, bool):
            raise TypeError(f"Expected bool, got '{type(b).__name__}'")
        self.__status = b

    @property
    def return_value(self) -> int:
        """
        The return value as an integer.
        """
        return self.__return_value
    
    @return_value.setter
    def return_value(self, r : int):
        if not isinstance(r, int):
            raise TypeError(f"Expected int, got '{type(r).__name__}'")
        self.__return_value = r

    @property
    def time(self) -> float:
        """
        The time (in seconds since the epoch) at which the API call was made.
        """
        return self.__time
    
    @time.setter
    def time(self, t : float):
        if not isinstance(t, float):
            raise TypeError(f"Expected float, got '{type(t).__name__}'")
        self.__time = t
    
    @property
    def thread(self) -> Thread:
        """
        The Thread that made this Call.
        """
        if self.__thread is None:
            raise RuntimeError("Got a Call without a calling Thread.")
        return self.__thread
    
    @thread.setter
    def thread(self, value : Thread):
        if not isinstance(value, Thread):
            raise TypeError("Expected Thread, got " + repr(type(value).__name__))
        self.__thread = value

    @property
    def label(self) -> str:
        """
        The label for this node.
        """
        return self.name
    




del Color, ColorSetting, SizeSetting, CommandTree, DataVertex, Mapping, chrono, logger