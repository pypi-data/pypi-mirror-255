"""
This module defines all graph-related base classes.
Look at the classes Vertex, Edge, Arrow and Graph.
Vertex, Edge and Arrow classes are heavily subclasses in BAGUETTE. Look at package 'baguette.bakery.source.types' to know more.
"""

from threading import RLock, Thread
from types import UnionType
from typing import Any, Callable, Iterable, Iterator, Never, Optional, Self, TypeGuard, TypeVar, TypedDict, Union, overload
from weakref import WeakKeyDictionary, WeakValueDictionary
from .colors import Color
from .config import ColorSetting, SizeSetting, SwitchSetting, WeightSetting
from Viper.meta.iterable import InstanceReferencingClass
from Viper.collections import IsoSet

__all__ = ["Vertex", "Edge", "Arrow", "Graph", "FrozenGraph"]





class Vertex(metaclass = InstanceReferencingClass):

    """
    A vertex for a graph. Can be linked to other vertices and added to a graph.
    """

    from Viper.collections import IsoSet as __IsoSet
    from .colors import Color as __Color

    __slots__ = {
        "__edges" : "The set of edges linking this vertex to others.",
        "__size" : "The customized size of the vertex",
        "__color" : "The customized color of the vertex"
        }
    
    default_color = ColorSetting(Color.white)
    default_size = SizeSetting(2.0)

    def __init__(self) -> None:
        self.__edges : "Vertex.__IsoSet[Edge]" = Vertex.__IsoSet()
        self.__color : "Color | None" = None
        self.__size : "float | None" = None
        for g in Graph.active_graphs():
            g._register(self)

    @property
    def edges(self) -> IsoSet["Edge"]:
        return self.__edges

    @property
    def color(self) -> Color:
        """
        The Color of this Vertex.
        """
        if self.__color is not None:
            return self.__color
        return self.default_color
    
    @color.setter
    def color(self, value : Color):
        if not isinstance(value, Vertex.__Color):
            raise TypeError(f"Expected Color, got '{type(value).__name__}'")
        self.__color = value

    @color.deleter
    def color(self):
        self.__color = None

    @property
    def size(self) -> float:
        """
        The size of this Vertex.
        """
        if self.__size is not None:
            return self.__size
        return self.default_size
    
    @size.setter
    def size(self, value : float):
        if not isinstance(value, float):
            try:
                value = float(value)
            except:
                pass
        if not isinstance(value, float):
            raise TypeError("Expected float, got " + repr(type(value).__name__))
        if value < 0 or value in (float("inf"), float("nan")):
            raise ValueError("Expected positive finite number for size, got " + repr(value))
        self.__size = value
    
    @size.deleter
    def size(self):
        self.__size = None

    @property
    def label(self) -> str:
        """
        The label used when plotting this vertex.
        """
        return type(self).__name__
    
    def __str__(self) -> str:
        """
        Implements str(self).
        """
        return f"{type(self).__name__}['{self.label}']"
    
    def __setstate__(self, state : dict[str, Any]):
        """
        Implements loading of self.
        """
        self.__edges = Vertex.__IsoSet()
        for k, v in state.items():
            setattr(self, k, v)
    
    def __getstate__(self) -> dict[str, Any]:
        """
        Implements dumping of self.
        """
        return {
            "color" : self.color,
            "size" : self.size
        }
    
    def __copy__(self) -> Self:
        """
        Implements copy of self. Does not copy the edges this vertex is part of.
        """
        cp = type(self).__new__(type(self))
        cp.color = self.color
        cp.size = self.size
        return cp
    
    def __deepcopy__(self, memo : dict[int, Any]) -> Self:
        """
        Implements deepcopy of self. Does not copy the edges this vertex is part of.
        """
        cp = self.__copy__()
        memo[id(self)] = cp
        return cp
                    
    def neighbors(self) -> Iterator["Vertex"]:
        """
        Iterates over all the neighbor vertices.
        """
        for e in self.__edges:
            if e.source is self:
                yield e.destination
            else:
                yield e.source
    
    def outwards(self) -> Iterator["Vertex"]:
        """
        Iterates over the outwards neighbors of this vertex (neighbors linked by an outgoing arrow).
        """
        for e in self.__edges:
            if isinstance(e, Arrow) and e.source is self:
                yield e.destination
    
    def inwards(self) -> Iterator["Vertex"]:
        """
        Iterates over the inwards neighbors of this vertex (neighbors linked by an incomming arrow).
        """
        for e in self.__edges:
            if isinstance(e, Arrow) and e.destination is self:
                yield e.source
    
    def linked(self) -> Iterator["Vertex"]:
        """
        Iterates over the undirected neighbors if this vertex (neighbors linked by a strict edge).
        """
        for e in self.__edges:
            if not isinstance(e, Arrow):
                yield (e.source if e is not e.source else e.destination)

    def connect(self, o : "Vertex", *, directional : bool = False) -> "Edge":
        """
        Links this vertex to another. Directional indicates if the link should be an arrow instead of an edge.
        """
        if not isinstance(o, Vertex):
            raise TypeError("Expected vertex, got " + repr(o.__class__.__name__))
        if not isinstance(directional, bool):
            raise TypeError("Expected bool for directional, got" + repr(directional.__class__.__name__))
        if directional:
            e = Arrow(self, o)
        else:
            e = Edge(self, o)
        e.write()
        return e

    @classmethod
    def add_vertices_to_graph(cls : type["Vertex"], G : "Graph", fil : Optional[Callable[["Vertex"], bool]] = None):
        """
        Adds all vertices of this class to a graph.
        If given a filter function fil, only filtered vertices will be added.
        """
        if not isinstance(G, Graph):
            raise TypeError("Expected graph, got " + repr(G.__class__.__name__))
        if fil != None and not callable(fil):
            raise TypeError("Expected callable for filter, got " + repr(fil.__class__.__name__))
        if fil == None:
            G.vertices.update(cls)
        else:
            G.vertices.update(filter(fil, cls))
            




