"""
This module defines MetaGraphs, MetaVertices, MetaEdges and MetaArrows. They allow you to create graph patterns.
Look at these classes!
"""

from types import UnionType
from typing import Any, Iterable, Iterator, Literal, Never, Optional, TypeVar, overload
from Viper.collections.isomorph import IsoDict, IsoSet
from ...bakery.source.colors import Color
from ...bakery.source.graph import Arrow, Edge, FrozenGraph, Graph, Vertex, _GraphStateDict
from .evaluator import Evaluator

__all__ =   ["MetaVertex", "MetaEdge", "MetaArrow", "MetaGraph", "FrozenMetaGraph"]





class MetaVertex(Vertex):

    """
    This class describes a type vertex. One or multiple Vertex subclasses can be associated to it as well as additional conditions.
    This class defines properties cls and condition which can be efficiently affected with a special syntax:
    >>> MV = MetaVertex()
    >>> MV.cls = (File, )
    >>> MV.condition = Evaluator("lambda x : x.name.endswith('.exe')")

    is equivalent to:
    >>> MV = MetaVertex[File]("lambda x : x.name.endswith('.exe')")
    """

    @classmethod
    def __class_getitem__(cls, cls_init : type[Vertex] | tuple[type[Vertex], ...] | UnionType):
        try:
            Mv = cls()
            Mv.cls = cls_init
            return Mv
        except BaseException as E:
            raise E from None

    __slots__ = {
        "__class" : "The class that this MetaVertex represents.",
        "__condition" : "An additional condition function. Takes a Vertex as an input and tells whether or not it can be a valid match (does not need to check type)",
        "__color" : "The Color forcefully set to this MetaVertex.",
        "__hash" : "The computed hash."
    }

    def __init__(self, *, parent: Optional[Vertex] = None) -> None:
        from ...bakery.source.colors import Color
        from .evaluator import Evaluator
        self.__class : tuple[type[Vertex], ...] = (Vertex, )
        self.__condition : Evaluator[Vertex, bool] | None = None
        self.__color : Color | None = None
        self.__hash : int | None = None
        self.edges : "IsoSet[MetaEdge]"
        super().__init__()

    @property
    def color(self) -> Color:
        """
        The color of this MetaVertex. Defaults to the average of the colors of all its Vertex classes.
        """
        from ...bakery.source.colors import Color
        if self.__color is not None:
            return self.__color
        return Color.average(*[(cls.default_color) for cls in self.cls])
    
    @color.setter
    def color(self, c : Color):
        from ...bakery.source.colors import Color
        if not isinstance(c, Color):
            raise TypeError("Expected Color, got " + repr(type(c).__name__))
        self.__color = c

    @color.deleter
    def color(self):
        self.__color = None
    
    @property
    def cls(self) -> tuple[type[Vertex], ...]:
        """
        The classes that this vertex represents.
        """
        return self.__class
    
    @cls.setter
    def cls(self, cls : type[Vertex] | tuple[type[Vertex], ...] | UnionType):
        """
        Sets the class(es) associated with this vertex.
        """
        if self.__hash is not None:
            raise RuntimeError(f"__hash__ has been computed: you cannot edit this {type(self).__name__} without breaking container structures")
        from types import UnionType

        from ...bakery.source.graph import Vertex
        if isinstance(cls, UnionType):
            args : tuple[type[Vertex]] = cls.__args__ # type: ignore
            for c in args:
                if not isinstance(c, type) or not issubclass(c, Vertex):
                    raise TypeError("Expected subclass of Vertex or tuple of subclasses, got a " + repr(c))
            self.__class = args
        elif isinstance(cls, type) and issubclass(cls, Vertex):
            self.__class = (cls, )
        elif isinstance(cls, tuple):
            for c in cls:
                if not isinstance(c, type) or not issubclass(c, Vertex):
                    raise TypeError("Expected subclass of Vertex or tuple of subclasses, got a " + repr(c))
            self.__class = cls
        else:
            raise TypeError("Expected subclass of Vertex or tuple of subclasses, got " + repr(cls))
    
    @cls.deleter
    def cls(self):
        if self.__hash is not None:
            raise RuntimeError(f"__hash__ has been computed: you cannot edit this {type(self).__name__} without breaking container structures")
        from ...bakery.source.graph import Vertex
        self.__class = (Vertex, )

    @property
    def condition(self) -> Evaluator[Vertex, bool] | None:
        """
        An additional and optional condition to check when trying to match a Vertex to this MetaVertex.
        """
        return self.__condition
    
    @condition.setter
    def condition(self, cond : Evaluator[Vertex, bool] | str | None):
        """
        Sets the additional condition function for this MetaVertex.
        """
        if self.__hash is not None:
            raise RuntimeError(f"__hash__ has been computed: you cannot edit this {type(self).__name__} without breaking container structures")
        from .evaluator import Evaluator
        if isinstance(cond, str):
            try:
                cond = Evaluator(cond)
            except SyntaxError as e:
                raise e from None
        if not isinstance(cond, Evaluator | None):
            raise TypeError(f"Expected Evaluator, str or None, got '{type(cond).__name__}'")
        self.__condition = cond

    @condition.deleter
    def condition(self):
        if self.__hash is not None:
            raise RuntimeError(f"__hash__ has been computed: you cannot edit this {type(self).__name__} without breaking container structures")
        self.__condition = None
    
    def match(self, v : Vertex) -> bool:
        """
        Returns True if the Vertex v has a matching type.
        """
        return isinstance(v, self.__class) and (self.__condition(v) if self.__condition else True)
    
    def __contains__(self, v : Vertex) -> bool:
        """
        Implements v in self. Equivalent to self.match(v).
        """
        return self.match(v)
    
    def __get_cls_str(self) -> str:
        """
        Returns a string to display the class of a MetaVertex.
        """
        return " | ".join(c.__name__ for c in self.__class)
    
    def __call__(self, cond : Evaluator[Vertex, bool] | str):
        """
        Implements self(cond). Sets the condition and returns self.
        """
        try:
            self.condition = cond
            return self
        except BaseException as e:
            raise e from None
        
    def __getstate__(self):
        return super().__getstate__() | {
            "cls" : self.cls,
            "condition" : self.condition
        }
    
    def __setstate__(self, state : dict[str, Any]):
        self.__hash = None
        super().__setstate__(state)

    @property
    def label(self) -> str:
        return f"Vertex[{self.__get_cls_str()}]" + (f"({str(self.__condition)})" if self.__condition else "")

    def __str__(self) -> str:
        return f"{type(self).__name__}[{self.__get_cls_str()}]" + ("*" if self.__condition else "")
    
    def __repr__(self) -> str:
        return f"{type(self).__name__}[{self.__get_cls_str()}]" + (f"({repr(self.__condition.code)})" if self.__condition else "")
    
    def __eq__(self, other : Any) -> bool:
        """
        Implements self == other.
        """
        return isinstance(other, MetaVertex) and set(self.cls) == set(other.cls) and self.condition == other.condition
    
    def __hash__(self) -> int:
        """
        Implements hash(self).
        """
        if self.__hash is None:
            self.__hash = hash(hash(frozenset(self.cls)) * hash(self.condition))
        return self.__hash





