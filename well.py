#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines intervals and rock for holding lithologies.

:copyright: 2015 Agile Geoscience
:license: Apache 2.0
"""

import las


class WellError(Exception):
    pass


class Well(las.LASReader):
    """
    Well contains everything about the well. It inherits from
    las.LASReader.

    For example, well will contain header fields, curves, and
    other data from the 'basic' LAS file.

    We will then read supplementary LAS files, and/or maybe CSV
    data, into one main other attribute of Well: the striplog.
    """
    def __init__(self, f, null_subs=None, unknown_as_other=False):

        # First generate the parent object
        super(Well, self).__init__(f, null_subs, unknown_as_other)

        # Now add the new stuff
        pass
