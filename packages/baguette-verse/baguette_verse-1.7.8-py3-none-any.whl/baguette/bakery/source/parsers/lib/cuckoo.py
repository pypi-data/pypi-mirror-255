"""
This is the ParserClass for Cuckoo reports.
"""

from pathlib import Path, PurePath
from types import NotImplementedType
from typing import Any, Iterable, Iterator, Literal, TypedDict
from ..abc import CallInfo, MachineInfo, AbstractParser, ProcessInfo, ThreadInfo





class ProcessTree(TypedDict):

    pid : int
    track : bool
    process_name : str
    command_line : str
    first_seen : float
    children : "list[ProcessTree]"


class RawProcessInfo(TypedDict):

    pid : int
    track : bool
    process_name : str
    command_line : str
    first_seen : float
    process_path : str
    calls : "list[RawCallInfo]"
    modules : "list[RawImportInfo]"


class RawCallInfo(TypedDict):

    api : str
    status : int
    return_value : int
    arguments : dict[str, Any]
    flags : dict[str, Any]
    time : float
    tid : int


class RawImportInfo(TypedDict):

    imgsize : int
    baseaddr : str
    filepath : str





class CuckooParser(AbstractParser):

    """
    A report parser specialized for the Cuckoo sandbox.
    """

    report_name = "cuckoo"

    from json import load, JSONDecodeError as __JSONDecodeError
    from ..abc import ProcessInfo as __ProcessInfo, ImportInfo as __ImportInfo, ThreadInfo as __ThreadInfo, CallInfo as __CallInfo
    from ...utils import path_factory
    __path_factory = staticmethod(path_factory)
    __load = staticmethod(load)
    del load, path_factory

    def __init__(self, p: Path) -> None:
        super().__init__(p)
        self.__path = p
        self.__execution_tree : "list[tuple[ProcessInfo | None, ProcessInfo]]" = []
        self.__machines : "tuple[MachineInfo, ...] | None" = None
        self.__host : "MachineInfo | None" = None
        with p.open("r") as f:
            self.__data = CuckooParser.__load(f)

    @staticmethod
    def match_report_type(p: Path) -> bool | NotImplementedType:
        with p.open("r") as f:
            try:
                data = CuckooParser.__load(f)
            except CuckooParser.__JSONDecodeError:
                return False
        return isinstance(data, dict) and "debug" in data and isinstance(data["debug"], dict) and "cuckoo" in data["debug"] and isinstance(data["debug"]["cuckoo"], list)
    
    def process_tree_iterator(self) -> Iterator[tuple[ProcessInfo | None, ProcessInfo]]:
        if "behavior" not in self.__data:
            raise ValueError(f"Given Cuckoo report does not contain any behavioral info: '{self.__path}'")
        from Viper.frozendict import frozendict
        
        def clean_dict(d : "dict[str, Any]"):
            cd = {}
            for k, v in d.items():
                if isinstance(v, list):
                    cd[k] = tuple(v)
                elif isinstance(v, dict):
                    cd[k] = frozendict(v)
                else:
                    cd[k] = v
            return cd
        
        def thread_info_iterator(p : "RawProcessInfo"):
            starts : "dict[int, float]" = {}
            stops : "dict[int, float]" = {}
            calls : "dict[int, list[CallInfo]]" = {}
            for c in p["calls"]:
                starts.setdefault(c["tid"], c["time"])
                stops[c["tid"]] = c["time"]
                calls.setdefault(c["tid"], []).append(self.translator.translate(CuckooParser.__CallInfo(c["api"], bool(c["status"]), c["return_value"], clean_dict(c["arguments"]), clean_dict(c["flags"]), c["time"])))
            return tuple(ThreadInfo(TID, starts[TID], stops[TID], tuple(calls[TID])) for TID in starts)
        
        def explore_process_tree(p : "ProcessTree", parent : "ProcessInfo | None" = None) -> "Iterator[tuple[ProcessInfo | None, ProcessInfo]]":
            data : "RawProcessInfo"
            raw_process_info = None
            for data in self.__data["behavior"]["processes"]:
                if data["pid"] == p["pid"] and data["first_seen"] == p["first_seen"]:
                    raw_process_info = data
                    break
            if raw_process_info is None:
                return
            threads = thread_info_iterator(raw_process_info)
            process_info = CuckooParser.__ProcessInfo(
                p["pid"],
                p["first_seen"],
                max((t.stop for t in threads), default=float("inf")),
                threads,
                p["command_line"],
                CuckooParser.__path_factory(raw_process_info["process_path"]),
                tuple(CuckooParser.__ImportInfo(CuckooParser.__path_factory(i["filepath"]), i["imgsize"]) for i in raw_process_info["modules"])
            )
            yield (parent, process_info)
            for pi in p["children"]:
                yield from explore_process_tree(pi, process_info)

        if not self.__execution_tree:
            process_tree : "list[ProcessTree]" = self.__data["behavior"]["processtree"].copy()
            self.__execution_tree.extend((p1, p2) for p in process_tree for p1, p2 in explore_process_tree(p))
        
        yield from self.__execution_tree

    def machines(self) -> Iterable[MachineInfo]:
        if self.__machines is not None:
            return self.__machines
        hosts : set[str] = set()
        if "hosts" in self.__data["network"] and isinstance(self.__data["network"]["hosts"], list):
            hosts = set(self.__data["network"]["hosts"])
        domains : dict[str, str] = {data["ip"] : data["domain"] for data in self.__data["network"].get("domains", [])}
        hosts.difference_update(domains)
        machines = []
        for add, domain in domains.items():
            machines.append(MachineInfo(add, "", domain))
        machines.extend(MachineInfo(add, "", "") for add in hosts)
        self.__machines = tuple(machines)
        return self.__machines
    
    def host(self) -> MachineInfo:
        if self.__host is not None:
            return self.__host
        host_ip = ""
        if "dns_servers" in self.__data["network"] and "udp" in self.__data["network"]:
            for dns_ip in self.__data["network"]["dns_servers"]:
                for data in self.__data["network"]["udp"]:
                    if data["dst"] == dns_ip:
                        host_ip = data["src"]
                        break
                if host_ip:
                    break
        host_ip = host_ip or "127.0.0.1"
        domain = "localhost" if host_ip == "127.0.0.1" else ""
        hostname = ""
        for parent, p in self.process_tree_iterator():
            for t in p.threads:
                for api in t.calls:
                    if api.API in ("GetComputerNameW", "GetComputerNameA") and (name := api.arguments["computer_name"]):
                        hostname = name
                        break
                if hostname:
                    break
            if hostname:
                    break
        else:
            hostname = "host"
        self.__host = MachineInfo(host_ip, hostname, domain)
        return self.__host

    def sample_file_path(self) -> PurePath:
        import re
        from ...utils import path_factory
        expr1 = re.compile(r"^\d*-\d*-\d* \d*:\d*:\d*,\d* \[lib\.api\.process\] INFO: Successfully executed process from path (.+?) with arguments (.+) and pid \d+\n$")
        expr2 = re.compile(r"^\d*-\d*-\d* \d*:\d*:\d*,\d* \[lib\.api\.process\] ERROR: Failed to execute process from path (.+?) with arguments (.+) \(Error: Command (.+) returned non-zero exit status \d+\)\n$")
        line : str
        for line in self.__data["debug"]["log"]:
            if match := expr1.fullmatch(line):
                command_line : list[str] = [eval(match.group(1))] + (eval(match.group(2)) or [])
                break
            if match := expr2.fullmatch(line):
                command_line : list[str] = [eval(match.group(1))] + (eval(match.group(2)) or [])
                break
        else:
            raise ValueError(f"Could not find the log that signals the execution of the sample process in sample '{self.__path}'")
        file_name : str = self.__data["target"]["file"]["name"]
        expr3 = re.compile(r"^(.*),.*?$")       # Sometimes, its in the form <path,something else>
        for param in command_line:
            try:
                p = path_factory(param)
                if p.name == file_name or p.stem == file_name:
                    return p
                if (match := expr3.fullmatch(param)):
                    p = path_factory(match.group(1))
                    if p.name == file_name or p.stem == file_name:      # p.stem because an extension might have been added
                        return p
            except:
                pass
        raise ValueError(f"Could not find the sample file path in the sample process command line in sample '{self.__path}'")
    
    def platform(self) -> Literal['Windows', 'Unix']:
        return self.__data["info"]["platform"].title()