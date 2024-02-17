"""
This module contains all the functions that the tutorial will call for all steps.
"""

import argparse
import shutil
import textwrap
from pathlib import Path

from .utils import (data_filesystem, extract_subfolder, get_state, next_state,
                    set_state, states)


def clean_print(text : str):
    w, h = shutil.get_terminal_size()
    for line in text.splitlines():
        print("\n".join(textwrap.wrap(line, w)))


def help():
    clean_print(
"""Throughout this tutorial, you can use:
- 'baguette.tutorial' to move to the next step,
- 'baguette.tutorial.reset' to restart the tutorial, 
- 'baguette.tutorial.status' to know the progress of the tutorial,
- 'baguette.tutorial.help get see this message.
""")


def start():

    match get_state():

        case "not started":
            clean_print("""Welcome to the BAGUETTE tutorial. You will learn how to use BAGUETTE from start to end (without the details).\n
BAGUETTE is a framework to analyze efficiently malware dynamic analysis reports. Indeed, BAGUETTE means Behavioral Analysis Graph Using Execution Traces Towards Explainability.\n""")
            help()
            clean_print("""First you will need a working directory to perform this tutorial. If not already done, create one and continue from this new folder.
To use BAGUETTE, you will first need some report samples. Use 'baguette.tutorial.samples -h' to have some Cuckoo report examples.""")

            next_state("not started")

        case "baking":
            baguette_folder = Path("./Baguette")
            clean_print("Checking the BAGUETTEs you made.")

            def check(bpath : Path) -> bool:
                if not bpath.is_dir():
                    return False
                n = 0
                for p in bpath.iterdir():
                    if p.suffix == ".bag":
                        n += 1
                return bool(n)

            try:
                if not check(baguette_folder):
                    clean_print("I could not find the path in which you made your BAGUETTEs. Where is the folder that contains the '.bag' folders?")
                    n = 0
                    while not check(baguette_folder) and n < 3:
                        n += 1
                        path = input("> ")
                        try:
                            baguette_folder = Path(path)
                        except:
                            clean_print("That is not a valid path...Try again")
                            continue
                        if not check(baguette_folder):
                            clean_print("That is not an existing folder or it does not contain '.bag' folders...Try again")
                    if not check(baguette_folder):
                        clean_print("Look into your file system or restart the tutorial to get some BAGUETTEs!")
                        exit(1)
            except KeyboardInterrupt:
                clean_print("Exiting.")
                exit(1)

            baguettes = list(baguette_folder.glob('*.bag/baguette.pyt'))
            if not baguettes:
                clean_print("I could not find any 'baguette.pyt' file in your BAGUETTE folders. What did you do? Start over!")
            
            clean_print("""
In each '.bag' folder (if you did change special outputs), you should find:
- the index, which is a pickle of a baguette rack (look at 'help(baguette.rack)'), located in the 'index.pyt' file. It contains the metadata of the BAGUETTE.
- the BAGUETTE itself, also a pickle (look at 'help(baguette.bakery.source.graph)'), located in the 'baguette.pyt' file,
- the render of the BAGUETTE, saved using the GEXF format, located in the 'visual.gexf' file. It is made to be used with Gephi (https://gephi.org/) for visualizing the BAGUETTE.
""")

            chosen_baguette = str(baguettes[0]).replace("\\", "/")
            clean_print(f"""
You can now use Gephi to visualize the BAGUETTEs (if it looks a bit messy, have a look at the 'filters' parameter of the 'bake' command using 'bake -h'), or if you prefer you can dissect a BAGUETTE by hand in an interactive interpreter:
To do that, you just have to launch Python, import pickle, and load a 'baguette.pyt' file:
>>> from pickle import load
>>> bag = load(open('{chosen_baguette}', 'rb'))
>>> help(bag)

Good luck! And use 'baguette.tutorial' to learn about toasting!""")

            next_state("baking")

        case "baked":

            clean_print("""Now that you have baked some BAGUETTEs, it is time to learn about MetaGraphs!

Since BAGUETTE has a well-defined graph type structure, you can use it to define patterns.
Put simply, MetaGraphs are pattern graphs. Indeed, they are made of MetaVertices, MetaEdges and MetaArrows, which are just like normal Vertices, Edges and Arrows, except that they allow you to put constrains on types to match real vertices, edges or arrows.

For example, 'MetaVertex[File]' would mean 'Match a vertex which type is \"File\"'.
If you have two MetaVertices MV1 and MV2, then 'MetaArrow(MV1, MV2)[HasChildProcess]' would mean 'Match an arrow between the two vertices you already matched for MV1 and MV2, which type should be \"HasChildProcess\"'.

With such a syntax, you can build MetaGraphs using the 'metalib'. It is a script that can be launched without parameters which will start a Python interactive prompt with the environment necessary to work on MetaGraphs. Use 'dir()' to list all the resources available in the environment and 'help(resource)' to learn more about any of those.

In the metalib, we could declare a simple MetaGraph using a few commands:
>>> MG = MetaGraph()
>>> MG.File = MetaVertex[filesystem.File]
>>> MG.Directory = MetaVertex[filesystem.Directory]
>>> MG.Contains = MetaEdge(MG.Directory, MG.File)[filesystem.contains]
>>> save(MG, "dile_in_directory")

Note that in BAGUETTE, all the Vertex, Edge and Arrow subclasses are organized in behavioral packages, such as 'filesystem'. Others can be listed with 'behavioral_packages()'.
Remember, all the information you want can be found using Python 'dir' function (to enumerate your environment) and 'help' to find information about the available resources.

For this step of the tutorial, launch the metalib using the command 'metalib' and create a metagraph of your choice and save it under the name you want.""")

            next_state("baked")

        case "metalib":

            clean_print("You should now have created at least one MetaGraph. Checking...")

            from ..croutons.metalib.utils import entries, load
            
            if not entries():
                clean_print("I could not find any MetaGraph in the metalib! Did you save your MetaGraph before leaving? COme back when you see your MetaGraph when using 'entries()' in the metalib.")
                exit(1)
            
            if len(entries()) == 1:
                clean_print(f"I found a MetaGraph named '{entries()[0]}'.")
                chosen_metagraph = entries()[0]
            
            elif len(entries()) < 10:
                clean_print("I found multiple MetaGraphs. Which want do you want to use?")
                choices = {letter : name for letter, name in zip("abcdefghij", entries())}
                for l, n in choices.items():
                    clean_print(f"\t{l}) '{n}'")
                try:
                    c = input("Write the letter of your choice > ")
                    n = 0
                    while c not in choices and n < 3:
                        clean_print(f"Could not understand your choice : '{c}'. Try again:")
                        n += 1
                        c = input("Write the letter of your choice > ")
                    if c not in choices:
                        clean_print("Could not get a valid input. Giving up.")
                        exit(1)
                except KeyboardInterrupt:
                    clean_print("Exiting.")
                    exit(1)
                
                chosen_metagraph = choices[c]
                clean_print(f"You've chosen the MetaGraph '{chosen_metagraph}'. Loading it...")
            
            else:
                clean_print("There are many MetaGraphs!")
                try:
                    c = input("Write the name of your MetaGraph > ")
                    n = 0
                    while c not in entries() and n < 3:
                        clean_print(f"Could not find your choice : '{c}'. Try again:")
                        n += 1
                        c = input("Write the name of your MetaGraph > ")
                    if c not in entries():
                        clean_print("Could not get a valid input. Giving up.")
                        exit(1)
                except KeyboardInterrupt:
                    clean_print("Exiting.")
                    exit(1)

                chosen_metagraph = c
                clean_print(f"You've chosen the MetaGraph '{chosen_metagraph}'. Loading it...")
            
            MG = load(chosen_metagraph)

            if MG.n == 0:
                clean_print("That's lazy. You made an empty MetaGraph. It won't do much...")
            elif MG.n == 1 and MG.m == 0:
                clean_print("That's lazy. You made the most minimalistic MetaGraph...")
            elif MG.n < 3:
                clean_print(f"Ok, nice MetaGraph. Got {MG.n} vertice{'s' if MG.n > 1 else ''} and {MG.m} edge{'s' if MG.m > 1 else ''}/arrow{'s' if MG.m > 1 else ''}.")
            else:
                clean_print(f"That's a big MetaGraph! Got {MG.n} vertice{'s' if MG.n > 1 else ''} and {MG.m} edge{'s' if MG.m > 1 else ''}/arrow{'s' if MG.m > 1 else ''}!")
            
            clean_print(f"""
To search for matches of this MetaGraph in the BAGUETTEs you made, you need to use 'toast'.
To learn how to use all the options of 'toast', type 'toast -h'.
For now, you can use :
$ toast <your BAGUETTE folder> --pattern '{chosen_metagraph}' --paint red
This command line will search for matches of your MetaGraph '{chosen_metagraph}' and paint them red in the 'visual.gexf' files.""")

            next_state("metalib")

        case "toasting":

            clean_print("Examining your toasts...")

            from pickle import load

            from ..bakery.source.graph import Graph

            baguette_folder = Path("./Baguette")

            def check(bpath : Path) -> bool:
                if not bpath.is_dir():
                    return False
                n = 0
                for p in bpath.iterdir():
                    if p.suffix == ".bag":
                        n += 1
                return bool(n)

            try:
                if not check(baguette_folder):
                    clean_print("I could not find the path in which you made your BAGUETTEs. Where is the folder that contains the '.bag' folders?")
                    n = 0
                    while not check(baguette_folder) and n < 3:
                        n += 1
                        path = input("> ")
                        try:
                            baguette_folder = Path(path)
                        except:
                            clean_print("That is not a valid path...Try again")
                            continue
                        if not check(baguette_folder):
                            clean_print("That is not an existing folder or it does not contain '.bag' folders...Try again")
                    if not check(baguette_folder):
                        clean_print("Look into your file system or restart the tutorial to get some BAGUETTEs!")
                        exit(1)
            except KeyboardInterrupt:
                clean_print("Exiting.")
                exit(1)

            toasts = list(baguette_folder.glob("*.bag/extracted.pyt"))
            if not toasts:
                clean_print("I could not find any toasts. Did the 'toast' command run well?")
                exit(1)
            
            empty_found = False
            interesting_found = False
            for t_path in toasts:
                with t_path.open("rb") as tf:
                    toast : dict[str, list[Graph]] = load(tf)
                    if not isinstance(toast, dict) or any(not isinstance(si, str) for si in toast) or any(not isinstance(li, list) for li in toast.values()) or any(not isinstance(gj, Graph) for li in toast.values() for gj in li):
                        clean_print(f"The file at '{t_path}' is not the toast I expected to find. Actually, it's not even a toast...")
                        exit(1)
                    if not toast and not empty_found:
                        empty_found = True
                        clean_print(f"\nThe MetaGraphs you defined did not have any match in the BAGUETTE '{t_path.parent}'. That means the corresponding behavioral patterns are not relevant for this malware sample.")
                    if toast and not interesting_found:
                        interesting_found = True
                        clean_print(f"\nThe BAGUETTE at '{t_path.parent}' had at least one match. To be more precise, it had matches for the following MetaGraph{('s' if len(toast) > 1 else '')}:")
                        for name, li in toast.items():
                            clean_print(f"\t - for MetaGraph '{name}' : {len(li)} matches.")
                        clean_print(f"This means the MetaGraph{('s' if len(toast) > 1 else '')} you match relevent behavior for this sample.")
                    if interesting_found and empty_found:
                        break

            tutorial_path = str(Path(__file__).resolve()).replace("\\", "/")
            
            clean_print(f"""
You now know how to use the basic functionalities of BAGUETTE.
To learn further, you will need to dive into the very dense documentation of BAGUETTE. To do so, simply use '-h/--help' on command line tools or use the 'help()' function in an interactive Python interpreter on any class/module/package of BAGUETTE. You could look at some examples of interactive use of BAGUETTE code using an adequate IDE for example on this tutorial script file : '{tutorial_path}'.

Bon voyage!""")

            next_state("toasting")

        case "finished":

            clean_print("That's it! You completed the tutorial! Move on now!")

        case x:

            if x not in states():
                clean_print("How did you get there? You broke the tutorial. Use 'baguette.tutorial.reset' now!")
            else:
                status()

