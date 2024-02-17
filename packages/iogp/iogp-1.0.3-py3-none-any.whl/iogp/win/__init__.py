"""
OS-specific API.
"""

import platform


if platform.system() == 'Windows':
    from .win import *     # NOQA