class MetaEdge(Edge):

    """
    This class describes a type edge. One or multiple Edge subclasses can be associated to it.
    Note that a MetaEdge can represent a subclass of Arrow and in this case, the match can be made in both directions.
    Like MetaVertices, MetaEdges have special syntaxes for setting the cls and condition attributes:
    >>> U = MetaVertex[Directory]
    >>> V = MetaVertex[File]
    >>> UV = MetaEdge(U, V)
    >>> UV.cls = (Contains, )
    >>> UV.condition = Evaluator("lambda x : True")     # Dummy condition

    is equivalent to:
    >>> U = MetaVertex[Directory]
    >>> V = MetaVertex[File]
    >>> UV = MetaEdge(U, V)[contains]("lambda x : True")
    """

    __slots__ = {
        "__class" : "The class that this MetaEdge represents.",
        "__condition" : "An additional condition function. Takes an Edge as an input and tells whether or not it can be a valid match (does not need to check type)",
        "__color" : "The Color forcefully set to this MetaEdge.",
        "__hash" : "The computed hash."
    }

    def __init__(self, source: MetaVertex, destination: MetaVertex) -> None:
        from ...bakery.source.colors import Color
        from .evaluator import Evaluator
        if not isinstance(source, MetaVertex) or not isinstance(destination, MetaVertex):
            raise TypeError("Expected two MetaVertices, got " + repr(type(source).__name__) + " and " + repr(type(destination).__name__))
        self.__class : tuple[type[Edge], ...] = (Edge, )
        self.__condition : Evaluator[Edge, bool] | None = None
        self.__color : Color | None = None
        self.__hash : int | None = None
        self.source : MetaVertex
        self.destination : MetaVertex
        super().__init__(source, destination, auto_write=False)

    @property
    def color(self) -> Color:
        """
        The color of this MetaEdge. Defaults to the average of the colors of all its Edge classes.
        """
        from ...bakery.source.colors import Color
        if self.__color != None:
            return self.__color
        edge_colors = [cls.default_color for cls in self.cls if not cls.blend_vertices_colors]
        if edge_colors:
            return Color.average(*edge_colors)
        else:
            return Color.average(self.source.color, self.destination.color)
    
    @color.setter
    def color(self, c : Color):
        from ...bakery.source.colors import Color
        if not isinstance(c, Color):
            raise TypeError("Expected Color, got " + repr(type(c).__name__))
        self.__color = c

    @color.deleter
    def color(self):
        self.__color = None
    
    @property
    def cls(self) -> tuple[type[Edge], ...]:
        """
        The classes that this edge represents.
        """
        return self.__class
    
    @cls.setter
    def cls(self, cls : type[Edge] | tuple[type[Edge], ...] | UnionType):
        """
        Sets the class(es) associated with this edge.
        """
        if self.__hash is not None:
            raise RuntimeError(f"__hash__ has been computed: you cannot edit this {type(self).__name__} without breaking container structures")
        from types import UnionType

        from ...bakery.source.graph import Edge
        if isinstance(cls, UnionType):
            args : tuple[type[Edge]] = cls.__args__ # type: ignore
            for c in args:
                if not isinstance(c, type) or not issubclass(c, Edge):
                    raise TypeError("Expected subclass of Edge or tuple of subclasses, got a " + repr(c))
            self.__class = args
        elif isinstance(cls, type) and issubclass(cls, Edge):
            self.__class = (cls, )
        elif isinstance(cls, tuple):
            for c in cls:
                if not isinstance(c, type) or not issubclass(c, Edge):
                    raise TypeError("Expected subclasses of Edge or tuple of subclasses, got a " + repr(c))
            self.__class = cls
        else:
            raise TypeError("Expected subclass of Edge or tuple of subclasses, got " + repr(cls))
        
    @cls.deleter
    def cls(self):
        if self.__hash is not None:
            raise RuntimeError(f"__hash__ has been computed: you cannot edit this {type(self).__name__} without breaking container structures")
        from ...bakery.source.graph import Edge
        self.__class = (Edge, )
        
    @property
    def condition(self) -> Evaluator[Edge, bool] | None:
        """
        An additional condition to check when trying to match an Edge to this MetaEdge.
        """
        return self.__condition
    
    @condition.setter
    def condition(self, cond : Evaluator[Edge, bool] | str | None):
        """
        Sets the additional condition function for this MetaEdge.
        """
        if self.__hash is not None:
            raise RuntimeError(f"__hash__ has been computed: you cannot edit this {type(self).__name__} without breaking container structures")
        from .evaluator import Evaluator
        if isinstance(cond, str):
            try:
                cond = Evaluator(cond)
            except SyntaxError as e:
                raise e from None
        if not isinstance(cond, Evaluator | None):
            raise TypeError(f"Expected Evaluator, str or None, got '{type(cond).__name__}'")
        self.__condition = cond
    
    @condition.deleter
    def condition(self):
        if self.__hash is not None:
            raise RuntimeError(f"__hash__ has been computed: you cannot edit this {type(self).__name__} without breaking container structures")
        self.__condition = None
    
    def match(self, e : Edge) -> bool:
        """
        Returns True if the Egde e has a matching type.
        """
        return isinstance(e, self.__class) and (self.__condition(e) if self.__condition else True)
    
    def __contains__(self, e : Edge) -> bool:
        """
        Implements e in self. Equivalent to self.match(e).
        """
        return self.match(e)
    
    def __get_cls_str(self) -> str:
        """
        Returns a string to display the class of a MetaEdge.
        """
        return " | ".join(c.__name__ for c in self.cls)
    
    def __getstate__(self):
        return super().__getstate__() | {
            "cls" : self.cls,
            "condition" : self.condition
        }
    
    def __setstate__(self, state : dict[str, Any]):
        self.__hash = None
        super().__setstate__(state)

    @property
    def label(self) -> str:
        return f"Edge[{self.__get_cls_str()}]" + (f"({repr(self.__condition.code)})" if self.__condition else "")

    def __str__(self) -> str:
        return f"{type(self).__name__}[{self.__get_cls_str()}]" + ("*" if self.__condition else "")
    
    def __repr__(self) -> str:
        return f"{type(self).__name__}[{self.__get_cls_str()}]" + (f"({repr(self.__condition.code)})" if self.__condition else "")

    def __getitem__(self, cls : type[Edge] | tuple[type[Edge], ...] | UnionType):
        try:
            self.cls = cls
            return self
        except BaseException as E:
            raise E from None
        
    def __call__(self, cond : Evaluator[Edge, bool] | str):
        try:
            self.condition = cond
            return self
        except BaseException as e:
            raise e from None
    
    def __eq__(self, other : Any) -> bool:
        """
        Implements self == other.
        """
        return isinstance(other, MetaEdge) and set((self.source, self.destination)) == set((other.source, other.destination)) and set(self.cls) == set(other.cls) and self.condition == other.condition
    
    def __hash__(self) -> int:
        """
        Implements hash(self).
        """
        if self.__hash is None:
            self.__hash = hash(hash(frozenset(self.cls)) * hash(self.condition) * (hash(self.source) + hash(self.destination)))
        return self.__hash