def reset():
    clean_print("Resetting BAGUETTE tutorial.")
    set_state("not started")


def status():
    clean_print(f"Tutorial is currently at step : '{get_state()}' : {states()[get_state()]}")


def copy_reports():

    parser = argparse.ArgumentParser("baguette.tutorial.samples", description="This script will copy report examples (BAGUETTE input files) to the given destination folder.")

    parser.add_argument("destination", type=Path, default=Path("."), nargs="?", help="The path to the destination folder in which to copy report folders. Defaults to '.'.")

    args = parser.parse_args()

    if get_state() != "fetching samples":
        clean_print("Warning : fetching Cuckoo report samples in the wrong step of tutorial.")

    pth : Path = args.destination

    if pth.exists() and not pth.is_dir():
        parser.error("given destination path exists and is not a directory.")
    pth.mkdir(parents=True, exist_ok=True)

    reports_dir = data_filesystem / "reports"
    if not reports_dir.exists():
        raise FileNotFoundError("Could not find the report folder in the data archive! Check your BAGUETTE installation.")
    if not reports_dir.is_dir():
        raise FileExistsError("Report folder is not a folder in the data archive! Check you BAGUETTE installation.")

    dirs = list(extract_subfolder(reports_dir, pth))

    if pth.resolve() == Path.cwd():
        clean_print("Playground dataset available in current folder.")
    else:
        clean_print(f"Playground dataset available in '{pth}'")

    clean_print("""
The next step is to bake these reports into BAGUETTES. To do so, use the 'bake' command.
You can use 'bake -h' to learn ALL the options of bake.""")

    report_folders = {p.parent for p in dirs if p.is_file()}

    if not report_folders:
        clean_print("Could not find the extracted report folders...")
        exit(1)

    clean_print(f"""
For example, to bake the newly made reports, use:
$ bake {' '.join(str(pi) for pi in report_folders)} -o ./Baguette""")

    next_state("fetching samples")