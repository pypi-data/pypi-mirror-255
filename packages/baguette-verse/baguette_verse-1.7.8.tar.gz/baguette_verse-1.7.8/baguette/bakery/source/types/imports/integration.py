"""
This module contains integration protocols for this behavioral package.
"""

from .....logger import logger
from ...utils import chrono
from ..filesystem.integration import NewFile
from . import entities, relations

__all__ = []





logger.info("Loading integrations from {} library.".format(__name__.rpartition(".")[0].rpartition(".")[2]))

@chrono
def link(e : NewFile):
    from .entities import Import
    from .relations import IsFile
    if e.file.path.suffix.lower().endswith(".dll"):
        for i in Import:
            if e.file.path == i.path:
                break
        else:
            i = Import(path = e.file.path)
        IsFile(i, e.file)

NewFile.add_callback(link)





del NewFile, chrono, entities, link, logger, relations