class MetaArrow(Arrow, MetaEdge):

    """
    This class describes a type arrow. One or multiple Arrow subclasses can be associated to it.
    It has the same syntax rules as MetaEdges.
    """

    __slots__ = {
        "__class" : "The class that this MetaArrow represents.",
        "__condition" : "An additional condition function. Takes an Arrow as an input and tells whether or not it can be a valid match (does not need to check type)",
        "__hash" : "The computed hash."
    }

    def __init__(self, source: MetaVertex, destination: MetaVertex) -> None:
        from ...bakery.source.graph import Arrow
        from .evaluator import Evaluator
        self.__class : tuple[type[Arrow], ...] = (Arrow, )
        self.__condition : Evaluator[Arrow, bool] | None = None
        self.__hash : int | None = None
        super().__init__(source, destination)

    @property
    def cls(self) -> tuple[type[Arrow], ...]:
        """
        The classes that this arrow represents.
        """
        return self.__class
    
    @cls.setter
    def cls(self, cls : type[Arrow] | tuple[type[Arrow], ...] | UnionType):
        """
        Sets the class(es) associated with this arrow.
        """
        if self.__hash is not None:
            raise RuntimeError(f"__hash__ has been computed: you cannot edit this {type(self).__name__} without breaking container structures")
        from types import UnionType

        from ...bakery.source.graph import Arrow
        if isinstance(cls, UnionType):
            args : tuple[type[Arrow]] = cls.__args__ # type: ignore
            for c in args:
                if not isinstance(c, type) or not issubclass(c, Arrow):
                    raise TypeError("Expected subclass of Arrow or tuple of subclasses, got a " + repr(c))
            self.__class = args
        elif isinstance(cls, type) and issubclass(cls, Arrow):
            self.__class = (cls, )
        elif isinstance(cls, tuple):
            for c in cls:
                if not isinstance(c, type) or not issubclass(c, Arrow):
                    raise TypeError("Expected subclasses of Arrow or tuple of subclasses, got a " + repr(c))
            self.__class = cls
        else:
            raise TypeError("Expected subclass of Arrow or tuple of subclasses, got " + repr(cls))
        
    @cls.deleter
    def cls(self):
        if self.__hash is not None:
            raise RuntimeError(f"__hash__ has been computed: you cannot edit this {type(self).__name__} without breaking container structures")
        from ...bakery.source.graph import Arrow
        self.__class = (Arrow, )
        
    @property
    def condition(self) -> Evaluator[Arrow, bool] | None:
        """
        An additional condition to check when trying to match an Arrow to this MetaArrow.
        """
        return self.__condition
    
    @condition.setter
    def condition(self, cond : Evaluator[Arrow, bool] | str | None):
        """
        Sets the additional condition function for this MetaArrow.
        """
        if self.__hash is not None:
            raise RuntimeError(f"__hash__ has been computed: you cannot edit this {type(self).__name__} without breaking container structures")
        from .evaluator import Evaluator
        if isinstance(cond, str):
            try:
                cond = Evaluator(cond)
            except SyntaxError as e:
                raise e from None
        if not isinstance(cond, Evaluator | None):
            raise TypeError(f"Expected Evaluator, str or None, got '{type(cond).__name__}'")
        self.__condition = cond
    
    @condition.deleter
    def condition(self):
        if self.__hash is not None:
            raise RuntimeError(f"__hash__ has been computed: you cannot edit this {type(self).__name__} without breaking container structures")
        self.__condition = None
    
    def __setstate__(self, state : dict[str, Any]):
        self.__hash = None
        super().__setstate__(state)
    
    @overload
    def match(self, a : Edge) -> Literal[False]:
        ...

    @overload
    def match(self, a : Arrow) -> bool:
        ...

    def match(self, a):
        """
        Returns True if the Arrow a has a matching type.
        """
        return isinstance(a, self.__class) and (self.__condition(a) if self.__condition else True)

    def __get_cls_str(self) -> str:
        """
        Returns a string to display the class of a MetaArrow.
        """
        return " | ".join(c.__name__ for c in self.cls)

    @property
    def label(self) -> str:
        return f"Arrow[{self.__get_cls_str()}]" + (f"({repr(self.__condition.code)})" if self.__condition else "")
    
    def __str__(self) -> str:
        return f"{type(self).__name__}[{self.__get_cls_str()}]" + ("*" if self.__condition else "")
    
    def __repr__(self) -> str:
        return f"{type(self).__name__}[{self.__get_cls_str()}]" + (f"({repr(self.__condition.code)})" if self.__condition else "")
    
    def __getitem__(self, cls : type[Arrow] | tuple[type[Arrow], ...] | UnionType):
        return super().__getitem__(cls)
    
    def __call__(self, cond: Evaluator[Arrow, bool] | str):
        try:
            self.condition = cond
            return self
        except BaseException as e:
            raise e from None
        
    def __eq__(self, other : Any) -> bool:
        """
        Implements self == other.
        """
        return isinstance(other, MetaArrow) and (self.source, self.destination) == (other.source, other.destination) and set(self.cls) == set(other.cls) and self.condition == other.condition
    
    def __hash__(self) -> int:
        """
        Implements hash(self).
        """
        if self.__hash is None:
            self.__hash = hash(hash(frozenset(self.cls)) * hash(self.condition) * (hash(self.destination) - hash(self.source)))
        return self.__hash

    