class Edge(metaclass = InstanceReferencingClass):

    """
    An (undirected) edge for a graph. Links two vertices together.
    """

    from .colors import Color as __Color
    from copy import deepcopy
    __deepcopy = staticmethod(deepcopy)
    del deepcopy

    __slots__ = {
        "__source" : "The source vertex.",
        "__destination" : "The destination vertex.",
        "__weight" : "The customized weight of the edge",
        "__color" : "The customized color of the edge"
    }

    default_color = ColorSetting(Color.white)
    default_weight = WeightSetting(1.0)

    blend_vertices_colors = SwitchSetting(True)

    def __init__(self, source : Vertex, destination : Vertex, *, auto_write : bool = True) -> None:
        if not isinstance(source, Vertex) or not isinstance(destination, Vertex):
            raise TypeError("Expected vertex, vertex, got " + repr(source.__class__.__name__) + " and " + repr(destination.__class__.__name__))
        if not isinstance(auto_write, bool):
            raise TypeError("Expected bool for write, got " + repr(auto_write.__class__.__name__))
        self.__source : Vertex = source
        self.__destination : Vertex = destination
        self.__color : "Color | None" = None
        self.__weight : "float | None" = None
        if auto_write:
            self.write()
        for g in Graph.active_graphs():
            g._register(self)

    @property
    def source(self) -> Vertex:
        """
        The source Vertex of this Edge.
        """
        return self.__source
    
    @source.setter
    def source(self, u : Vertex):
        if not isinstance(u, Vertex):
            raise TypeError(f"Expected Vertex, got '{type(u).__name__}'")
        self.__source = u

    @property
    def destination(self) -> Vertex:
        """
        The destination Vertex of this Edge.
        """
        return self.__destination
    
    @destination.setter
    def destination(self, v : Vertex):
        if not isinstance(v, Vertex):
            raise TypeError(f"Expected Vertex, got '{type(v).__name__}'")
        self.__destination = v

    @property
    def color(self) -> Color:
        """
        The Color of this Vertex.
        """
        if self.__color is not None:
            return self.__color
        if self.blend_vertices_colors:
            return Edge.__Color.average(self.source.color, self.destination.color)
        else:
            return self.default_color
    
    @color.setter
    def color(self, value : Color):
        if not isinstance(value, Edge.__Color):
            raise TypeError(f"Expected Color, got '{type(value).__name__}'")
        self.__color = value

    @color.deleter
    def color(self):
        self.__color = None
        
    @property
    def weight(self) -> float:
        """
        The weight of this Edge.
        """
        if self.__weight is not None:
            return self.__weight
        return self.default_weight
    
    @weight.setter
    def weight(self, value : float):
        if not isinstance(value, float):
            try:
                value = float(value)
            except:
                pass
        if not isinstance(value, float):
            raise TypeError("Expected float for weight, got " + repr(type(value).__name__))
        if value < 0 or value in (float("inf"), float("nan")):
            raise ValueError("Expected positive finite number for weight, got " + repr(value))
        self.__weight = value

    @weight.deleter
    def weight(self):
        self.__weight = None

    @property
    def label(self) -> str:
        """
        The label used when plotting this edge.
        """
        return type(self).__name__
    
    def __repr__(self) -> str:
        """
        Implements repr(self).
        """
        return super().__repr__() + f" between {repr(self.source)} and {repr(self.destination)}"
    
    def __str__(self) -> str:
        """
        Implements str(self).
        """
        return str(self.source) + f" --{type(self).__name__}-- " + str(self.destination)
    
    def __hash__(self) -> int:
        """
        Implements hash(self).
        """
        return hash(hash(self.source) ^ hash(self.destination))
    
    def __eq__(self, o: object) -> bool:
        """
        Implements self == o.
        """
        if not isinstance(o, type(self)):
            return False
        return (self.source == o.source and self.destination == o.destination) or (self.source == o.destination and self.destination == o.source)
        
    def __setstate__(self, state : dict[str, Any]):
        """
        Implements loading of self.
        """
        for k, v in state.items():
            setattr(self, k, v)
    
    def __getstate__(self) -> dict[str, Any]:
        """
        Implements dumping of self.
        """
        return {
            "source" : self.source,
            "destination" : self.destination,
            "color" : self.color,
            "weight" : self.weight
        }
    
    def __copy__(self) -> Self:
        """
        Implements copy(self).
        """
        cp = type(self).__new__(type(self))
        cp.source = self.source
        cp.destination = self.destination
        cp.color = self.color
        cp.weight = self.weight
        return cp
    
    def __deepcopy__(self, memo : dict[int, Any]) -> Self:
        """
        Implements deepcopy(self).
        """
        cp = self.__copy__()
        memo[id(self)] = cp
        cp.source = Edge.__deepcopy(self.source)
        cp.destination = Edge.__deepcopy(self.destination)
        return cp
        
    def write(self):
        """
        Writes this edge in the edges sets of both vertices.
        """
        self.source.edges.add(self)
        self.destination.edges.add(self)
    
    def delete(self) -> tuple[Vertex, Vertex]:
        """
        Deletes the link. (Deletes it from the vertices egde sets)
        """
        self.source.edges.discard(self)
        self.destination.edges.discard(self)
        return self.source, self.destination
    
    @classmethod
    def add_edges_to_graph(cls : type["Edge"], G : "Graph", fil : Optional[Callable[["Edge"], bool]] = None):
        """
        Adds all edges of this class to a graph.
        If given a filter function fil, only filtered edges will be added.
        """
        if not isinstance(G, Graph):
            raise TypeError("Expected graph, got " + repr(G.__class__.__name__))
        if fil != None and not callable(fil):
            raise TypeError("Expected callable for filter, got " + repr(fil.__class__.__name__))
        if fil == None:
            G.edges.update(cls)
        else:
            G.edges.update(filter(fil, cls))

    
        


class Arrow(Edge):

    """
    An arrow (directed) for a graph. Links two vertices together.
    """
        
    def __str__(self) -> str:
        """
        Implements str(self).
        """
        return str(self.source) + f" --{type(self).__name__}-> " + str(self.destination)
    
    def __hash__(self) -> int:
        """
        Implements hash(self).
        """
        return hash(-hash(self.source) ^ hash(self.destination))
    
    def __eq__(self, o: object) -> bool:
        """
        Implements self == o.
        """
        if not isinstance(o, type(self)):
            return False
        return self.source == o.source and self.destination == o.destination
    




