#!/usr/bin/env python
# -*- coding: utf 8 -*-
"""
==================
striplog
==================
"""
from .lexicon import Lexicon
from .component import Component
from .legend import Decor, Legend
from .position import Position
from .interval import Interval
from .striplog import Striplog

__all__ = ['Lexicon',
           'Component',
           'Decor',
           'Legend',
           'Position',
           'Interval',
           'Striplog']


__version__ = None

try:
    from ._version import __version__
except ImportError:
    pass

__version__ = __version__ or "unknown"
