"""
iogp.gui: GUI wrappers and helper functions.

Author: Vlad Topan (vtopan/gmail)
"""
try:
    import PySide6
    from .qt import *   # noqa
    qt = True
except ImportError:
    qt = False