class DataVertex(Vertex):
    
    """
    Subclasses of DataVertex have a set of defining attributes/properties which are used for equality and hashing.
    Each subsequent subclasses should extend this set (__defining_data__).
    They can also extend __additional_data__ to add some important (but not primary) properties also included in pickles.
    Finally, they have a __computable_properties__ that are just used by str().
    """

    from copy import deepcopy
    __deepcopy = staticmethod(deepcopy)
    del deepcopy

    __defining_data__ : set[str] = set()
    __additional_data__ : set[str] = set()
    __computable_properties__ : set[str] = set()
    __repr_computing : set[int] = set()
    __str_computing : set[int] = set()

    def __init__(self, **defining_or_additional_data : Any) -> None:
        for name, value in defining_or_additional_data.items():
            if name not in self.__defining_data__ and name not in self.__additional_data__:
                raise AttributeError(f"Vertex type '{type(self)}' has no defining or additional property or attribute '{name}'")
            setattr(self, name, value)
        super().__init__()

    def __eq__(self, value: object) -> TypeGuard[Self]:
        return type(self) == type(value) and (all(getattr(self, name) == getattr(value, name) for name in self.__defining_data__) if self.__defining_data__ else self is value)
    
    def __hash__(self) -> int:
        h = 0
        if not self.__defining_data__:
            return super().__hash__()
        for name in self.__defining_data__:
            h ^= hash(getattr(self, name))
        return hash(h)
    
    def __getstate__(self) -> dict[str, Any]:
        return Vertex.__getstate__(self) | {name : getattr(self, name) for name in self.__defining_data__ | self.__additional_data__}
    
    def __copy__(self) -> Self:
        cp = super().__copy__()
        for name in self.__defining_data__ | self.__additional_data__:
            setattr(cp, name, getattr(self, name))
        return cp

    def __deepcopy__(self, memo: dict[int, Any]) -> Self:
        cp = super().__deepcopy__(memo)
        for name in self.__defining_data__ | self.__additional_data__:
            setattr(cp, name, DataVertex.__deepcopy(getattr(self, name)))
        return cp
    
    def __repr__(self) -> str:
        if id(self) not in DataVertex.__repr_computing:
            DataVertex.__repr_computing.add(id(self))
            res = f"{type(self).__name__}({', '.join(f'{name} = {repr(getattr(self, name))}' for name in self.__defining_data__ | self.__additional_data__)})"
            DataVertex.__repr_computing.remove(id(self))
            return res
        else:
            return f"{type(self).__name__}(...)"
    
    def __str__(self) -> str:
        if id(self) not in DataVertex.__str_computing:
            DataVertex.__str_computing.add(id(self))
            res = f"{type(self).__name__}['{self.label}']({', '.join(f'{name} = {repr(getattr(self, name))}' for name in self.__defining_data__ | self.__additional_data__ | self.__computable_properties__)})"
            DataVertex.__str_computing.remove(id(self))
            return res
        else:
            return f"{type(self).__name__}(...)"




class DataEdge(Edge):

    """
    Subclasses of DataEdge have a set of defining attributes/properties which are used for equality and hashing.
    Each subsequent subclasses should extend this set (__defining_data__).
    They can also extend __additional_data__ to add some important (but not primary) properties also included in pickles.
    Finally, they have a __computable_properties__ that are just used by str().
    """

    from copy import deepcopy
    __deepcopy = staticmethod(deepcopy)
    del deepcopy

    __defining_data__ : set[str] = set()
    __additional_data__ : set[str] = set()
    __computable_properties__ : set[str] = set()
    __repr_computing : set[int] = set()
    __str_computing : set[int] = set()


    def __init__(self, source: Vertex, destination: Vertex, *, auto_write: bool = True, **defining_data : Any) -> None:
        for name, value in defining_data.items():
            if name not in self.__defining_data__ and name not in self.__additional_data__:
                raise AttributeError(f"Edge type '{type(self)}' has no defining or additional property or attribute '{name}'")
            setattr(self, name, value)
        super().__init__(source, destination)

    def __eq__(self, o: object) -> TypeGuard[Self]:
        return Edge.__eq__(self, o) and all(getattr(self, name) == getattr(o, name) for name in self.__defining_data__)
    
    def __hash__(self) -> int:
        h = 0
        for name in self.__defining_data__:
            h ^= hash(getattr(self, name))
        return hash(Edge.__hash__(self) * h)
    
    def __getstate__(self) -> dict[str, Any]:
        return Edge.__getstate__(self) | {name : getattr(self, name) for name in self.__defining_data__ | self.__additional_data__}
    
    def __copy__(self) -> Self:
        cp = super().__copy__()
        for name in self.__defining_data__ | self.__additional_data__:
            setattr(cp, name, getattr(self, name))
        return cp

    def __deepcopy__(self, memo: dict[int, Any]) -> Self:
        cp = super().__deepcopy__(memo)
        for name in self.__defining_data__ | self.__additional_data__:
            setattr(cp, name, DataEdge.__deepcopy(getattr(self, name)))
        return cp

    def __repr__(self) -> str:
        if id(self) not in DataEdge.__repr_computing:
            DataEdge.__repr_computing.add(id(self))
            res = f"{type(self).__name__}({', '.join(e for e in (repr(self.source), repr(self.destination)) + tuple(f'{name} = {repr(getattr(self, name))}' for name in self.__defining_data__ | self.__additional_data__))})"
            DataEdge.__repr_computing.remove(id(self))
            return res
        else:
            return f"{type(self).__name__}({repr(self.source)}, {repr(self.destination)}, ...)"

    def __str__(self) -> str:
        if id(self) not in DataEdge.__str_computing:
            DataEdge.__str_computing.add(id(self))
            res = f"{self.source} --{type(self).__name__}({', '.join(e for e in (f'{name} = {repr(getattr(self, name))}' for name in self.__defining_data__ | self.__additional_data__ | self.__computable_properties__))})-- {self.destination}"
            DataEdge.__str_computing.remove(id(self))
            return res
        else:
            return f"{type(self).__name__}({self.source}, {self.destination}, ...)"





class DataArrow(DataEdge, Arrow):

    """
    Subclasses of DataArrow have a set of defining attributes/properties which are used for equality and hashing.
    Each subsequent subclasses should extend this set (__defining_data__).
    They can also extend __additional_data__ to add some important (but not primary) properties also included in pickles.
    Finally, they have a __computable_properties__ that are just used by str().
    """

    def __eq__(self, o: object) -> bool:
        return Arrow.__eq__(self, o) and all(getattr(self, name) == getattr(o, name) for name in self.__defining_data__)

    def __hash__(self) -> int:
        h = 0
        for name in self.__defining_data__:
            h ^= hash(getattr(self, name))
        return hash(Arrow.__hash__(self) * h)

    def __str__(self) -> str:
        return f"{self.source} --{type(self).__name__}({', '.join(e for e in (f'{name} = {repr(getattr(self, name))}' for name in self.__defining_data__ | self.__additional_data__))})-> {self.destination}"





