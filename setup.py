from distutils.core import setup
import py2exe

opts = {
    "py2exe": {
        "ascii": True,
        "compressed": True
    }
}

setup(options = opts, console=['streaming.py'])