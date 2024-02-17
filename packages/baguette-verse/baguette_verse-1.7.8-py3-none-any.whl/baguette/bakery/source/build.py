"""
This module defines the compiler interface. Look at the Builder class.
"""

from io import IOBase
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Iterator

from ...logger import logger
from .event import Event
from .graph import Graph
from .types.execution.entities import Call, Process
from .utils import chrono
from .parsers.abc import ProcessInfo, CallInfo

__all__ = ["Builder", "build", "BuildingPhase"]





class BuildingPhase(Event):
    
    """
    This class of event is made to notify the system that we are entering a new buidling phase.
    The major attribute is the name of the phase.
    The minor attribute indicates the iteration number of this phase.
    """

    __lock = Lock()
    __extra_phases = 0

    __slots__ = {
        "major" : "The name of the phase of which the execution is starting.",
        "minor" : "The iteration number of this phase."
    }

    def __init__(self, major : str, minor : int) -> None:
        self.major = major
        self.minor = minor
    
    @staticmethod
    def request_finalizing_phase() -> int:
        """
        Requests a new finalizing phase to be performed by the Builder.
        Returns the integer assigned to the minor of the scheduled finalizer phase.
        """
        with BuildingPhase.__lock:
            n = BuildingPhase.__extra_phases
            BuildingPhase.__extra_phases += 1
            return n
    
    @staticmethod
    def finalizing_steps() -> int:
        """
        Returns the number of finalizing steps tp be performed.
        """
        with BuildingPhase.__lock:
            return BuildingPhase.__extra_phases