class _GraphStateDict(TypedDict):

    vertices : IsoSet[Vertex]
    edges : IsoSet[Edge]
    data : dict[str, Any]

class Graph:

    """
    A graph class. Add starting vertices and use explore() to complete the graph.
    Graph can be used in context managers to append all Vertices and Edges created in the current thread to the context Graph:
    >>> G = Graph()
    >>> with G:
    ...     u = Vertex()
    ...     e = Edge(u, u)
    ... 
    >>> u in G.vertices:
    True
    >>> e in G.edges:
    True
    """

    from Viper.collections.isomorph import IsoSet as __IsoSet, IsoDict as __IsoDict
    from typing import Iterable as __Iterable
    from threading import current_thread as __current_thread
    from copy import copy, deepcopy
    __deepcopy = staticmethod(deepcopy)
    __copy = staticmethod(copy)
    del copy, deepcopy

    __slots__ = {
        "vertices" : "The set of Vertices in this graph",
        "edges" : "The set of Edges in this graph",
        "data" : "A dictionary holding additional data for this graph",
        "__weakref__" : "A slot for weak references to Graph objects",
        "__to_append" : "A list of Vertices and Edges to be added at the exit of the context the current Graph is affected to"
    }

    __active_graphs : WeakKeyDictionary[Thread, dict[int, bool]] = WeakKeyDictionary()
    __graphs : WeakValueDictionary[int, "Graph"] = WeakValueDictionary()

    def __init__(self, vertices_or_edges : Iterable[Vertex | Edge] = ()) -> None:
        Graph.__graphs[id(self)] = self
        self.vertices : Graph.__IsoSet[Vertex] = Graph.__IsoSet()
        self.edges : Graph.__IsoSet[Edge] = Graph.__IsoSet()
        self.data : "dict[str, Any]" = {}
        self.__to_append : "list[Edge | Vertex]" = []
        if not isinstance(vertices_or_edges, Graph.__Iterable):
            raise TypeError(f"Expected iterable, got '{type(vertices_or_edges).__name__}'")
        if not isinstance(vertices_or_edges, Graph.__Iterable):
            raise TypeError("Expected iterable, got " + repr(vertices_or_edges.__class__.__name__))
        for value in vertices_or_edges:
            if isinstance(value, Vertex):
                self.vertices.add(value)
            elif isinstance(value, Edge):
                value.write()
                self.edges.add(value)
            else:
                raise TypeError("Expected edge or vertex, got " + repr(value.__class__.__name__))
            
    def __copy__(self) -> Self:
        """
        Implements copy(self).
        """
        cp = type(self).__new__(type(self))
        cp.edges = Graph.__IsoSet()
        cp.data = Graph.__copy(self.data)
        translation_table : "Graph.__IsoDict[Vertex, Vertex]" = Graph.__IsoDict((u, Graph.__copy(u)) for u in self.vertices)
        cp.vertices = Graph.__IsoSet(translation_table.values())
        for e in self.edges:
            e_cp = Graph.__copy(e)
            e_cp.source, e_cp.destination = translation_table[e.source], translation_table[e.destination]
            cp.edges.add(e_cp)
        return cp
            
    def __deepcopy__(self) -> Self:
        """
        Implements deepcopy(self).
        """
        cp = type(self).__new__(type(self))
        cp.edges = Graph.__IsoSet()
        cp.data = Graph.__deepcopy(self.data)
        translation_table : "Graph.__IsoDict[Vertex, Vertex]" = Graph.__IsoDict((u, Graph.__deepcopy(u)) for u in self.vertices)
        cp.vertices = Graph.__IsoSet(translation_table.values())
        for e in self.edges:
            e_cp = Graph.__deepcopy(e)
            e_cp.source, e_cp.destination = translation_table[e.source], translation_table[e.destination]
            cp.edges.add(e_cp)
        return cp

    def __bool__(self) -> bool:
        """
        Implements bool(self).
        """
        return len(self.vertices) > 0

    def __eq__(self, other : object) -> bool:
        """
        Implements self == other.
        """
        if not isinstance(other, Graph):
            return NotImplemented
        if self.vertices.iso_view != other.vertices.iso_view:
            return False
        
        comp = self.edges.iso_view @ other.edges.iso_view
        if not comp.source_complete or not comp.destination_complete:
            return False
        if not self:
            return True
        
        for mapping in comp:
            v_mapping : "Graph.__IsoDict[Vertex, Vertex]" = Graph.__IsoDict()
            for e, f in mapping.items():
                e_s, f_s, e_d, f_d = e.source, f.source, e.destination, f.destination
                if not isinstance(e, Arrow) or not isinstance(f, Arrow):
                    if e_s != f_s:
                        e_s, e_d = e_d, e_s
                if v_mapping.setdefault(e_s, f_s) is not f_s:
                    break
                if v_mapping.setdefault(e_d, f_d) is not f_d:
                    break
            else:
                return True

        return False

    def __ge__(self, other : "Graph") -> bool:
        """
        Implements self >= other.
        """
        if not isinstance(other, Graph):
            return NotImplemented
        return other <= self
    
    def __gt__(self, other : "Graph") -> bool:
        """
        Implements self > other.
        """
        if not isinstance(other, Graph):
            return NotImplemented
        return other < self
    
    def __le__(self, other : "Graph") -> bool:
        """
        Implements self <= other.
        """
        if not isinstance(other, Graph):
            return NotImplemented
        if not self.vertices.iso_view <= other.vertices.iso_view:
            return False
        
        comp = self.edges.iso_view @ other.edges.iso_view
        if not comp.source_complete:
            return False
        if not self:
            return True
        
        for mapping in comp:
            v_mapping : "Graph.__IsoDict[Vertex, Vertex]" = Graph.__IsoDict()
            for e, f in mapping.items():
                e_s, f_s, e_d, f_d = e.source, f.source, e.destination, f.destination
                if not isinstance(e, Arrow) or not isinstance(f, Arrow):
                    if e_s != f_s:
                        e_s, e_d = e_d, e_s
                if v_mapping.setdefault(e_s, f_s) is not f_s:
                    break
                if v_mapping.setdefault(e_d, f_d) is not f_d:
                    break
            else:
                return True

        return False
    
    def __lt__(self, other : "Graph") -> bool:
        """
        Implements self < other.
        """
        if not isinstance(other, Graph):
            return NotImplemented
        v_comp = self.vertices.iso_view @ other.vertices.iso_view
        if not v_comp.source_complete:
            return False
        
        comp = self.edges.iso_view @ other.edges.iso_view
        if not comp.source_complete or v_comp.destination_complete:
            return False
        if not self:
            return True
        
        for mapping in comp:
            v_mapping : "Graph.__IsoDict[Vertex, Vertex]" = Graph.__IsoDict()
            for e, f in mapping.items():
                e_s, f_s, e_d, f_d = e.source, f.source, e.destination, f.destination
                if not isinstance(e, Arrow) or not isinstance(f, Arrow):
                    if e_s != f_s:
                        e_s, e_d = e_d, e_s
                if v_mapping.setdefault(e_s, f_s) is not f_s:
                    break
                if v_mapping.setdefault(e_d, f_d) is not f_d:
                    break
            else:
                return True

        return False
    
    def __and__(self, other : "Graph") -> "Graph":
        """
        Implements self & other.
        Returns the first of the biggest common subgraphs common to the two graphs (found by intersect).
        Returns an empty Graph on empty intersection.
        """
        if not isinstance(other, Graph):
            return NotImplemented
        
        for g in self.intersection(other):
            return g
        return Graph()
    
    def __rand__(self, other : "Graph") -> "Graph":
        """
        Implements other & self.
        """
        return self & other
        
    def __or__(self, other : "Graph") -> "Graph":
        """
        Implements self | other.
        Returns the first union of two graphs by combining them from the biggest common subgraph (found by union).
        If they have no intersections, the result will be the "concatenation" of the two graphs, with no links between them.
        """
        if not isinstance(other, Graph):
            return NotImplemented
        
        for g in self.union(other):
            return g
        return Graph()
    
    def __ror__(self, other : "Graph") -> "Graph":
        """
        Implements other | self.
        """
        return self | other
    
    def __iter__(self) -> Iterator[Vertex | Edge]:
        """
        Iterates over the Graph vertices then edges.
        """
        yield from self.vertices
        yield from self.edges

    T = TypeVar("T", bound = Vertex | Edge)

    def __getitem__(self, cls : type[T]) -> IsoSet[T]:
        """
        Implements self[cls]. Returns an Isoset of vertices or edges of this Graph that are only of the given class(es).
        """
        return Graph.__IsoSet(v for v in self.vertices if isinstance(v, cls)) | Graph.__IsoSet(e for e in self.edges if isinstance(e, cls))
    
    del T

    def intersection(self, other : "Graph") -> Iterator["Graph"]:
        """
        Yields all the possible maximal subgraphs that are common to the two graphs.
        If there is no intersection, just yields an empty Graph.
        """
        if not isinstance(other, Graph):
            raise TypeError(f"Expected Graph, got '{type(other).__name__}'")

        n = 0
        for mapping in self.edges @ other.edges:

            v_mapping : "Graph.__IsoDict[Vertex, Vertex]" = Graph.__IsoDict()
            for e, f in mapping.items():
                e_s, f_s, e_d, f_d = e.source, f.source, e.destination, f.destination
                if not isinstance(e, Arrow) or not isinstance(f, Arrow):
                    if e_s != f_s:
                        e_s, e_d = e_d, e_s
                if v_mapping.setdefault(e_s, f_s) is not f_s:
                    break
                if v_mapping.setdefault(e_d, f_d) is not f_d:
                    break
            else:
                continue
            del v_mapping
            
            source_vertices : "Graph.__IsoSet[Vertex]" = Graph.__IsoSet()
            destination_vertices : "Graph.__IsoSet[Vertex]" = Graph.__IsoSet()
            translation_table : "Graph.__IsoDict[Vertex, Vertex]" = Graph.__IsoDict()
            subgraph = Graph()
            for e_s, e_d in mapping.items():
                u_s, v_s, u_d, v_d = e_s.source, e_s.destination, e_d.source, e_d.destination
                e_s_cp = Graph.__deepcopy(e_s)
                e_s_cp.source, e_s_cp.destination = translation_table.setdefault(u_s, e_s_cp.source), translation_table.setdefault(v_s, e_s_cp.destination)
                e_s_cp.write()
                subgraph.extend((translation_table[u_s], translation_table[v_s], e_s_cp))
                source_vertices.update((u_s, v_s))
                destination_vertices.update((u_d, v_d))
            
            remaining_maps = (self.vertices - source_vertices) @ (other.vertices - destination_vertices)
            if remaining_maps:
                for sub_map in remaining_maps:
                    subgraph_i = Graph.__deepcopy(subgraph)
                    for u_s, u_d in sub_map.items():
                        subgraph_i.append(Graph.__deepcopy(u_s))
                    n += 1
                    yield subgraph_i
            
            else:
                n += 1
                yield subgraph
        
        if not n:
            yield Graph()
    
    def union(self, other : "Graph") -> Iterator["Graph"]:
        """
        Yields all the possible merging of the two graphs obtained by combining the maximal common subgraphs.
        """
        if not isinstance(other, Graph):
            raise TypeError(f"Expected Graph, got '{type(other).__name__}'")
        
        
        def complete_graph(inter : Graph, source : Graph, destination : Graph, vertex_mapping : "Graph.__IsoDict[Vertex, Vertex]", edge_mapping : "Graph.__IsoDict[Edge, Edge]") -> Graph:
            """
            Transforms a triple (G1 & G2, G1, G2) into G1 | G2 given the sets of used vertices and edges in both G1 and G2 used to make G1 & G2.
            """
            for u in filter(lambda u : u not in vertex_mapping, source.vertices):
                u_cp = Graph.__deepcopy(u)
                vertex_mapping[u] = u_cp
                inter.append(u_cp)
            for u in filter(lambda u : u not in vertex_mapping, destination.vertices):
                u_cp = Graph.__deepcopy(u)
                vertex_mapping[u] = u_cp
                inter.append(u_cp)
            for e in filter(lambda e : e not in edge_mapping, source.edges):
                e_cp = Graph.__deepcopy(e)
                e_cp.source = vertex_mapping[e.source]
                e_cp.destination = vertex_mapping[e.destination]
                inter.append(e_cp)
            for e in filter(lambda e : e not in edge_mapping, destination.edges):
                e_cp = Graph.__deepcopy(e)
                e_cp.source = vertex_mapping[e.source]
                e_cp.destination = vertex_mapping[e.destination]
                inter.append(e_cp)
            return inter


        n = 0
        for mapping in self.edges @ other.edges:

            v_mapping : "Graph.__IsoDict[Vertex, Vertex]" = Graph.__IsoDict()
            for e, f in mapping.items():
                e_s, f_s, e_d, f_d = e.source, f.source, e.destination, f.destination
                if not isinstance(e, Arrow) or not isinstance(f, Arrow):
                    if e_s != f_s:
                        e_s, e_d = e_d, e_s
                if v_mapping.setdefault(e_s, f_s) is not f_s:
                    break
                if v_mapping.setdefault(e_d, f_d) is not f_d:
                    break
            else:
                continue
            
            vertex_translation_table : "Graph.__IsoDict[Vertex, Vertex]" = Graph.__IsoDict()
            edge_translation_table : "Graph.__IsoDict[Edge, Edge]" = Graph.__IsoDict()
            subgraph = Graph()
            for e_s, e_d in mapping.items():
                u_s, v_s, u_d, v_d = e_s.source, e_s.destination, e_d.source, e_d.destination
                if u_s != u_d:
                    u_d, v_d = v_d, u_d
                e_s_cp = Graph.__deepcopy(e_s)
                e_s_cp.source, e_s_cp.destination = vertex_translation_table.setdefault(u_s, e_s_cp.source), vertex_translation_table.setdefault(v_s, e_s_cp.destination)
                vertex_translation_table[u_d] = vertex_translation_table[u_s]
                vertex_translation_table[v_d] = vertex_translation_table[v_s]
                e_s_cp.write()
                subgraph.extend((vertex_translation_table[u_s], vertex_translation_table[v_s], e_s_cp))
                edge_translation_table[e_s] = e_s_cp
                edge_translation_table[e_d] = edge_translation_table[e_s]
            
            used_destination_vertices = IsoSet(vertex_translation_table)
            remaining_vertex_maps = (self.vertices - used_destination_vertices) @ (other.vertices - used_destination_vertices)
            del used_destination_vertices
            if remaining_vertex_maps:
                for sub_map_i in remaining_vertex_maps:
                    vertex_translation_table_i = vertex_translation_table.copy()
                    subgraph_i = Graph.__deepcopy(subgraph)
                    for u_s, u_d in sub_map_i.items():
                        u_s_cp = Graph.__deepcopy(u_s)
                        subgraph_i.append(u_s_cp)
                        vertex_translation_table_i[u_s] = u_s_cp
                        vertex_translation_table_i[u_d] = u_s_cp
                    n += 1
                    yield complete_graph(subgraph_i, self, other, vertex_translation_table_i, edge_translation_table)
            
            else:
                n += 1
                yield complete_graph(subgraph, self, other, vertex_translation_table, edge_translation_table)
        
        if not n:
            yield complete_graph(Graph(), self, other, Graph.__IsoDict(), Graph.__IsoDict())

    def __enter__(self):
        """
        Implements with self.
        """
        Graph.__active_graphs.setdefault(Graph.__current_thread(), {})[id(self)] = True

    def _register(self, vertex_or_edge : Vertex | Edge):
        """
        Internal function that registers a Vertex or an Edge to be added to the Graph at context exit.
        """
        self.__to_append.append(vertex_or_edge)
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        Implements with self.
        """
        Graph.__active_graphs[Graph.__current_thread()].pop(id(self))
        to_append, self.__to_append = self.__to_append, []
        self.extend(to_append)
    
    @staticmethod
    def active_graphs() -> list["Graph"]:
        """
        Returns the list of all the active Graphs in the current thread.
        """
        if Graph.__current_thread() not in Graph.__active_graphs:
            return []
        return [Graph.__graphs[i] for i, inserting in Graph.__active_graphs[Graph.__current_thread()].items() if inserting]
    
    @staticmethod
    def graphs_status() -> list[tuple["Graph", bool]]:
        """
        More advanced version of active_graphs. Returns a dictionary of Graphs that indicates if they are in auto_write mode.
        """
        if Graph.__current_thread() not in Graph.__active_graphs:
            return []
        return [(Graph.__graphs[i], inserting) for i, inserting in Graph.__active_graphs[Graph.__current_thread()].items()]

    def explore(self, source : Optional[Vertex] = None) -> None:
        """
        Explores the graph for more linked vertices. If a vertex of the graph is given, only searches starting from that vertex. Otherwise, searches from all vertices.
        """
        if source == None:
            to_explore = self.vertices.copy()
        else:
            if not isinstance(source, Vertex):
                raise TypeError("Expected vertex, got " + repr(source.__class__.__name__))
            if source not in self.vertices:
                raise KeyError("Vertex not in graph.")
            to_explore = {source}
        seen_vertices = set()
        seen_edges = set()
        while to_explore:
            u = to_explore.pop()
            seen_vertices.add(u)
            seen_edges.update(u.edges)
            new = set()
            for v in u.neighbors():
                if v not in seen_vertices:
                    new.add(v)
            to_explore.update(new)
        self.vertices.update(seen_vertices)
        self.edges.update(seen_edges)

    def pairs(self) -> Iterator[tuple[Vertex, Edge, Vertex]]:
        """
        Yields all (vertex u, edge e, vertex v) tuples where (u, v) is a pair of linked vertices. e may be an edge or an arrow directed from u to v.
        """
        for e in self.edges:
            yield e.source, e, e.destination

    def __len__(self) -> int:
        """
        Implements len(self). Returns the number of vertices.
        """
        return len(self.vertices)
    
    def __contains__(self, vertex_or_edge : Vertex | Edge) -> bool:
        """
        Implements vertex_or_edge in self. Returns True if the given Vertex or Edge is in the Graph.
        """
        if isinstance(vertex_or_edge, Vertex):
            return vertex_or_edge in self.vertices
        elif isinstance(vertex_or_edge, Edge):
            return vertex_or_edge in self.edges
        else:
            raise TypeError(f"Expected Vertex or Edge, got '{type(vertex_or_edge).__name__}'")
    
    @property
    def n(self) -> int:
        """
        The number of vertices.
        """
        return len(self)
    
    @property
    def m(self) -> int:
        """
        The number of edges and arrows.
        """
        return len(self.edges)
        
    def append(self, value : Vertex | Edge, explore : bool = False):
        """
        Adds a vertex or an edge to the graph.
        If explore is True, explores the graph from the added vertex or the source vertex of the added edge.
        """
        if not isinstance(explore, bool):
            raise TypeError("Expected bool for explore, got " + repr(explore.__class__.__name__))
        if isinstance(value, Vertex):
            self.vertices.add(value)
            if explore:
                self.explore(value)
        elif isinstance(value, Edge):
            value.write()
            self.edges.add(value)
            if explore:
                self.explore(value.source)
        else:
            raise TypeError("Expected edge or vertex, got " + repr(value.__class__.__name__))
    
    def remove(self, value : Vertex | Edge):
        """
        Removes a vertex or an edge from the graph.
        When removing a vertex, it will also remove all edges/arrows connected to it.
        """
        if isinstance(value, Vertex):
            self.edges.difference_update(value.edges)
            for e in value.edges.copy(): 
                e.source.edges.discard(e)
                e.destination.edges.discard(e)
            self.vertices.discard(value)
        elif isinstance(value, Edge):
            self.edges.discard(value)
            value.source.edges.discard(value)
            value.destination.edges.discard(value)
        else:
            raise TypeError("Expected edge or vertex, got " + repr(type(value).__name__))

    def extend(self, values : Iterable[Vertex | Edge], explore : bool = False):
        """
        Extends the graph with an iterable of vertices and/or edges.
        """
        from typing import Iterable
        if not isinstance(explore, bool):
            raise TypeError("Expected bool for explore, got " + repr(explore.__class__.__name__))
        if not isinstance(values, Iterable):
            raise TypeError("Expected iterable, got " + repr(values.__class__.__name__))
        for value in values:
            if isinstance(value, Vertex):
                self.vertices.add(value)
                if explore:
                    self.explore(value)
            elif isinstance(value, Edge):
                value.write()
                self.edges.add(value)
                if explore:
                    self.explore(value.source)
            else:
                raise TypeError("Expected edge or vertex, got " + repr(value.__class__.__name__))
        
    def paint(self, c : Color):
        """
        Changes the colors of all vertices and edges/arrows of this graph to the given Color.
        """
        from .colors import Color
        if not isinstance(c, Color):
            raise TypeError("Expected Color, got " + repr(type(c).__name__))
        for u in self.vertices:
            u.color = c
        for e in self.edges:
            e.color = c

    def __getstate__(self) -> _GraphStateDict:
        """
        Implements dumping of self.
        """
        return {
            "vertices" : self.vertices,
            "edges" : self.edges, 
            "data" : self.data
        }

    def __setstate__(self, state : _GraphStateDict):
        """
        Implements loading of self. Note that subclass attributes must be handled by the user.
        """
        thread_dict = Graph.__active_graphs.get(Graph.__current_thread(), default={})
        thread_dict[id(self)] = False       # This is a weak graph activation. It does not trigger auto_insertion.
        Graph.__graphs[id(self)] = self
        try:
            for name in ("vertices", "edges", "data"):
                setattr(self, name, state[name])
            if isinstance(self.vertices, set):       # For compatibility issues (before IsoSets)
                self.vertices = Graph.__IsoSet(self.vertices)
            if isinstance(self.edges, set):
                self.edges = Graph.__IsoSet(self.edges)
            for e in self.edges:
                e.write()
        finally:
            thread_dict.pop(id(self))
   
    # def __copy__(self) -> "graph":
    #     """
    #     Implements copy of self
    #     """
    #     from copy import copy
    #     translation = {u : copy(u) for u in self.vertices}
    #     cp = graph()
    #     cp.vertices.update(translation.values())
    #     for u, e, v in self.pairs():
    #         e = copy(e)
    #         e.source = translation[u]
    #         e.destination = translation[v]
    #         e.write()
    #     return cp
    
    # def __deepcopy__(self, memo : Dict[int, Any]) -> "graph":
    #     """
    #     Implements deepcopy of self
    #     """
    #     from copy import deepcopy
    #     translation = {u : deepcopy(u, memo) for u in self.vertices}
    #     cp = graph()
    #     cp.vertices.update(translation.values())
    #     for u, e, v in self.pairs():
    #         e = deepcopy(e, memo)
    #         e.source = translation[u]
    #         e.destination = translation[v]
    #         e.write()
    #     return cp

    def export(self, file : str, *, subgraph_supported : bool = False) -> None:
        """
        Writes this graph under the GEXF format into given file.
        """
        # List of possible attributes to include in visuals :
        # Node Size : proportional to radius! not surface area!
        # Color : R, G, B
        # Node Shape : Any of "disc", "square", "triangle" or "diamond"
        # Edge Thickness : same as weight?
        # Edge Shape : Any of "solid", "dotted", "dashed" or "double"
        from datetime import date
        import json

        forbidden_characters : dict[int, str] = {i : "�" for i in range(32) if chr(i) not in {"\n", "\t", "\r"}}

        if not isinstance(subgraph_supported, bool):
            raise TypeError("Expected bool for subgraph_supported, got " + repr(subgraph_supported.__class__.__name__))
        try:
            with open(file, "wb") as f:
                import xml.etree.ElementTree as ET
                head = b'<?xml version="1.0" encoding="UTF-8"?>'
                root = ET.Element("gexf", attrib={"xmlns":"http://www.gexf.net/1.3", "version":"1.3", "xmlns:viz":"http://www.gexf.net/1.3/viz", "xmlns:xsi":"http://www.w3.org/2001/XMLSchema-instance", "xsi:schemaLocation":"http://www.gexf.net/1.3 http://www.gexf.net/1.3/gexf.xsd"})
                meta = ET.SubElement(root, "meta", lastmodifieddate=date.today().isoformat())
                creator = ET.SubElement(meta, "creator")
                creator.text = "Graph Builder"
                description = ET.SubElement(meta, "description")
                description.text = ""
                graph = ET.SubElement(root, "graph", mode="static")
                node_attr = ET.SubElement(graph, "attributes", **{"class" : "node", "mode" : "static"})
                node_attributes = {}
                edge_attr = ET.SubElement(graph, "attributes", **{"class" : "edge", "mode" : "static"})
                edge_attributes = {}
                nodes = ET.SubElement(graph, "nodes")
                edges = ET.SubElement(graph, "edges")
                n_ids = Graph.__IsoDict((u, i) for i, u in enumerate(self.vertices))
                additional_links : set[tuple[Vertex, Vertex]] = set()
                for u, i in n_ids.items():
                    d = {}
                    if isinstance(u, DataVertex):
                        d |= {name : str(getattr(u, name)).translate(forbidden_characters) for name in u.__defining_data__ | u.__additional_data__ | u.__computable_properties__}
                    d["Type"] = type(u).__name__
                    if "__weakref__" in d:
                        d = {}
                    node_i = ET.SubElement(nodes, "node", id=str(i), label=u.label.translate(forbidden_characters))
                    attr_i = ET.SubElement(node_i, "attvalues")
                    for name, value in d.items():
                        if name not in node_attributes:
                            node_attributes[name] = ET.SubElement(node_attr, "attribute", id=name, title=name, type="string")
                        if isinstance(value, (dict, list)):
                            try:
                                svalue = json.dumps(value, indent = "\t")
                            except:
                                svalue = str(value)
                        else:
                            svalue = str(value)
                        ET.SubElement(attr_i, "attvalue", **{"for" : name, "value" : svalue.translate(forbidden_characters)})
                    size = ET.SubElement(node_i, "viz:size", value=str(u.size))
                    color = ET.SubElement(node_i, "viz:color", r=str(int(u.color.R * 255)), g=str(int(u.color.G * 255)), b=str(int(u.color.B * 255)))
                for u, e, v in self.pairs():
                    if u not in n_ids:
                        continue
                    if v not in n_ids:
                        continue
                    d = {}
                    if isinstance(e, DataEdge):
                        d |= {name : str(getattr(e, name)).translate(forbidden_characters) for name in e.__defining_data__ | e.__additional_data__ | e.__computable_properties__}
                    d["Type"] = type(e).__name__
                    if "__weakref__" in d:
                        d = {}
                    try:
                        edge_i = ET.SubElement(edges, "edge", source=str(n_ids[u]), target=str(n_ids[v]), type=("directed" if isinstance(e, Arrow) else "undirected"), label=e.label.translate(forbidden_characters), attrib=d, weight=str(e.weight))
                    except KeyError:
                        raise
                    color = ET.SubElement(edge_i, "viz:color", r=str(int(e.color.R * 255)), g=str(int(e.color.G * 255)), b=str(int(e.color.B * 255)))
                    attr_i = ET.SubElement(edge_i, "attvalues")
                    for name, value in d.items():
                        if name not in edge_attributes:
                            edge_attributes[name] = ET.SubElement(edge_attr, "attribute", id=name, title=name, type="string")
                        if isinstance(value, (dict, list)):
                            try:
                                svalue = json.dumps(value, indent = "\t")
                            except:
                                svalue = str(value)
                        else:
                            svalue = str(value)
                        ET.SubElement(attr_i, "attvalue", **{"for" : name, "value" : svalue.translate(forbidden_characters)})
                for u, v in additional_links:
                    edge_i = ET.SubElement(edges, "edge", source=str(n_ids[u]), target=str(n_ids[v]), type="directed", label="contains", weight="1.0")
                f.write(head + b"\n")
                ET.indent(root, "\t")
                for line in ET.tostringlist(root):
                    f.write(line + b"\n")
        except Exception as E:
            raise