class _MetaGraphStateDict(_GraphStateDict):

    named_objects : dict[str, MetaEdge | MetaVertex]

class MetaGraph(Graph):

    """
    This particular type of graph can only contain MetaVertices, MetaEdges or MetaArrows. It can be used for normal graph exploration.

    Note that contrary to normal Graphs, MetaGraphs can hold named vertices and edges:
    >>> MG = MetaGraph()
    >>> MG.File = MetaVertex[File]
    >>> len(MG.vertices)
    1
    >>> MG.File
    MetaVertex[File]

    MetaGraphs can also be created by giving a Graph or an iterable of Vertices and Edges to the constructor, in which case, it will make a MetaGraph that matches the structure of the given Graph.
    It can also receive a MetaGraph or an iterable of MetaVertices and MetaEdges, to perform a MetaGraph copy.
    """

    from itertools import chain as __chain
    from Viper.collections import IsoSet as __IsoSet, IsoDict as __IsoDict
    from ...bakery.source.graph import Graph as __Graph

    __slots__ = {
        "__named_objects" : "A dict holding named vertices and edges."
    }

    vertices : __IsoSet[MetaVertex]
    edges : __IsoSet[MetaEdge]

    def __init__(self, g : Iterable[Vertex | Edge] | Graph = Graph()) -> None:
        if isinstance(g, Graph):
            g = MetaGraph.__chain(g.vertices, g.edges)
        MetaGraph.__Graph.__init__(self)
        self.__named_objects : "dict[str, MetaEdge | MetaVertex]" = {}
        vertices : "MetaGraph.__IsoSet[Vertex]" = MetaGraph.__IsoSet()
        edges : "MetaGraph.__IsoSet[Edge]" = MetaGraph.__IsoSet()
        all_meta = True
        for k in g:
            if isinstance(k, Vertex):
                vertices.add(k)
                if not isinstance(k, MetaVertex):
                    all_meta = False
            elif isinstance(k, Edge):
                edges.add(k)
                if not isinstance(k, MetaEdge):
                    all_meta = False
            else:
                raise TypeError(f"Expected iterable of Vertices and Edges, got a '{type(k).__name__}'")
            
        if all_meta:
            for value in MetaGraph.__chain(vertices, edges):
                if isinstance(value, MetaVertex):
                    self.vertices.add(value)
                elif isinstance(value, MetaEdge):
                    value.write()
                    self.edges.add(value)
        else:

            vertex_translation_table : dict[int, MetaVertex] = {}

            for v in vertices:
                Mv = MetaVertex()
                Mv.cls = type(v)
                vertex_translation_table[id(v)] = Mv
                self.append(Mv)
            
            for e in edges:
                u, v = e.source, e.destination

                if id(u) not in vertex_translation_table:
                    Mu = MetaVertex()
                    Mu.cls = type(u)
                    vertex_translation_table[id(u)] = Mu
                    self.append(Mu)
                
                if id(v) not in vertex_translation_table:
                    Mv = MetaVertex()
                    Mv.cls = type(v)
                    vertex_translation_table[id(v)] = Mv
                    self.append(Mv)
                
                if isinstance(e, Arrow):
                    Me = MetaArrow(vertex_translation_table[id(u)], vertex_translation_table[id(v)])
                    Me.cls = type(e)
                    self.append(Me)
                
                else:
                    Me = MetaEdge(vertex_translation_table[id(u)], vertex_translation_table[id(v)])
                    Me.cls = type(e)
                    self.append(Me)
    
    @property
    def names(self) -> list[str]:
        """
        Returns the list of names for named Meta{Vertices, Edges, Arrows} available in this MetaGraph.
        """
        return list(self.__named_objects)

    def pairs(self) -> Iterator[tuple[MetaVertex, MetaEdge, MetaVertex]]:
        for u, e, v in super().pairs():
            if not isinstance(u, MetaVertex) or not isinstance(e, MetaEdge) or not isinstance(v, MetaVertex):
                raise TypeError("Got a normal Vertex/Edge in a MetaGraph")
            yield u, e, v
    
    def append(self, value: MetaVertex | MetaEdge, explore: bool = False):
        if not isinstance(value, MetaVertex | MetaEdge | MetaArrow):
            raise TypeError("Expected MetaVertex, MetaEdge or MetaArrow, got " + repr(type(value).__name__))
        if isinstance(value, MetaEdge):
            value.write()
        return super().append(value, explore)
    
    def extend(self, values: Iterable[MetaVertex | MetaEdge], explore: bool = False):
        from typing import Iterable
        from ...bakery.source.graph import Graph
        if not isinstance(explore, bool):
            raise TypeError("Expected bool for explore, got " + repr(explore.__class__.__name__))
        if not isinstance(values, Iterable):
            raise TypeError("Expected iterable, got " + repr(values.__class__.__name__))
        def __checked():
            for v in values:
                if not isinstance(v, MetaVertex | MetaEdge | MetaArrow):
                    raise TypeError("Expected iterable of MetaVertex, MetaEdge or MetaArrow, got " + repr(type(v).__name__))
                if isinstance(v, MetaEdge):
                    v.write()
                yield v
        return Graph.extend(self, __checked(), explore)
    
    @overload
    def __or__(self, other: "MetaGraph") -> "MetaGraph":
        pass

    @overload
    def __or__(self, other : Graph) -> Graph:
        pass

    def __or__(self, other):
        if isinstance(other, MetaGraph):
            return MetaGraph(Graph.__or__(self, other))
        return Graph.__or__(self, other)
    
    @overload
    def __ror__(self, other: "MetaGraph") -> "MetaGraph":
        pass

    @overload
    def __ror__(self, other : Graph) -> Graph:
        pass

    def __ror__(self, other):
        if isinstance(other, MetaGraph):
            return MetaGraph(Graph.__ror__(other, self))
        return Graph.__ror__(other, self)
        
    @overload
    def __and__(self, other: "MetaGraph") -> "MetaGraph":
        pass

    @overload
    def __and__(self, other : Graph) -> Graph:
        pass

    def __and__(self, other):
        if isinstance(other, MetaGraph):
            return MetaGraph(Graph.__and__(self, other))
        return Graph.__and__(self, other)
    
    @overload
    def __rand__(self, other: "MetaGraph") -> "MetaGraph":
        pass

    @overload
    def __rand__(self, other : Graph) -> Graph:
        pass

    def __rand__(self, other):
        if isinstance(other, MetaGraph):
            return MetaGraph(Graph.__rand__(other, self))
        return Graph.__rand__(other, self)
    
    def __iter__(self) -> Iterator[MetaVertex | MetaEdge]:
        yield from self.vertices
        yield from self.edges    

    T = TypeVar("T", bound = MetaVertex | MetaEdge)

    def __getitem__(self, cls : type[T]) -> IsoSet[T]:
        """
        Implements self[cls]. Returns an Isoset of vertices or edges of this Graph that are only of the given class(es).
        """
        return Graph.__IsoSet(v for v in self.vertices if isinstance(v, cls)) | Graph.__IsoSet(e for e in self.edges if isinstance(e, cls))

    del T

    def __dir__(self) -> list[str]:
        return list(super().__dir__()) + self.names
    
    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError as e:
            if name not in self.__named_objects:
                raise e from None
            return self.__named_objects[name]
    
    def __getstate__(self) -> _MetaGraphStateDict:
        d = super().__getstate__() | {"named_objects" : self.__named_objects}
        return d
    
    def __setstate__(self, state: _MetaGraphStateDict):
        self.__named_objects = state.pop("named_objects")
        super().__setstate__(state)
    
    def __setattr__(self, name: str, value: Any) -> None:
        try:
            super().__getattribute__(name)
            return super().__setattr__(name, value)
        except AttributeError:
            if isinstance(value, MetaEdge | MetaVertex):
                self.__named_objects[name] = value
                self.append(value)
            else:
                return super().__setattr__(name, value)
    
    def __delattr__(self, name: str) -> None:
        if name in self.__named_objects:
            v = self.__named_objects.pop(name)
            if v not in self.__named_objects.values():
                self.remove(v)
        else:
            return super().__delattr__(name)
    
    def remove(self, value : MetaVertex | MetaEdge):
        for name, v in self.__named_objects.copy().items():
            if v == value:
                self.__named_objects.pop(name)
        super().remove(value)
    
    def __neighborhood_mapper(self, g : Graph) -> tuple[__IsoDict[Vertex, __IsoSet[MetaVertex]], __IsoDict[MetaVertex, int]]:
        """
        Searches the given graph for matches of the metagraph.
        Returns a mapping of the possible roles each Vertex can fit and the number of possible matches for each MetaVertex.
        """

        mapping : MetaGraph.__IsoDict[Vertex, MetaGraph.__IsoSet[MetaVertex]] = MetaGraph.__IsoDict()
        candidates : MetaGraph.__IsoDict[MetaVertex, int] = MetaGraph.__IsoDict((Mv, 0) for Mv in self.vertices)

        for v in g.vertices:
            for Mv in self.vertices:
                if Mv.match(v):
                    if v not in mapping:
                        mapping[v] = MetaGraph.__IsoSet()
                    mapping[v].add(Mv)
                    candidates[Mv] += 1
        
        return mapping, candidates
    
    def __clear_mapper_deadends(self, mapping : __IsoDict[Vertex, __IsoSet[MetaVertex]]):
        """
        Clears the deadends in a mapping returned by self.__neighborhood_mapper():
        (Operates on the mapping itself)
        """

        work = MetaGraph.__IsoDict((v, sMv.copy()) for v, sMv in mapping.items())

        while work:

            v, sMv = work.popitem()
            Mv = sMv.pop()
            if sMv:
                work[v] = sMv

            ok = False
            edge_possibilities : MetaGraph.__IsoDict[MetaEdge, MetaGraph.__IsoSet[Edge]] = MetaGraph.__IsoDict()     # For all MetaNeighbors. If any of them has an empty 

            for Me in Mv.edges:

                edge_possibilities[Me] = MetaGraph.__IsoSet()

                for e in v.edges:

                    if Me.match(e) and (not isinstance(Me, MetaArrow) or (e.source is v) == (Me.source is Mv)):     # MetaEdge or well-oriented MetaArrow
                        edge_possibilities[Me].add(e)
                                
            all_ok = True
            decisive_neighbors : MetaGraph.__IsoSet[tuple[Vertex, MetaVertex]] = MetaGraph.__IsoSet()

            for Me in edge_possibilities:

                ok = False

                for e in edge_possibilities[Me]:

                    u = e.source if e.source is not v else e.destination
                    Mu = Me.source if Me.source is not Mv else Me.destination
                    decisive_neighbors.add((u, Mu))
                    
                    if u in mapping and Mu in mapping[u]:
                        ok = True
            
                if not ok:
                    all_ok = False
            
            if not all_ok:
                mapping[v].discard(Mv)
                if not mapping[v]:
                    mapping.pop(v)
                
                for u, Mu in decisive_neighbors:
                    if u in mapping and Mu in mapping[u] and (u is not v or Mu is not Mv):      # Could cause issues in self-connected vertices
                        if u not in work:
                            work[u] = MetaGraph.__IsoSet()
                        work[u].add(Mu)
            
    def __expand_subgraph(self, g : Graph, mapping : __IsoDict[Vertex, __IsoSet[MetaVertex]], sub : __IsoDict[MetaVertex | MetaEdge, Vertex | Edge], Mv : MetaVertex) -> Iterator[__IsoDict[MetaVertex | MetaEdge, Vertex | Edge]]:
        """
        Yields all the next steps of the subgraph sub of Graph g in construction by adding all possible vertices that can fit the role of Mv.
        """
        from itertools import product

        existing : MetaGraph.__IsoDict[Vertex, MetaVertex] = MetaGraph.__IsoDict((sub[Mu], Mu) for Mu in Mv.neighbors() if Mu in sub)      # The neighbors of Mv that have already been chosen

        if not existing:        # We are starting from zero or we reached a new component
            
            used_Mvs = MetaGraph.__IsoSet(v for v in sub.values() if v in mapping and Mv in mapping[v])        # The candidates for Mv that are already part of the subgraph

            for v in mapping:
                if Mv in mapping[v] and v not in used_Mvs:
                    subv = sub.copy()
                    subv[Mv] = v
                    yield subv
            
            return

        existing_iter = iter(existing)

        u = next(existing_iter)

        vertex_possibilities : MetaGraph.__IsoSet[Vertex] = MetaGraph.__IsoSet(v for v in u.neighbors() if v in mapping and Mv in mapping[v])

        for u in existing_iter:
            vertex_possibilities.intersection_update({v for v in u.neighbors() if v in mapping and Mv in mapping[v]})
        
        vertex_possibilities.difference_update(sub.values())

        for v in vertex_possibilities:
            edge_possibilities : MetaGraph.__IsoDict[MetaEdge, MetaGraph.__IsoSet[Edge]] = MetaGraph.__IsoDict()

            for u, Mu in existing.items():

                edges = u.edges & v.edges
                Medges = Mu.edges & Mv.edges
                for Me in Medges:
                    edge_possibilities[Me] = MetaGraph.__IsoSet()
                    for e in edges:
                        if Me.match(e) and (not isinstance(Me, MetaArrow) or (e.source is v) == (Me.source is Mv)):
                            edge_possibilities[Me].add(e)
            
            Me_list = list(edge_possibilities)
            for e_list in product(*[edge_possibilities[Me] for Me in Me_list]):
                if len(MetaGraph.__IsoSet(e_list)) == len(e_list):     # No edge was used as two different MetaEdges between v and one of its neighbors
                    subv = sub.copy()
                    subv[Mv] = v
                    for Me, e in zip(Me_list, e_list):
                        subv[Me] = e
                    yield subv

    def __discover(self) -> Iterator[MetaVertex]:
        """
        Yields successive MetaVertices by exploring the MetaGraph. The next MetaVertex yielded is either a neighbor of one of the previously yielded ones or is the first of a new connected component.
        """
        
        to_do : MetaGraph.__IsoSet[MetaVertex] = MetaGraph.__IsoSet(self.vertices)
        done : MetaGraph.__IsoSet[MetaVertex] = MetaGraph.__IsoSet()
        component_explorable : MetaGraph.__IsoSet[MetaVertex] = MetaGraph.__IsoSet()

        while to_do:
            if not component_explorable:
                Mu = to_do.pop()
                component_explorable.add(Mu)

            else:
                component_done = True
                for Mv in component_explorable.copy():
                    sMu = MetaGraph.__IsoSet(Mv.neighbors()) - done
                    if sMu:
                        component_done = False
                        Mu = sMu.pop()
                        to_do.discard(Mu)
                        break
                    else:
                        component_explorable.remove(Mv)

                if component_done:
                    continue
                    
            component_explorable.add(Mu)
            yield Mu
            done.add(Mu)
         
    def search_iter(self, g : Graph) -> Iterator[Graph]:
        """
        Searches through g for all occurences of a subgraph that matches the metagraph.
        Yields all the matching subgraphs.
        """
        from typing import Iterator

        from ...bakery.source.graph import Graph

        # subgraphs : list[dict[MetaVertex | MetaEdge, Vertex | Edge]] = [{}]
        # next_subgraphs : list[dict[MetaVertex | MetaEdge, Vertex | Edge]] = []

        mapping, candidates = self.__neighborhood_mapper(g)
        if 0 in candidates.values():        # At least one MetaVertex has no matches...
            return

        self.__clear_mapper_deadends(mapping)

        order = list(self.__discover())

        # print("Got {} vertices with openings.".format(len([v for v, sMv in mapping.items() if sMv])))

        def build_iter(g : Graph, mapping : MetaGraph.__IsoDict[Vertex, MetaGraph.__IsoSet[MetaVertex]], sub : MetaGraph.__IsoDict[MetaVertex | MetaEdge, Vertex | Edge], i : int) -> Iterator[Graph]:
            if i == len(order) - 1:     # Last MetaVertex to append
                for subi in self.__expand_subgraph(g, mapping, sub, order[i]):
                    gi = Graph()
                    gi.extend(subi.values())
                    yield gi
            else:
                for subi in self.__expand_subgraph(g, mapping, sub, order[i]):
                    yield from build_iter(g, mapping, subi, i + 1)
        
        yield from build_iter(g, mapping, MetaGraph.__IsoDict(), 0)

        # for i, Mv in enumerate(self.__discover()):
        #     for sub in subgraphs:
        #         next_subgraphs.extend(self.__expand_subgraph(g, mapping, sub, Mv))
        #     subgraphs = next_subgraphs
        #     next_subgraphs = []
        
        # for dg in subgraphs:
        #     g = Graph()
        #     g.extend(dg.values())
        #     yield g



    class Match:

        """
        An object that represents a match between a MetaGraph and a Graph.
        """

        __slots__ = {
            "__metagraph",
            "__match",
            "__map"
        }

        def __init__(self, metagraph : "MetaGraph", match : Graph, map : IsoDict[MetaVertex | MetaEdge, Vertex | Edge]) -> None:
            self.__metagraph = metagraph
            self.__match = match
            self.__map = map

        @property
        def metagraph(self) -> "MetaGraph":
            """
            The MetaGraph that this is a match for.
            """
            return self.__metagraph
        
        @property
        def graph(self) -> Graph:
            """
            The complete Graph that matches the MetaGraph.
            """
            return self.__match
        
        @overload
        def __getitem__(self, i : MetaVertex) -> Vertex:
            pass

        @overload
        def __getitem__(self, i : MetaEdge) -> Edge:
            pass

        @overload
        def __getitem__(self, i : MetaArrow) -> Arrow:
            pass

        @overload
        def __getitem__(self, i : Vertex) -> MetaVertex:
            pass

        @overload
        def __getitem__(self, i : Edge) -> MetaEdge:
            pass

        def __getitem__(self, i):
            """
            Implements self[i].
            If i is a MetaVertex/MetaEdge, returns the matched Vertex/Edge.
            If i is a Vertex/Edge, returns the matching MetaVertex/MetaEdge.
            """
            if isinstance(i, (MetaVertex, MetaEdge)):
                if i not in self.__map:
                    raise KeyError(i)
                return self.__map[i]
            else:
                for Mj, j in self.__map.items():
                    if i is j:
                        return Mj
                raise KeyError(i)
            
        def pairs(self):
            """
            Iterates over all the match pairs.
            """
            return ((i, self[i]) for i in self.__map)



    def match_iter(self, g : Graph) -> Iterator[Match]:
        """
        Searches through g for all occurences of a subgraph that matches the metagraph.
        Yields all the possible Match objects.
        """
        from typing import Iterator

        from ...bakery.source.graph import Graph

        # subgraphs : list[dict[MetaVertex | MetaEdge, Vertex | Edge]] = [{}]
        # next_subgraphs : list[dict[MetaVertex | MetaEdge, Vertex | Edge]] = []

        mapping, candidates = self.__neighborhood_mapper(g)
        if 0 in candidates.values():        # At least one MetaVertex has no matches...
            return

        self.__clear_mapper_deadends(mapping)

        order = list(self.__discover())

        # print("Got {} vertices with openings.".format(len([v for v, sMv in mapping.items() if sMv])))

        def build_iter(g : Graph, mapping : MetaGraph.__IsoDict[Vertex, MetaGraph.__IsoSet[MetaVertex]], sub : MetaGraph.__IsoDict[MetaVertex | MetaEdge, Vertex | Edge], i : int) -> Iterator[tuple[Graph, IsoDict[MetaVertex | MetaEdge, Vertex | Edge]]]:
            if i == len(order) - 1:     # Last MetaVertex to append
                for subi in self.__expand_subgraph(g, mapping, sub, order[i]):
                    gi = Graph()
                    gi.extend(subi.values())
                    yield gi, subi
            else:
                for subi in self.__expand_subgraph(g, mapping, sub, order[i]):
                    yield from build_iter(g, mapping, subi, i + 1)
        
        yield from (MetaGraph.Match(self, gi, mapi) for gi, mapi in build_iter(g, mapping, MetaGraph.__IsoDict(), 0))

    def __contains__(self, g : Graph) -> bool:
        """
        Implements g in self. Returns True if Graph g matches entirely MetaGraph self.
        """
        if len(g.vertices) > len(self.vertices) or len(g.edges) > len(self.edges):
            return False
        return g in self.search_iter(g)





