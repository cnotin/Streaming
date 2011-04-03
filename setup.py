from distutils.core import setup
import py2exe

opts = {
    "py2exe": {
        "ascii": True,
        "compressed": True,
        "optimize":2
    }
}

setup(options = opts, console=['streaming.py'])