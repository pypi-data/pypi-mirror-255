"""
This module defines some useful tools for MetaGraphs.
"""

from .metagraph import MetaGraph

__all__ = ["baguette_structure"]





def baguette_structure() -> MetaGraph:
    """
    Returns the structure graph of BAGUETTE. It contains all the possible relations in BAGUETTE.
    """
    from itertools import permutations, product
    from typing import TypeVar

    from ...bakery.source.graph import Arrow, Edge, Vertex
    from ...bakery.source.types.utils import relation_types, relations, types
    from .metagraph import MetaArrow, MetaEdge, MetaGraph, MetaVertex

    types_list = list(types())

    R : type[Edge]
    S : tuple[type[Vertex]]
    D : tuple[type[Vertex]]

    mg = MetaGraph()
    
    involved_in_source : dict[type[Vertex], set[type[Edge]]] = {}
    involved_in_destination : dict[type[Vertex], set[type[Edge]]] = {}

    for T in types_list:
        involved_in_destination[T] = set()
        involved_in_source[T] = set()

        for R in relations():
            S, D = relation_types(R)
            
            if issubclass(T, S):
                involved_in_source[T].add(R)
            
            if issubclass(T, D):
                involved_in_destination[T].add(R)

    vertex_merges : dict[type[Vertex], set[type[Vertex]]] = {}

    for Ti, Tj in permutations(types_list, 2):
            if involved_in_destination[Ti] == involved_in_destination[Tj] and involved_in_source[Ti] == involved_in_source[Ti]:
                
                if Ti in vertex_merges:
                    Si = vertex_merges[Ti]
                else:
                    Si = set()
                    vertex_merges[Ti] = Si
                if Tj in vertex_merges:
                    Sj = vertex_merges[Tj]
                else:
                    Sj = set()
                    vertex_merges[Tj] = Sj

                Si.add(Tj)
                Sj.add(Ti)
    
    vertex_groups : list[set[type[Vertex]]] = []

    for T in types_list:
        if T in vertex_merges:
            found = False
            for s in vertex_groups:
                if s & vertex_merges[T]:
                    s.add(T)
                    found = True
                    break
            if not found:
                vertex_groups.append({T})
        else:
            vertex_groups.append({T})

    TV = TypeVar("TV")
    def sort_classes(*cls : type[TV], ref : type[TV]) -> tuple[type[TV]]:
        """
        Sorts Vertex classes in inheritance order (parents first).
        """
        def count_to_vertex(t : type[ref]) -> int | float:
            if t == ref:
                return 0
            if not issubclass(t, ref):
                return float("inf")
            return min(count_to_vertex(ti) for ti in t.__bases__) + 1 # type: ignore
        return tuple(sorted(cls, key=count_to_vertex))
    
    vertex_map : dict[tuple[type[Vertex]], MetaVertex] = {}
    with mg:
        for vg in vertex_groups:
            vt = sort_classes(*vg, ref = Vertex)
            MV = MetaVertex()
            MV.cls = vt
            vertex_map[vt] = MV
    
    with mg:
        for (VTi, MVi), (VTj, MVj) in product(vertex_map.items(), vertex_map.items()):
            relation_set : set[type[Edge]] = set()
            for Ti, Tj in product(VTi, VTj):
                relation_set.update(involved_in_source.get(Ti, set()) & involved_in_destination.get(Tj, set()))
            arrows_to_merge : set[type[Arrow]] = set()
            edges_to_merge : set[type[Edge]] = set()
            for R in relation_set:
                if issubclass(R, Arrow):
                    arrows_to_merge.add(R)
                else:
                    edges_to_merge.add(R)
            if arrows_to_merge:
                MA = MetaArrow(MVi, MVj)
                MA.cls = sort_classes(*arrows_to_merge, ref = Arrow)
            if edges_to_merge:
                ME = MetaEdge(MVi, MVj)
                ME.cls = sort_classes(*edges_to_merge, ref = Edge)

    return mg





del MetaGraph