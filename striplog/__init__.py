#!/usr/bin/env python
# -*- coding: utf 8 -*-
"""
==================
striplog
==================
"""
from .legend import Decor, Legend
from .interval import Interval
from .component import Component
from .striplog import Striplog
from .lexicon import Lexicon

__all__ = ['Lexicon',
           'Component',
           'Decor',
           'Legend',
           'Interval',
           'Striplog']


__version__ = "unknown"
try:
    from ._version import __version__
except ImportError:
    pass
