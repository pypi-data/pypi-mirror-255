"""
This script will copy the content of reports.zip into the given destination folder.
(Archive's password is b"infected")
"""

from typing import Iterator
import zipfile
from pathlib import Path

__all__ = ["data_file", "data_filesystem", "extract_subfolder", "states", "get_state", "set_state", "warn_wrong_state", "next_state"]





data_file = zipfile.ZipFile(Path(__file__).parent / "data.zip")
data_file.setpassword(b"infected")

data_filesystem = zipfile.Path(data_file)

def extract_subfolder(source : zipfile.Path, destination : Path) -> Iterator[Path]:
    """
    Uncompresses a zip source folder (path should be relative to the data archive) into the destination folder.
    Returns the number of files extracted.
    """
    from zipfile import Path as ZPath

    if not source.exists():
        raise FileNotFoundError(f"Could not find file '{source}' in data archive")
    if source.is_file():
        raise FileExistsError(f"Member '{source}' is a file in the data archive")
    
    if destination.exists() and not destination.is_dir():
        raise FileExistsError(f"'{destination}' destination folder exists and is not a directory")

    def deep_iter(path : ZPath) -> list[ZPath]:
        if path.is_file():
            return [path]
        elif path.is_dir():
            l = [path]
            for pi in path.iterdir():
                l.extend(deep_iter(pi))
            return l
        else:
            return []
    
    for file_path in deep_iter(source):
        relative = str(file_path)[len(str(source)):]
        dest = destination / relative
        if file_path.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
            yield dest
        elif file_path.is_file():
            dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open("wb") as f:
                f.write(file_path.read_bytes())
            yield dest





# __states should be ordered and describe the tutorial scenario.
__states = {
    "not started" : "The tutorial has not been started yet.",
    "fetching samples" : "The user should use the command line 'baguette.tutorial.samples -h' to get report samples.",
    "baking" : "The user should use 'bake' to start baking BAGUETTEs from the report samples.\nOnce done, the user should use 'baguette.tutorial' for next step.",
    "baked" : "The user has studied the freshly baked BAGUETTEs and is ready to learn about toasting.\nUse 'baguette.tutorial' for next step.",
    "metalib" : "The user should be writting a MetaGraph.\nOnce it has been saved, use 'baguette.tutorial' to continue.",
    "toasting" : "The user should be toasting BAGUETTEs using the newly defined MetaGraph.\nUse 'baguette.tutorial' once done.",
    "finished" : "The user has completed the tutorial.\nUse 'baguette.tutorial.reset' to do it again."
}

def states() -> dict[str, str]:
    """
    Returns the list of possible states of the tutorial.
    """
    return __states.copy()

def get_state() -> str:
    """
    Returns the current state of the tutorial.
    """
    from pathlib import Path
    pth = Path(__file__).parent / "state.txt"
    if not pth.exists():
        return list(__states)[0]
    state = pth.read_text()
    if state not in __states:
        raise RuntimeError(f"Unregistered tutorial state: '{state}'")
    return state

def set_state(state : str):
    """
    Sets the state of the tutorial.
    """
    from pathlib import Path
    pth = Path(__file__).parent / "state.txt"
    if state not in __states:
        raise RuntimeError(f"Unregistered tutorial state: '{state}'")
    pth.write_text(state)

def next_state(state : str) -> bool:
    """
    Moves to next state if the current state is the given state.
    Returns True on success, False otherwise.
    """
    if get_state() == state:
        l = list(__states)
        i = l.index(state)
        n_state = l[(i + 1) % len(l)]
        set_state(n_state)
        return True
    return False

def warn_wrong_state(expected_state : str) -> bool:
    """
    Checks that the tutorial is in the given expected stated. If not, prints a warning about that.
    Returns True of the tutorial is in the right state, False otherwise.
    """
    if get_state() == expected_state:
        return True
    print("error : tutorial already started. Use 'baguette.tutorial.reset' to restart the tutorial.")
    print(f"Tutorial is currently at step : '{get_state()}' : {__states[get_state()]}")
    return False





del zipfile, Path