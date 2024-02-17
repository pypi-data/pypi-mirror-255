"""
This module adds some useful tools for parsers, especially for translating API calls.
"""

from collections.abc import Iterable
from pathlib import Path
from typing import Any, TYPE_CHECKING
if TYPE_CHECKING:
    from .abc import CallInfo

__all__ = ["Translator"]





class Translator:

    """
    A Translator is used to translate API call registered from a given source into a BAGUETTE compatible version.
    The most important part of this process is translating API call parameter names.
    """

    import json as __json
    from pathlib import Path as __Path



    class StrDict(dict[str, str]):

        """
        A subclass of dict that only allows str keys and values.
        """

        def __init__(self, iterable = (), **kwargs):
            super().__init__(iterable, **kwargs)
            for k, v in self.items():
                if not isinstance(k, str):
                    raise TypeError(f"Expected str keys, got a '{type(k).__name__}'")
                if not isinstance(v, str):
                    raise TypeError(f"Expected str values, got a '{type(v).__name__}'")
                
        def __setitem__(self, k: str, v: str) -> None:
            if not isinstance(k, str):
                raise TypeError(f"Expected str keys, got a '{type(k).__name__}'")
            if not isinstance(v, str):
                raise TypeError(f"Expected str values, got a '{type(v).__name__}'")
            return super().__setitem__(k, v)
        
        def get(self, k : str, default : str = "") -> str:
            if not isinstance(k, str):
                raise TypeError(f"Expected str keys, got a '{type(k).__name__}'")
            if not isinstance(default, str):
                raise TypeError(f"Expected str keys, got a '{type(default).__name__}'")
            return super().get(k, default)
        
        def setdefault(self, k : str, default : str = "") -> str:
            if not isinstance(k, str):
                raise TypeError(f"Expected str keys, got a '{type(k).__name__}'")
            if not isinstance(default, str):
                raise TypeError(f"Expected str keys, got a '{type(default).__name__}'")
            return super().setdefault(k, default)
        
        def copy(self):
            return Translator.StrDict(self)
        
        def update(self, mapping : dict[str, str], **kwargs : str):
            mapping = Translator.StrDict(mapping) | Translator.StrDict(kwargs)
            super().update(mapping)
        
        @classmethod
        def fromkeys(cls, keys : Iterable[str], value : str = ""):
            return cls((k, value) for k in keys)



    class CallTranslation:

        """
        A class to handle the translation of a single API call more easily.
        """

        def __init__(self, translator : "Translator", name : str, argument_table : "Translator.StrDict", flag_table : "Translator.StrDict") -> None:
            self.__translator = translator
            self.__name = name
            self.__argument_table = argument_table
            self.__flag_table = flag_table

        def __str__(self) -> str:
            return f"<{self.name} translation: args[{', '.join(f'{k} -> {v}' for k, v in self.args.items())}] flags[{', '.join(f'{k} -> {v}' for k, v in self.flags.items())}]>"

        @property
        def name(self) -> str:
            """
            The name of this API call's translation.
            """
            return self.__name
        
        @property
        def translator(self) -> "Translator":
            """
            The Translator this translation is part of.
            """
            return self.__translator
        
        @property
        def argument_codex(self) -> "Translator.StrDict":
            """
            The translation table for this call's argument names.
            """
            return self.__argument_table
        
        @argument_codex.setter
        def argument_codex(self, codex : dict[str, str]):
            if isinstance(codex, dict):
                try:
                    codex = Translator.StrDict(codex)
                except:
                    raise TypeError("Expected dict with str keys and str values")
            if not isinstance(codex, Translator.StrDict):
                raise TypeError(f"Expected dict, got '{type(codex).__name__}'")
            self.__argument_table.clear()
            self.__argument_table.update(codex)

        @argument_codex.deleter
        def argument_codex(self):
            self.__argument_table.clear()

        arguments = args = argument_codex

        @property
        def flag_codex(self) -> "Translator.StrDict":
            """
            The translation table for this call's flag names.
            """
            return self.__flag_table
        
        @flag_codex.setter
        def flag_codex(self, codex : dict[str, str]):
            if isinstance(codex, dict):
                try:
                    codex = Translator.StrDict(codex)
                except:
                    raise TypeError("Expected dict with str keys and str values")
            if not isinstance(codex, Translator.StrDict):
                raise TypeError(f"Expected dict, got '{type(codex).__name__}'")
            self.__flag_table.clear()
            self.__flag_table.update(codex)

        @flag_codex.deleter
        def flag_codex(self):
            self.__flag_table.clear()

        flags = flag_codex


    @staticmethod
    def __pickle_names__():
        return {
            f"_{Translator.__name__}__original_names" : "Names",
            f"_{Translator.__name__}__argument_translation_table" : "Argument Translations",
            f"_{Translator.__name__}__flags_translation_table" : "Flags Translations"
        }

    def __init__(self) -> None:
        self.__original_names : "dict[str, str]" = {}
        self.__argument_translation_table : "dict[str, Translator.StrDict]" = {}
        self.__flags_translation_table : "dict[str, Translator.StrDict]" = {}
    
    def export_to_file(self, path : Path | str):
        """
        Exports the Translator to the given file path as a JSON.
        """
        if isinstance(path, str):
            try:
                path = Translator.__Path(path)
            except:
                pass
        if not isinstance(path, Translator.__Path):
            raise TypeError(f"Expected Path, got '{type(path).__name__}'")
        with path.open("w") as file:
            pickle_names = self.__pickle_names__()
            Translator.__json.dump({pickle_names[name] : value for name, value in self.__dict__.items()}, file, indent = "\t")
        
    @staticmethod
    def import_from_file(path : Path | str) -> "Translator":
        """
        Returns a Translator built from the given JSON file.
        """
        if isinstance(path, str):
            try:
                path = Translator.__Path(path)
            except:
                pass
        if not isinstance(path, Translator.__Path):
            raise TypeError(f"Expected Path, got '{type(path).__name__}'")
        with path.open("r") as file:
            try:
                self = Translator()
                pickle_names = {a : b for b, a in self.__pickle_names__().items()}
                self.__dict__ = {pickle_names[name] : value for name, value in Translator.__json.load(file).items()}
            except Translator.__json.JSONDecodeError:
                raise ValueError(f"Given path is not a JSON file or is corrupted: '{path}'")
        return self
    
    @property
    def names(self) -> list[str]:
        """
        Returns the list of API call names translated by this Translator.
        """
        return list(self.__original_names.values())
    
    def __getitem__(self, name : str) -> "Translator.CallTranslation":
        """
        Implements self[name]. Returns the translation of the call with the given name.
        """
        if not isinstance(name, str):
            raise TypeError(f"Expected str, got '{type(name).__name__}'")
        return Translator.CallTranslation(self, self.__original_names.setdefault(name.lower(), name), self.__argument_translation_table.setdefault(name.lower(), Translator.StrDict()), self.__flags_translation_table.setdefault(name.lower(), Translator.StrDict()))
    
    def __contains__(self, name : str) -> bool:
        """
        Implements name in self.
        """
        if not isinstance(name, str):
            raise TypeError(f"Expected str, got '{type(name).__name__}'")
        return name.lower() in self.__original_names

    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError:
            return self[name]
        
    def __dir__(self) -> list[str]:
        return list(super().__dir__()) + self.names
    
    def translate(self, c : "CallInfo") -> "CallInfo":
        """
        Translates the given API call. Modifies the CallInfo object directly and returns it.
        """
        if c.API in self:
            translation = self[c.API]
            c.arguments = {(translation.args[name] if name in translation.args else name) : value for name, value in c.arguments.items()}
            c.flags = {(translation.flags[name] if name in translation.flags else name) : value for name, value in c.flags.items()}
        return c




del Iterable, Path, Any