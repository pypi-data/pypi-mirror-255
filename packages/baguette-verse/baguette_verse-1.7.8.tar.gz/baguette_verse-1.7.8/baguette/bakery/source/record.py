from typing import Any, Dict, Iterable, Union
from Viper.frozendict import frozendict





class Record(frozendict[str, int | float | bool | bytes | str]):

    """
    A subclass of frozendict to hold key-values informations with str keys.
    They can be used with attributes too.
    """

    def __getitem__(self, k: str) -> int | float | bool | bytes | str:
        if not isinstance(k, str):
            raise TypeError(f"Record keys must be str, not '{type(k).__name__}'")
        return super().__getitem__(k)
    
    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError as e:
            try:
                return self[name]
            except KeyError:
                raise e
    
    def __delattr__(self, name: str) -> None:
        if name in super().__getattribute__("__dict__"):
            raise ValueError("Cannot delete attribute '{}' for this object.".format(name))
        try:
            self.pop(name)
        except KeyError as e:
            raise AttributeError(f"record object has no attribute '{name}'")
    
    def __dir__(self) -> list[str]:
        return list(super().__dir__()) + list(self.keys())

    



del Any, Dict, Iterable, Union, frozendict