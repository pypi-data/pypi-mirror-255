"""
This module contains Vertex subclasses for this behavioral package.
"""

from typing import Iterator, Literal, Optional, Sequence
from Viper.collections.isomorph import IsoDict

from .....logger import logger
from ...config import ColorSetting, SizeSetting
from ...colors import Color
from ...graph import DataVertex
from ...utils import chrono
from ..filesystem.entities import File, Handle
from ..network.entities import Connection, Socket
from .utils import IOOperation, PreDiffDescriptor

__all__ = ["Data", "Diff"]





logger.info("Loading entities from {} library.".format(__name__.rpartition(".")[0].rpartition(".")[2]))

class Data(DataVertex):
    
    """
    A data vertex. Represents data read, written or appended to a file.
    """

    from .utils import entropy as entropy_func
    __entropy = staticmethod(entropy_func)
    del entropy_func

    similarity_threshold = 0.75

    __slots__ = {
        "__data" : "The bytes data exchanged through the handle",
        "__time" : "The time at which this message was seen",
        "__initialized" : "Indicates if this Vertex can be compared to other Data Vertices"
    }

    __defining_data__ = DataVertex.__defining_data__ | {
        "data",
        "time"
    }
    
    __computable_properties__ = DataVertex.__computable_properties__ | {
        "length",
        "entropy",
        "isprintable"
    }

    default_color = ColorSetting(Color(0.5882352941176471, 1.0, 1.0))
    default_size = SizeSetting(0.5)

    def __init__(self, *, data : bytes, time : float) -> None:
        super().__init__(data = data, time = time)
        self.__initialized = False

    @property
    def data(self) -> bytes:
        """
        The data exchanged.
        """
        return self.__data
    
    @data.setter
    def data(self, d : bytes):
        if not isinstance(d, bytes):
            raise TypeError(f"Expected bytes, got '{type(d).__name__}'")
        self.__data = d

    @property
    def time(self) -> float:
        """
        The time at which this data was seen.
        """
        return self.__time
    
    @time.setter
    def time(self, t : float):
        if not isinstance(t, float):
            raise TypeError(f"Expected float, got '{type(t).__name__}'")
        self.__time = t
    
    @property
    def length(self) -> int:
        """
        The length (in bytes) of the data.
        """
        return len(self.data)
    
    @property
    def entropy(self) -> float:
        """
        The byte-wise entropy of the data.
        """
        return Data.__entropy(self.data)

    @property
    def isprintable(self) -> bool:
        """
        True if the data only contains printable characters.
        """
        try:
            data = self.data.decode()
        except:
            return False
        return data.isprintable()

    @property
    def vector(self) -> Handle | Socket:
        """
        The Handle or Socket Vertex that this Data node is Conveying data to or from.
        """
        from ..filesystem import Handle
        from ..network import Socket
        for u in self.neighbors():
            if isinstance(u, Handle | Socket):
                return u
        raise RuntimeError("Got a data node without vector.")
    
    def compare(self):
        """
        Links the node to other similar nodes.
        """
        from .relations import IsSimilarTo
        from .utils import levenshtein_similarity
        self.__initialized = True
        for d in Data:
            if (1 - Data.similarity_threshold) * max(len(d.data), len(self.data)) < abs(len(d.data) - len(self.data)):      # Size difference is too high, similarity will be below threshold
                continue
            if d is not self and d.__initialized:
                s1 = levenshtein_similarity(d.data, self.data, Data.similarity_threshold)
                if s1 < Data.similarity_threshold:
                    continue
                if self.time < d.time:
                    l1 = IsSimilarTo(self, d)
                else:
                    l1 = IsSimilarTo(d, self)
                l1.weight = s1
                # s2 = levenshtein_subset_similarity(d.data, self.data)
                # if self.time < d.time:
                #     l2 = IsAlmostIn(self, d)
                # else:
                #     l2 = IsAlmostIn(d, self)
                # l2.weight = s2