class FrozenGraph(Graph):
    
    """
    Frozen (immutable) version of Graphs.
    """

    from Viper.collections import FrozenIsoSet as __FrozenIsoSet, IsoSet as __IsoSet

    def __init__(self, vertices_or_edges: Iterable[Vertex | Edge] = ()) -> None:
        super().__init__(vertices_or_edges)
        self.vertices : "FrozenGraph.__FrozenIsoSet[Vertex]" = FrozenGraph.__FrozenIsoSet(self.vertices)
        self.edges : "FrozenGraph.__FrozenIsoSet[Edge]" = FrozenGraph.__FrozenIsoSet(self.edges)
        
    def append(self, value: Vertex | Edge, explore: bool = False) -> Never:
        raise AttributeError(f"Cannot append to a '{type(self).__name__}'")
    
    def remove(self, value: Vertex | Edge) -> Never:
        raise AttributeError(f"Cannot remove from a '{type(self).__name__}'")
    
    def extend(self, values: Iterable[Vertex | Edge], explore: bool = False) -> Never:
        raise AttributeError(f"Cannot extend a '{type(self).__name__}'")
    
    def paint(self, c: Color) -> Never:
        raise AttributeError(f"Cannot paint to a '{type(self).__name__}'")
    
    def __hash__(self) -> int:
        return hash(hash(self.vertices) -  hash(self.edges))
    
    @overload
    def __or__(self, other: "FrozenGraph") -> "FrozenGraph":
        pass

    @overload
    def __or__(self, other : Graph) -> Graph:
        pass

    def __or__(self, other):
        if isinstance(other, FrozenGraph):
            return FrozenGraph(Graph.__or__(self, other))
        return Graph.__or__(self, other)
    
    @overload
    def __ror__(self, other: "FrozenGraph") -> "FrozenGraph":
        pass

    @overload
    def __ror__(self, other : Graph) -> Graph:
        pass

    def __ror__(self, other):
        if isinstance(other, FrozenGraph):
            return FrozenGraph(Graph.__ror__(other, self))
        return Graph.__ror__(other, self)
        
    @overload
    def __and__(self, other: "FrozenGraph") -> "FrozenGraph":
        pass

    @overload
    def __and__(self, other : Graph) -> Graph:
        pass

    def __and__(self, other):
        if isinstance(other, FrozenGraph):
            return FrozenGraph(Graph.__and__(self, other))
        return Graph.__and__(self, other)
    
    @overload
    def __rand__(self, other: "FrozenGraph") -> "FrozenGraph":
        pass

    @overload
    def __rand__(self, other : Graph) -> Graph:
        pass

    def __rand__(self, other):
        if isinstance(other, FrozenGraph):
            return FrozenGraph(Graph.__rand__(other, self))
        return Graph.__rand__(other, self)
    
    def __getstate__(self) -> _GraphStateDict:
        res = super().__getstate__()
        res["edges"] = FrozenGraph.__IsoSet(res["edges"])
        res["vertices"] = FrozenGraph.__IsoSet(res["vertices"])
        return res
    
    def __setstate__(self, state: _GraphStateDict):
        super().__setstate__(state)
        self.edges = FrozenGraph.__FrozenIsoSet(self.edges)
        self.vertices = FrozenGraph.__FrozenIsoSet(self.vertices)


    

del RLock, Thread, Any, Callable, Iterable, Iterator, Never, Optional, TypeVar, TypedDict, Union, WeakKeyDictionary, WeakValueDictionary, Color, ColorSetting, SizeSetting, SwitchSetting, WeightSetting, InstanceReferencingClass, IsoSet