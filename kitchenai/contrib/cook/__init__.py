from .cook import Cook
def load_ipython_extension(ipython):
    ipython.register_magics(Cook)

    