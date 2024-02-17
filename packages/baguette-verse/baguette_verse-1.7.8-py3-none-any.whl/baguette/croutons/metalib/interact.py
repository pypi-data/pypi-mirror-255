"""
This module can be launched to run an interactive session to work with MetaGraphs.
"""

import logging

from ...logger import set_level

set_level(logging.WARNING)
from ..source.evaluator import Evaluator
from .utils import *

import_env(globals())

env = globals().copy()
env.pop("import_env")

__all__ = ["main"]





def main():
    from Viper.interactive import InteractiveInterpreter
    InteractiveInterpreter(env).interact("MetaLib interactive console.\nUse save(MG, name) and load(name) to save and load MetaGraphs.\nUse entries() to get a list of all MetaGraphs available in the library.\nUse remove(name) to delete a MetaGraph from the library.\nAll useful types are loaded, including Graph and MetaGraph related types, as well as Evaluators.")





if __name__ == "__main__":
    main()