class Diff(DataVertex):

    """
    A diff vertex. This represents all the information gathered on a file's content during the lifetime of a handle.
    """

    from typing import Iterable as __Iterable
    from .utils import IOOperation as __IOOperation

    similarity_threshold = 0.90

    __slots__ = {
        "__read" : "The content of the read diff file",
        "__read_type" : "The file type determined by libmagic from what has been read",
        "__written" : "The content of the write diff file",
        "__written_type" : "The file type determined by libmagic from what has been written",
        "__glob" : "The content of the global diff file",
        "__glob_type" : "The file type determined by libmagic from the final state of the file",
        "__read_total" : "The total amount of bytes that were read",  # Counts double if you read twice the same byte
        "__read_space" : "The amount of bytes that were read in the file",    # This one only counts one
        "__written_total" : "The total amount of bytes that were written",
        "__written_space" : "The amount of bytes that were written in the file",
        "__glob_space" : "The amount of bytes that were accessed in the file",
        "__read_entropy" : "The amount of entropy that was read from the file",
        "__written_entropy" : "The amount of entropy that was written to the file",
        "__glob_entropy" : "The entropy that resulted in the file from all operations",
        "__printable_rate" : "Indicates how much of the final state of the file only contains printable characters",
        "__encoding" : "A valid encoding for the final file",
        "__operations" : "The list of all operations that appear in the Diff node",
        "__analyzer_inst" : "A magic analyzer to infer file type"
    }

    __defining_data__ = DataVertex.__defining_data__ | {
        "read",
        "written",
        "glob"
    }

    __additional_data__ = DataVertex.__additional_data__ | {
        "read_type",
        "written_type",
        "glob_type",
        "read_total",
        "written_total",
        "read_entropy",
        "written_entropy",
        "glob_entropy",
        "printable_rate",
        "encoding"
    }

    __computable_properties__ = DataVertex.__computable_properties__ | {
        "read_space",
        "written_space",
        "glob_space",
    }

    default_color = ColorSetting(Color(50, 150, 255))
    default_size = SizeSetting(1.5)

    min_size = SizeSetting(0.5)
    max_size = SizeSetting(2.5)

    diff_low_entropy_color = ColorSetting(Color(50, 150, 255))
    diff_high_entropy_color = ColorSetting(Color(255, 50, 150))

    def __init__(self, *, read : bytes, written : bytes, glob : bytes, operations : __Iterable[IOOperation]) -> None:
        self.__read_type = None
        self.__written_type = None
        self.__glob_type = None
        self.__read_total = None
        self.__written_total = None
        self.__read_entropy = None
        self.__written_entropy = None
        self.__glob_entropy = None
        self.__printable_rate = None
        self.__encoding = None
        self.__analyzer_inst = None

        self.operations = operations
        super().__init__(read = read, written = written, glob = glob)

    def __setstate__(self, state):
        self.__analyzer_inst = None
        super().__setstate__(state)

    @property
    def __analyzer(self):
        """
        Internal libmagic analyzer.
        """
        if self.__analyzer_inst is None:
            from magic import Magic
            self.__analyzer_inst = Magic(keep_going=True, uncompress=True)
        return self.__analyzer_inst
    
    @property
    def operations(self) -> tuple[IOOperation, ...]:
        """
        The sequence of IO operations that led to this Diff node's buffers.
        """
        return self.__operations
    
    @operations.setter
    def operations(self, o : __Iterable[IOOperation]):
        if not isinstance(o, Diff.__Iterable):
            raise TypeError(f"Expected iterable, got '{type(o).__name__}'")
        o = tuple(o)
        for e in o:
            if not isinstance(e, Diff.__IOOperation):
                raise TypeError(f"Expected iterable if IOOperation, got a '{type(e).__name__}'")
        self.__operations = o

    @property
    def read(self) -> bytes:
        """
        The current content of the read diff file.
        """
        return self.__read

    @read.setter
    def read(self, data : bytes):
        if not isinstance(data, bytes):
            raise TypeError(f"Expected bytes, got '{type(data).__name__}'")
        self.__read = data
    
    @property
    def written(self) -> bytes:
        """
        The current content of the write diff file.
        """
        return self.__written
    
    @written.setter
    def written(self, data : bytes):
        if not isinstance(data, bytes):
            raise TypeError(f"Expected bytes, got '{type(data).__name__}'")
        self.__written = data
    
    @property
    def glob(self) -> bytes:
        """
        The current content of the global diff file.
        """
        return self.__glob
    
    @glob.setter
    def glob(self, data : bytes):
        if not isinstance(data, bytes):
            raise TypeError(f"Expected bytes, got '{type(data).__name__}'")
        self.__glob = data
    
    @property
    def content(self) -> tuple[bytes, bytes, bytes]:
        """
        The current content of the read, write and global diff files.
        """
        return self.read, self.written, self.glob
    
    @property
    def read_type(self) -> Sequence[str]:
        """
        The file types identified by libmagic for the read buffer.
        """
        if self.__read_type is None:
            self.__read_type = self.__analyzer.from_buffer(self.read).split("\\012- ")
        return self.__read_type
    
    @read_type.setter
    def read_type(self, t : list[str]):
        if not isinstance(t, list):
            raise TypeError(f"Expected list, got '{type(t).__name__}'")
        for e in t:
            if not isinstance(e, str):
                raise TypeError(f"Expected list[str], got a '{type(e).__name__}'")
        self.__read_type = t

    @property
    def written_type(self) -> Sequence[str]:
        """
        The file types identified by libmagic for the write buffer.
        """
        if self.__written_type is None:
            self.__written_type = self.__analyzer.from_buffer(self.written).split("\\012- ")
        return self.__written_type
    
    @written_type.setter
    def written_type(self, t : list[str]):
        if not isinstance(t, list):
            raise TypeError(f"Expected list, got '{type(t).__name__}'")
        for e in t:
            if not isinstance(e, str):
                raise TypeError(f"Expected list[str], got a '{type(e).__name__}'")
        self.__written_type = t

    @property
    def glob_type(self) -> Sequence[str]:
        """
        The file types identified by libmagic for the global buffer.
        """
        if self.__glob_type is None:
            self.__glob_type = self.__analyzer.from_buffer(self.glob).split("\\012- ")
        return self.__glob_type
    
    @glob_type.setter
    def glob_type(self, t : list[str]):
        if not isinstance(t, list):
            raise TypeError(f"Expected list, got '{type(t).__name__}'")
        for e in t:
            if not isinstance(e, str):
                raise TypeError(f"Expected list[str], got a '{type(e).__name__}'")
        self.__glob_type = t

    @property
    def read_total(self) -> int:
        """
        The total amount of bytes read from the buffer (with repetition).
        """
        if self.__read_total is None:
            from .utils import Read
            self.__read_total = sum(len(op.data) for op in self.__operations if isinstance(op, Read))
        return self.__read_total
    
    @read_total.setter
    def read_total(self, t : int):
        if not isinstance(t, int):
            raise TypeError(f"Expected int, got '{type(t).__name__}'")
        self.__read_total = t

    @property
    def written_total(self) -> int:
        """
        The total amount of bytes written from the buffer (with repetition).
        """
        if self.__written_total is None:
            from .utils import Write
            self.__written_total = sum(len(op.data) for op in self.__operations if isinstance(op, Write))
        return self.__written_total
    
    @written_total.setter
    def written_total(self, t : int):
        if not isinstance(t, int):
            raise TypeError(f"Expected int, got '{type(t).__name__}'")
        self.__written_total = t
    
    @property
    def read_space(self) -> int:
        """
        The total amount of bytes read in the target (no repetition).
        """
        return len(self.read)
    
    @property
    def written_space(self) -> int:
        """
        The total amount of bytes written in the target (no repetition).
        """
        return len(self.written)

    @property
    def glob_space(self) -> int:
        """
        The total amount of bytes read/written in the target (no repetition).
        """
        return len(self.glob)
    
    @property
    def read_entropy(self) -> float:
        """
        The byte-wise entropy of the read buffer.
        """
        if self.__read_entropy is None:
            from .utils import entropy
            self.__read_entropy = entropy(self.read)
        return self.__read_entropy
    
    @read_entropy.setter
    def read_entropy(self, e : float):
        if not isinstance(e, float):
            raise TypeError(f"Expected float, got '{type(e).__name__}'")
        self.__read_entropy = e

    @property
    def written_entropy(self) -> float:
        """
        The byte-wise entropy of the write buffer.
        """
        if self.__written_entropy is None:
            from .utils import entropy
            self.__written_entropy = entropy(self.written)
        return self.__written_entropy
    
    @written_entropy.setter
    def written_entropy(self, e : float):
        if not isinstance(e, float):
            raise TypeError(f"Expected float, got '{type(e).__name__}'")
        self.__written_entropy = e

    @property
    def glob_entropy(self) -> float:
        """
        The byte-wise entropy of the global buffer.
        """
        if self.__glob_entropy is None:
            from .utils import entropy
            self.__glob_entropy = entropy(self.glob)
        return self.__glob_entropy
    
    @glob_entropy.setter
    def glob_entropy(self, e : float):
        if not isinstance(e, float):
            raise TypeError(f"Expected float, got '{type(e).__name__}'")
        self.__glob_entropy = e

    @property
    def printable_rate(self) -> float:
        """
        The ratio of characters in the final version of the target that are printable.
        """
        if self.__printable_rate is None:
            from .utils import printable_rate_and_encoding
            self.__printable_rate, self.__encoding = printable_rate_and_encoding(self.glob)
        return self.__printable_rate
    
    @printable_rate.setter
    def printable_rate(self, r : float):
        if not isinstance(r, float):
            raise TypeError(f"Expected float, got '{type(r).__name__}'")
        self.__printable_rate = r

    @property
    def encoding(self) -> str:
        """
        Returns the most probable encoding of the final state of the target.
        """
        if self.__encoding is None:
            from .utils import printable_rate_and_encoding
            self.__printable_rate, self.__encoding = printable_rate_and_encoding(self.glob)
        return self.__encoding
    
    @encoding.setter
    def encoding(self, e : str):
        if not isinstance(e, str):
            raise TypeError(f"Expected str, got '{type(e).__name__}'")
        self.__encoding = e
    
    @chrono
    @staticmethod
    def process_data(pre_diff : PreDiffDescriptor):
        """
        Given a PreDiffDescriptor, checks if the associated Diff node already exists, finds the similar nodes, create it if it does not exist itself and links its to its target or vector.
        """

        from ...config import CompilationParameters
        from .relations import HasSimilarContent, IsDiffOf, IsReadBy, WritesInto
        from .utils import levenshtein_similarity

        r, w, g = pre_diff.reader.dump(), pre_diff.writer.dump(), pre_diff.glob.dump()
        
        similars : list[tuple[Diff, float, 'Literal["read_buffer", "write_buffer", "global_buffer"]', 'Literal["read_buffer", "write_buffer", "global_buffer"]']] = []
        
        for u in Diff:
            lw, ls, ld = 0.0, "", ""
            if (r, w, g) == u.content:
                self = u
                break

            if not CompilationParameters.SkipLevenshteinForDiffNodes:
                for sn, sb in zip(("read_buffer", "write_buffer", "global_buffer"), (r, w, g)):
                    if sb:
                        for un, ub in zip(("read_buffer", "write_buffer", "global_buffer"), u.content):
                            if (1 - Diff.similarity_threshold) * max(len(sb), len(ub)) < abs(len(sb) - len(ub)):      # Size difference is too high, similarity will be below threshold
                                continue
                            if ub:
                                s = levenshtein_similarity(sb, ub, Diff.similarity_threshold)
                                if s >= lw:
                                    lw = s
                                    ls = sn
                                    ld= un
                if ls and lw >= Diff.similarity_threshold:      # Heuristic is not perfect : checking that the threshold has indeed been reached!
                    similars.append((
                        u,
                        lw * (HasSimilarContent.max_weight - HasSimilarContent.min_weight) + HasSimilarContent.min_weight,        # 0 <= lw <= 1
                        ls,
                        ld
                    ))
        
        else:
            self = Diff(read = r, written = w, glob = g, operations = pre_diff.operation)
            for u, lw, ls, ld in similars:
                l = HasSimilarContent(self, u, source_buffer = ls, destination_buffer = ld)
                l.weight = lw
                
        if r and not w:
            IsReadBy(self, pre_diff.target_or_vector)
        elif w and not r:
            WritesInto(pre_diff.target_or_vector, self)
        else:
            IsDiffOf(pre_diff.target_or_vector, self)
    
    @property
    def label(self) -> str:
        """
        The name of the node to display. It is the global data type.
        """
        if len(self.glob_type) == 1:
            return self.glob_type[0]
        return " | ".join(t for t in self.glob_type if t != "data")

    @property
    def vectors(self) -> Iterator[Handle | Socket]:
        """
        The Handle or Socket Vertices that this Diff node is interacting with.
        """
        from ..filesystem import Handle
        from ..network import Socket
        for u in self.neighbors():
            if isinstance(u, Handle | Socket):
                yield u
    
    @property
    def targets(self) -> Iterator[File | Connection]:
        """
        The File or Connection Vertices that this Diff node is interacting with.
        """
        from ..filesystem import File
        from ..network import Connection
        for u in self.neighbors():
            if isinstance(u, File | Connection):
                yield u





del Iterator, Literal, Optional, Sequence, IsoDict, logger, ColorSetting, SizeSetting, Color, DataVertex, chrono, File, Handle, Connection, Socket, IOOperation, PreDiffDescriptor