"""
This is just an entry point of BAGUETTE to redirect the user.
"""





def clean_print(text : str):
    import shutil, textwrap
    w, h = shutil.get_terminal_size()
    for line in text.splitlines():
        print("\n".join(textwrap.wrap(line, w)))

def main():
    clean_print("""Bonjour!
Welcome to the Baguette-Verse!
To use Baguette, you have multiple choices.

If you have some ideas about what is Baguette, you can use the commands:
- baguette.bake (or just bake) to bake BAGUETTEs.
- baguette.metalib (or just metalib) to enter the metalib, create and manage MetaGraphs.
- baguette.toast (or just toast) to toast existing BAGUETTEs.""")
    
    from .tutorial.utils import get_state
    if get_state() == "not started":
        clean_print("""
If you don't know how to use Baguette yet (or don't know what a BAGUETTE is), use 'baguette.tutorial'.""")





if __name__ == "__main__":
    main()