class FrozenMetaGraph(MetaGraph, FrozenGraph):

    """
    Frozen (immutable) version of MetaGraphs. Built from a Graph or MetaGraph given to its constructor.
    """

    from Viper.collections import FrozenIsoSet as __FrozenIsoSet
    from ...bakery.source.graph import FrozenGraph as __FrozenGraph

    def __init__(self, g: Iterable[Vertex | Edge] | Graph = Graph()) -> None:
        MetaGraph.__init__(self, g)
        self.vertices : "FrozenMetaGraph.__FrozenIsoSet[MetaVertex]" = FrozenMetaGraph.__FrozenIsoSet(self.vertices)
        self.edges : "FrozenMetaGraph.__FrozenIsoSet[MetaEdge]" = FrozenMetaGraph.__FrozenIsoSet(self.edges)

    def append(self, value: MetaVertex | MetaEdge, explore: bool = False) -> Never:
        raise AttributeError(f"Cannot append to a '{type(self).__name__}'")
    
    def remove(self, value: MetaVertex | MetaEdge) -> Never:
        raise AttributeError(f"Cannot remove from a '{type(self).__name__}'")
    
    def extend(self, values: Iterable[MetaVertex | MetaEdge], explore: bool = False) -> Never:
        raise AttributeError(f"Cannot extend a '{type(self).__name__}'")
    
    @overload
    def __or__(self, other: "FrozenMetaGraph") -> "FrozenMetaGraph":
        pass

    @overload
    def __or__(self, other : MetaGraph) -> MetaGraph:
        pass

    @overload
    def __or__(self, other : FrozenGraph) -> FrozenGraph:
        pass

    @overload
    def __or__(self, other : Graph) -> Graph:
        pass

    def __or__(self, other):
        if isinstance(other, FrozenMetaGraph):
            return FrozenMetaGraph(Graph.__or__(self, other))
        elif isinstance(other, MetaGraph):
            return MetaGraph(Graph.__or__(self, other))
        elif isinstance(other, FrozenMetaGraph.__FrozenGraph):
            return FrozenMetaGraph.__FrozenGraph(Graph.__or__(self, other))
        return Graph.__or__(self, other)

    @overload
    def __ror__(self, other: "FrozenMetaGraph") -> "FrozenMetaGraph":
        pass

    @overload
    def __ror__(self, other : MetaGraph) -> MetaGraph:
        pass

    @overload
    def __ror__(self, other : FrozenGraph) -> FrozenGraph:
        pass

    @overload
    def __ror__(self, other : Graph) -> Graph:
        pass

    def __ror__(self, other):
        if isinstance(other, FrozenMetaGraph):
            return FrozenMetaGraph(Graph.__ror__(self, other))
        elif isinstance(other, MetaGraph):
            return MetaGraph(Graph.__ror__(self, other))
        elif isinstance(other, FrozenMetaGraph.__FrozenGraph):
            return FrozenMetaGraph.__FrozenGraph(Graph.__ror__(self, other))
        return Graph.__ror__(self, other)
    
    @overload
    def __and__(self, other: "FrozenMetaGraph") -> "FrozenMetaGraph":
        pass

    @overload
    def __and__(self, other : MetaGraph) -> MetaGraph:
        pass

    @overload
    def __and__(self, other : FrozenGraph) -> FrozenGraph:
        pass

    @overload
    def __and__(self, other : Graph) -> Graph:
        pass

    def __and__(self, other):
        if isinstance(other, FrozenMetaGraph):
            return FrozenMetaGraph(Graph.__and__(self, other))
        elif isinstance(other, MetaGraph):
            return MetaGraph(Graph.__and__(self, other))
        elif isinstance(other, FrozenMetaGraph.__FrozenGraph):
            return FrozenMetaGraph.__FrozenGraph(Graph.__and__(self, other))
        return Graph.__and__(self, other)

    @overload
    def __rand__(self, other: "FrozenMetaGraph") -> "FrozenMetaGraph":
        pass

    @overload
    def __rand__(self, other : MetaGraph) -> MetaGraph:
        pass

    @overload
    def __rand__(self, other : FrozenGraph) -> FrozenGraph:
        pass

    @overload
    def __rand__(self, other : Graph) -> Graph:
        pass

    def __rand__(self, other):
        if isinstance(other, FrozenMetaGraph):
            return FrozenMetaGraph(Graph.__rand__(self, other))
        elif isinstance(other, MetaGraph):
            return MetaGraph(Graph.__rand__(self, other))
        elif isinstance(other, FrozenMetaGraph.__FrozenGraph):
            return FrozenMetaGraph.__FrozenGraph(Graph.__rand__(self, other))
        return Graph.__rand__(self, other)

    def __getstate__(self) -> _MetaGraphStateDict:
        return MetaGraph.__getstate__(self) | FrozenMetaGraph.__FrozenGraph.__getstate__(self)
    
    def __setstate__(self, state: _MetaGraphStateDict):
        MetaGraph.__setstate__(self, state)
        FrozenMetaGraph.__FrozenGraph.__setstate__(self, state)

    