class Builder:

    """
    This class handles the building of BAGUETTEs. Just give the source file to the constructor and call build().
    """

    def __init__(self, p : Path, report_type : str | None = None) -> None:
        from ...logger import logger
        from .parsers import AbstractParser, parsers

        ParserCls = None
        for cls in parsers:
            if report_type == cls.report_name:
                ParserCls = cls
                logger.info(f"Info specified a {report_type} report")
                break
        
        if ParserCls is None:
            ParserCls = AbstractParser
        if ParserCls == AbstractParser:
            ParserCls = AbstractParser.find_parser(p)
        if ParserCls is None:
            raise ValueError(f"Could not determine the type of execution report that this file is : '{p}'")
        self.data = ParserCls(p)
        self._progress = 0
        self._target = 1
    
    @property
    def progress(self) -> float:
        """
        Returns the progress (between 0.0 and 1.0) of the current task.
        """
        return self._progress / self._target
    

    @chrono
    def build(self) -> None:
        """
        Builds the BAGUETTE from the source file.
        """
        BuildingPhase("Initialization", 0).throw()
        from threading import current_thread
        from .graph import Graph
        from .types.execution import (Call, FollowedBy, NextSignificantCall,
                                      Process, Thread)
        from .types.execution.utils import CallHandler
        from .types.filesystem.integration import declare_existing_file
        from .types.network import Host, SpawnedProcess
        from .utils import active_builders
        from ...logger import logger
        self.graph = Graph()
        self.graph.data["builder"] = self
        active_builders[current_thread()] = self

        try:
            with self.graph:

                BuildingPhase("Network Discovery", 0).throw()
                logger.info("Identifying machines.")

                hd = self.data.host()
                self.host = Host(address = hd.IP, name = hd.hostname or "host", domain = hd.domain or "", platform = self.data.platform())
                for machine in self.data.machines():
                    if machine.IP != hd.IP:
                        Host(address = machine.IP, name = machine.hostname or "", domain = machine.domain or "", platform = "")

                Host.current = self.host
                self.host.platform = self.data.platform()
                self.graph.data["platform"] = self.data.platform()

                BuildingPhase("Input Parsing", 0).throw()
                logger.debug("Discovering work on calls.")

                self._target = sum(len(t.calls) for p1, p2 in self.data.process_tree_iterator() for t in p2.threads)
                
                N_calls = self._target
                logger.info("{} Calls to find.".format(self._target))

                # Building the basic execution graph
                BuildingPhase("Graph Building", 0).throw()
                logger.info("Building execution star.")
                for parent, process in self.data.process_tree_iterator():
                    self.build_process_execution_trace(process, parent)

                # Creating a file node for the sample file.
                logger.debug("Creating sample file.")
                try:
                    path = self.data.sample_file_path()
                    declare_existing_file(path)
                except RuntimeError:
                    logger.error("Could not find the process executing the sample.")

                # Discovering calls
                logger.info("Discovering {} calls.".format(N_calls))
                calls : list[Call] = []
                self._target += len(Call) * 2
                for t in Thread:
                    a = t.first
                    while a is not None:
                        calls.append(a)
                        next_a = None
                        for l in a.edges:
                            if isinstance(l, FollowedBy) and l.destination is not a:
                                next_a = l.destination
                                break
                        a = next_a
                if len(calls) < N_calls:
                    logger.warning("{} calls have been forgotten!".format(N_calls - len(calls)))
                
                # Sorting calls based on time
                logger.info("Sorting calls based on time.")
                calls.sort(key = lambda a : a.time)

            with self.graph:    # We will export the created vertices and edges now
                # Interpreting each Call
                BuildingPhase("Call Interpretation", 0).throw()
                logger.info("Integrating {} calls.".format(N_calls))
                for a in calls:
                    CallHandler.integrate_chain(a)
                    self._progress += 1
                
            with self.graph:    # Again
                # Linking processes to host
                BuildingPhase("Process Attribution", 0).throw()
                logger.info("Linking root processes to host machine.")
                p : Process
                for p in Process:
                    if not p.parent_process:
                        SpawnedProcess(self.host, p)
                
            with self.graph:
                # Making skip links
                BuildingPhase("Call Skip-Linking", 0).throw()
                logger.info("Adding skip links in system call sequences")
                for t in Thread:
                    last = t.first
                    new = last
                    while new and last:
                        if new is not last:
                            for l in new.edges:
                                if not isinstance(l, FollowedBy):
                                    NextSignificantCall(last, new)
                                    last = new
                                    break
                        next_call = None
                        for l in new.edges:
                            if isinstance(l, FollowedBy) and l.destination is not new:
                                next_call = l.destination
                                break
                        new = next_call
                
                # Extra building phases
            for i in range(BuildingPhase.finalizing_steps()):
                with self.graph:
                    logger.info("Running finalization phase #{}.".format(i + 1))
                    BuildingPhase("Finalizer", i).throw()
            
        finally:
            self.graph.data.pop("builder")
            active_builders.pop(current_thread())


    @chrono
    def build_process_execution_trace(self, process : ProcessInfo, parent : ProcessInfo | None) -> Process:
        """
        Given the formatted source data of a process, creates the corresponding Process node, Thread nodes and the sequences of API Call nodes.
        """
        from ..source.types.execution import (FollowedBy,
                                              HasChildProcess, HasFirstCall,
                                              HasThread, Process, Thread)
        from ..source.types.imports import HasImport, Import

        p = Process(PID = process.PID, command = process.command, executable = process.executable, start = process.start, stop = process.stop)
        p.executable = process.executable
        if parent:
            for p2 in Process:
                if p2.PID == parent.PID and p2.start == p2.start:
                    HasChildProcess(p2, p)
                    break

        for imp in process.imports:
            basename = imp.path.name
            length = imp.size
            path = imp.path
            if basename.lower().endswith(".dll"):
                for imp in Import:
                    if imp.path == path and imp.size == length:
                        break
                else:
                    imp = Import(path = path, length = length)
                HasImport(p, imp)

        for ti in process.threads:
            t = Thread(TID = ti.TID, start = ti.start, stop = ti.stop)
            HasThread(p, t)
            i = -1
            for i, ci in enumerate(ti.calls):
                c = self.api_to_vertex(ci)
                c.thread = t
                if t.first is None:
                    HasFirstCall(t, c)
                    t.first = c
                    t.last = c
                elif t.last:
                    FollowedBy(t.last, c)
                    t.last = c
            t.n_calls = i + 1
        
        p.stop = max((t.stop for t in p.threads), default=p.start)

        return p

    @chrono
    def api_to_vertex(self, call : CallInfo) -> Call:
        """
        Given the formatted data from the source file, builds the corresponding Call node.
        """
        from ..source.record import Record
        from ..source.types.execution import Call
        a = Call(name = call.API,
                 arguments = Record(**call.arguments),
                 flags = Record(**call.flags),
                 status = call.status,
                 return_value = call.return_value,
                 time = call.time
                 )
        return a





def build(file : Path) -> "Graph":
    """
    Shortcut function to directly build a BAGUETTE from a source file. Returns the freshly-baked BAGUETTE.
    """
    b = Builder(file)
    b.build()
    return b.graph





del IOBase, Lock, Any, Dict, Iterator, logger, Event, Graph, Call, Process, chrono