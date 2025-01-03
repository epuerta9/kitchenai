import multiprocessing
import platform

from .__version__ import __version__

if platform.system() == "Darwin":
    multiprocessing.set_start_method("fork", force=True)