# N = 0

# class Square(UniqueVertex):
#     def __init__(self, *, c: Color = Color.blue, parent: Optional["Vertex"] = None) -> None:
#         global N
#         super().__init__(c=c, parent=parent)
#         self.label = type(self).__name__[0]+str(N)
#         N += 1

# class Triangle(UniqueVertex):
#     def __init__(self, *, c: Color = Color.red, parent: Optional["Vertex"] = None) -> None:
#         global N
#         super().__init__(c=c, parent=parent)
#         self.label = type(self).__name__[0]+str(N)
#         N += 1

# class Circle(UniqueVertex):
#     def __init__(self, *, c: Color = Color.green, parent: Optional["Vertex"] = None) -> None:
#         global N
#         super().__init__(c=c, parent=parent)
#         self.label = type(self).__name__[0]+str(N)
#         N += 1

# class TriangleToTriangle(Arrow):
#     pass

# class TriangleToCircle(Arrow):
#     pass

# class CircleToSquare(Arrow):
#     pass

# class SquareToTriangle(Arrow):
#     pass



# print("Building and exporting MetaGraph.")
# MG = MetaGraph()

# T0 = MetaVertex[Triangle]
# T1 = MetaVertex[Triangle]
# C2 = MetaVertex[Circle]
# S3 = MetaVertex[Square]
# T4 = MetaVertex[Triangle]

