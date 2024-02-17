"""
This module defines some useful functions for manipulating the BAGUETTE graph typing system.
"""

from functools import cache
from types import ModuleType
from .. import types as type_package
from ..graph import Edge, Vertex

__all__ = ["types", "relations", "relation_types", "behavioral_packages", "baguette_structure"]





@cache
def types(mod : ModuleType = type_package) -> set[type[Vertex]]:
    """
    Returns the list of available Vertex types available in a given module or package (recursively). Defaults to the BAGUETTE's types package.
    """
    from ..graph import Vertex
    from types import ModuleType

    if not isinstance(mod, ModuleType):
        raise TypeError("Expected module or package, got " + repr(type(mod).__name__))

    type_set : set[type[Vertex]] = set()
    package_name = mod.__name__

    for name in dir(mod):
        value = getattr(mod, name)
        if isinstance(value, type) and issubclass(value, Vertex):
            type_set.add(value)
        elif isinstance(value, ModuleType):
            name = value.__name__.rpartition(".")[0]
            if name == package_name:
                type_set.update(types(value))
    
    return type_set





@cache
def relations(mod : ModuleType = type_package) -> set[type[Edge]]:
    """
    Returns the list of available Edge and Arrow types available in a given module or package (recursively). Defaults to the BAGUETTE's types package.
    """
    from ..graph import Edge
    from types import ModuleType

    if not isinstance(mod, ModuleType):
        raise TypeError("Expected module or package, got " + repr(type(mod).__name__))

    type_set : set[type[Edge]] = set()
    package_name = mod.__name__

    for name in dir(mod):
        value = getattr(mod, name)
        if isinstance(value, type) and issubclass(value, Edge):
            type_set.add(value)
        elif isinstance(value, ModuleType):
            name = value.__name__.rpartition(".")[0]
            if name == package_name:
                type_set.update(relations(value))
    
    return type_set





def behavioral_packages() -> dict[str, ModuleType]:
    """
    Returns a dictionary holding all the avaiable behavioral packages in the form {name : package}.
    Such packages can be used with types() and relations().
    """
    from .. import types as type_package

    index = {}
    package_name = type_package.__name__
    for name in dir(type_package):
        value = getattr(type_package, name)
        if isinstance(value, ModuleType):
            pname, _, mname = value.__name__.rpartition(".")
            if name == package_name:
                index[mname] = value

    return index





@cache
def relation_types(edge_class : type[Edge]) -> tuple[tuple[type[Vertex]], tuple[type[Vertex]]]:
    """
    Given an Edge or Arrow subclass, gives the best type hints for the source and destination vertices.
    Defaults to (Vertex, Vertex) when no annotations exist.
    """
    from typing import get_type_hints
    from types import UnionType
    from ..graph import Edge, Vertex

    if not isinstance(edge_class, type) or not issubclass(edge_class, Edge):
        raise TypeError("Expected Edge subclass, got " + repr(edge_class))

    hints = get_type_hints(edge_class)
    S, D = hints.get("source", Vertex), hints.get("destination", Vertex)
    if isinstance(S, UnionType):
        S = tuple(S.__args__)
    else:
        S = (S, )
    if isinstance(D, UnionType):
        D = tuple(D.__args__)
    else:
        D = (D, )
    return S, D





def baguette_structure():
    """
    A dynamic clone of 'baguette.croutons.source.utils.baguette_structure'.
    """
    from ....croutons.source.utils import baguette_structure
    return baguette_structure()
    




del cache, ModuleType, type_package, Edge, Vertex