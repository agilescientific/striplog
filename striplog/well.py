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

    If we start using pandas dataframes, this is the place to
    do it.

    Args:
      f (str): The path to an LAS file.
      null_subs (float): Something to substitute for the declared
        null value, which is probably -999.25. Often it's convenient
        to use np.nan.
      unknown_as_other (bool): Whether you'd like to load unknown
        sections as plain text blocks. A hack to cope with LAS3 files
        without having to handle arbitrary sections.
    """
    def __init__(self, f, null_subs=None, unknown_as_other=False):

        # First generate the parent object.
        super(Well, self).__init__(f, null_subs, unknown_as_other)

        # Add an empty striplog dict for later.
        self.striplog = {}

    # __repr__, __str__, etc, will come from LASReader

    def add_striplog(self, striplog, name):
        """
        Add a striplog to the well object. Returns nothing.

        Args:
          striplog (Striplog): A striplog object.
          name (str): A name for the log, e.g. 'cuttings', or 'Smith 2012'
        """
        self.striplog[name] = striplog

    def to_las(self):
        """
        Save this well as an LAS 3 file.
        """
        pass

    def plot(self):
        """
        Plot a simple representation of the well.
        """
        pass
