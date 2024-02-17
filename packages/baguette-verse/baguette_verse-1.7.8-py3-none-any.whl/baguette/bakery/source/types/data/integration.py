"""
This module contains integration protocols for this behavioral package.
"""

from .....logger import logger
from ...build import BuildingPhase
from ...utils import chrono
from ..filesystem.entities import File, Handle
from ..network.entities import Connection, Socket
from . import entities, relations

__all__ = ["register_read_operation", "register_write_operation"]





logger.info("Loading integrations from {} library.".format(__name__.rpartition(".")[0].rpartition(".")[2]))

@chrono
def register_read_operation(target : File | Connection, vector : Handle | Socket, content : bytes | bytearray | memoryview | str, offset : int | None = None):
    """
    Registers a read operation to be added to the corresponding DiffNodes.
    """
    from .utils import Read, PreDiffDescriptor
    if isinstance(content, str):
        content = content.encode("utf-8")
    t = PreDiffDescriptor.get_target_diff_descriptor(target)
    v = PreDiffDescriptor.get_vector_diff_descriptor(vector)
    
    if offset == None:
        t.add_operation(Read(t.last_pos(), content))
        v.add_operation(Read(v.last_pos(), content))
    else:
        t.add_operation(Read(offset, content))
        v.add_operation(Read(offset, content))

@chrono
def register_write_operation(target : File | Connection, vector : Handle | Socket, content : bytes | bytearray | memoryview | str, offset : int | None = None):
    """
    Registers a write operation to be added to the corresponding DiffNodes.
    """
    from .utils import Write, PreDiffDescriptor
    if isinstance(content, str):
        content = content.encode("utf-8")
    t = PreDiffDescriptor.get_target_diff_descriptor(target)
    v = PreDiffDescriptor.get_vector_diff_descriptor(vector)
    
    if offset == None:
        t.add_operation(Write(t.last_pos(), content))
        v.add_operation(Write(v.last_pos(), content))
    else:
        t.add_operation(Write(offset, content))
        v.add_operation(Write(offset, content))


__N_diff_comparison_phase = BuildingPhase.request_finalizing_phase()
__N_diff_normalization_phase = BuildingPhase.request_finalizing_phase()
        

@chrono
def compile_diff_nodes(e : BuildingPhase):
    """
    When called with the right finalizing phase event, will cause all Diff nodes to compute their data attributes.
    """
    from time import time_ns

    from Viper.format import duration

    from .....logger import logger
    from ...config import CompilationParameters
    from .entities import Diff
    from .utils import PreDiffDescriptor
    if e.major == "Finalizer" and e.minor == __N_diff_comparison_phase:
        descriptors = PreDiffDescriptor.descriptors()
        logger.debug("Compiling{} {} Diff nodes.".format(" and comparing" if not CompilationParameters.SkipLevenshteinForDiffNodes else "", len(descriptors)))
        n = len(descriptors)
        t0 = time_ns()
        t = t0
        for i, d in enumerate(descriptors):
            if n == 0:
                breakpoint()
            Diff.process_data(d)
            if (time_ns() - t) / 1000000000 > 15:
                t = time_ns()
                logger.debug("Finalizing {} Diff nodes : {:.2f}%. ETA : {}".format(n, (i + 1) / n * 100, duration(round((t - t0) / (i + 1) * (n - i - 1)))))

@chrono
def normalize_diff_nodes(e : BuildingPhase):
    """
    When called with the right finalizing phase event, will cause all Diff nodes to compare their diff file sizes and change their size accordingly.
    Same for colors regarding entropy using the defined color scale.
    Also, Diff node size will also be proportional to the square root of the number of vectors and targets linked to them.
    """
    from typing import Type

    from .....logger import logger
    from ...colors import Color
    from ...graph import Vertex
    from ..filesystem import File, Handle
    from ..network import Connection, Socket
    from .entities import Diff
    from .relations import IsDiffOf

    def project_range(x : float, sa : float, sb : float, da : float, db : float) -> float:
        if sa == sb:
            return (da + db) / 2
        p = (x - sa) / (sb - sa)
        return p * (db - da) + da

    def normalize_neighbor(cls : Type[Vertex]):
        if len(cls) > 0:
            logger.debug("Normalizing {} {} nodes.".format(len(cls), cls.__name__))
            a, b = min(sum(v.size for v in u.neighbors() if isinstance(v, Diff)) for u in cls), max(sum(v.size for v in u.neighbors() if isinstance(v, Diff)) for u in cls)
            minsize = Diff.min_size
            maxsize = Diff.max_size
            for u in cls:
                u.size = project_range(sum(v.size for v in u.neighbors() if isinstance(v, Diff)), a, b, minsize, maxsize)

    if e.major == "Finalizer" and e.minor == __N_diff_normalization_phase:
        logger.debug("Normalizing sizes of {} Diff nodes.".format(len(Diff)))
        if len(Diff) == 0:
            return
        a, b = min(len(d.glob) for d in Diff), max(len(d.glob) for d in Diff)
        minsize = 0.5
        maxsize = 3.0
        for d in Diff:
            d.size = project_range(len(d.glob), a, b, minsize, maxsize) * len([e for e in d.edges if isinstance(e, IsDiffOf)]) ** 0.5
    
        for cls in (File, Handle, Socket, Connection):
            normalize_neighbor(cls)
        
        logger.debug("Normalizing colors of {} Diff nodes.".format(len(Diff)))
        a, b = min(d.glob_entropy for d in Diff), max(d.glob_entropy for d in Diff)
        for d in Diff:
            d.color = Color.linear((Diff.diff_low_entropy_color, Diff.diff_high_entropy_color), (1 - d.glob_entropy / 8, d.glob_entropy / 8))




        
BuildingPhase.add_callback(compile_diff_nodes)
BuildingPhase.add_callback(normalize_diff_nodes)





del BuildingPhase, Connection, File, Handle, Socket, chrono, entities, compile_diff_nodes, logger, normalize_diff_nodes, relations