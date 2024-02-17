"""
This module contains integration protocols for this behavioral package.
"""

from .....logger import logger
from ...build import BuildingPhase
from ...utils import chrono
from . import entities, relations
from .utils import CallHandler

__all__ = []





logger.info("Loading integrations from {} library.".format(__name__.rpartition(".")[0].rpartition(".")[2]))

@chrono
def integrate_thread_creation(c : entities.Call):
    """
    Links a Thread vertex to the Call vertex (from another thread) that created it.
    """
    from .....logger import logger
    from .entities import Thread
    from .relations import InjectedThread, StartedThread
    if c.arguments.thread_identifier != 0:      # Should indicate that the call failed
        logger.debug("New thread detected.")
        for t in Thread:
            if t.TID == c.arguments.thread_identifier:
                break
        else:
            t = Thread(TID = c.arguments.thread_identifier, start = c.time, stop = float("inf"))
        if c.name in {"CreateRemoteThread", "CreateRemoteThreadEx"}:
            l = StartedThread(c, t, remote = True)
            logger.debug("Detected thread injection.")
            l.remote = True
            p = c.thread.process
            InjectedThread(p, t)
        else:
            l = StartedThread(c, t, remote = False)

@chrono
def integrate_process_creation(c : entities.Call):
    """
    Links a Process vertex to the Call vertex (from another process) that created it.
    """
    from .....logger import logger
    from .entities import Process
    from .relations import StartedProcess
    from ...utils import parse_command_line, path_factory
    if c.arguments.process_identifier != 0:
        logger.debug("New process detected.")
        for p in Process:
            if p.PID == c.arguments.process_identifier and p.command == c.arguments.command_line:
                break
        else:
            p = Process(PID = c.arguments.process_identifier, command = c.arguments.command_line, executable = path_factory(c.arguments.filepath) if c.arguments.filepath else path_factory(parse_command_line(c.arguments.command_line)[0]), start = c.time)
        l = StartedProcess(c, p)
        




# Thread creation handlers
CallHandler(integrate_thread_creation, "CreateThread")          # Basic thread creation
CallHandler(integrate_thread_creation, "CreateRemoteThread", "CreateRemoteThreadEx")    # Remote thread creation (into another process)

# Process creation handlers
CallHandler(integrate_process_creation, lambda name : "CreateProcess" in name)





__N_phase = BuildingPhase.request_finalizing_phase()

@chrono
def remove_cuckoo_phantom_processes(ev : BuildingPhase):
    """
    When called with the right finalizing phase event, will cause Process nodes which represent Cuckoo process (inital processes with no info available) to be erased.
    """
    from .....logger import logger
    from ...graph import Graph
    from ..network import Host, SpawnedProcess
    from .entities import Process
    if ev.major == "Finalizer" and ev.minor == __N_phase:
        logger.debug("Erasing Cuckoo phantom processes.")
        n = 0
        h = Host.current
        for e in h.edges.copy():
            p = e.destination
            if isinstance(p, Process) and not p.parent_process and not p.executable:
                for pi in p.children_processes:
                    SpawnedProcess(h, pi)
                for ei in p.edges.copy():
                    if isinstance(e, SpawnedProcess):
                        h = e.source
                    ei.delete()
                    for g in Graph.active_graphs():
                        g.remove(ei)
                for g in Graph.active_graphs():
                    g.remove(p)
                n += 1
        if n:
            logger.debug("Actually removed {} Cuckoo process{}.".format(n, "es" if n > 1 else ""))





BuildingPhase.add_callback(remove_cuckoo_phantom_processes)





del BuildingPhase, CallHandler, chrono, entities, integrate_process_creation, integrate_thread_creation, logger, relations, remove_cuckoo_phantom_processes