# print(repr(T0), repr(T1), repr(C2), repr(S3), repr(T4))

# MetaArrow(T0, T1).cls = TriangleToTriangle
# MetaArrow(T1, C2).cls = TriangleToCircle
# MetaArrow(C2, S3).cls = CircleToSquare
# MetaArrow(S3, T4).cls = SquareToTriangle
# MetaArrow(T4, T1).cls = TriangleToTriangle
# MetaArrow(T1, T4).cls = TriangleToTriangle

# MG.append(T0, explore=True)

# MG.export("meta.gexf")

# print("Building Graph.")
# g = Graph()

# C0 = Circle()
# T1 = Triangle()
# S2 = Square()
# T3 = Triangle()
# T4 = Triangle()
# T5 = Triangle()
# S6 = Square()
# T7 = Triangle()
# T8 = Triangle()
# C9 = Circle()
# C10 = Circle()
# C11 = Circle()
# S12 = Square()
# T13 = Triangle()
# S14 = Square()
# C15 = Circle()
# C16 = Circle()
# S17 = Square()
# T18 = Triangle()
# T19 = Triangle()
# T20 = Triangle()
# T21 = Triangle()

# TriangleToCircle(T3, C0)
# CircleToSquare(C0, S2)
# TriangleToTriangle(T1, T3)
# TriangleToTriangle(T4, T1)
# SquareToTriangle(S2, T3)
# TriangleToTriangle(T5, T3)
# SquareToTriangle(S6, T4)
# TriangleToTriangle(T3, T8)
# TriangleToTriangle(T8, T3)
# TriangleToCircle(T3, C9)
# TriangleToCircle(T8, C9)
# TriangleToCircle(T5, C11)
# CircleToSquare(C11, S6)
# CircleToSquare(C11, S17)
# CircleToSquare(C9, S12)
# SquareToTriangle(S12, T8)
# CircleToSquare(C15, S12)
# CircleToSquare(C15, S17)
# TriangleToCircle(T7, C10)
# TriangleToTriangle(T7, T13)
# TriangleToTriangle(T13, T7)
# CircleToSquare(C10, S14)
# SquareToTriangle(S14, T13)
# CircleToSquare(C16, S12)
# CircleToSquare(C16, S14)
# SquareToTriangle(S17, T18)
# TriangleToCircle(T19, C15)
# TriangleToCircle(T20, C16)
# TriangleToCircle(T21, C16)
# SquareToTriangle(S14, T20)
# SquareToTriangle(S14, T21)
# TriangleToTriangle(T18, T19)
# TriangleToTriangle(T19, T18)
# TriangleToTriangle(T19, T20)
# TriangleToTriangle(T20, T21)
# TriangleToTriangle(T21, T20)
# TriangleToTriangle(T19, T21)

# g.append(T5, explore=True)

# print("Matching...")

# for i, subi in enumerate(MG.search_iter(g)):
#     if i == 3:
#         for v in subi.vertices:
#             v.color = color.white
#         for e in subi.edges:
#             e.color = color.white

# print("Exporting Graph.")
# g.export("graph.gexf")