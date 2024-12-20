from .notebooks import NotebookMagics
def load_ipython_extension(ipython):
    ipython.register_magics(NotebookMagics)

    