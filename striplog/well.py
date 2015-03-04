#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines intervals and rock for holding lithologies.

:copyright: 2015 Agile Geoscience
:license: Apache 2.0
"""
import csv

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

    def __get_curve_params(self, abbrev, fname):
        """
        Returns a dictionary of petrophysical parameters for
        plotting purposes.
        """
        params = {'acronym': abbrev}
        with open(fname, 'rU') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['acronymn'] == abbrev:
                    params['track'] = int(row['track'])
                    params['units'] = row['units']
                    params['xleft'] = float(row['xleft'])
                    params['xright'] = float(row['xright'])
                    params['logarithmic'] = row['logarithmic']
                    params['hexcolor'] = row['hexcolor']
                    params['fill_left_cond'] = bool(row['fill_left_cond'])
                    params['fill_left'] = row['fill_left']
                    params['fill_right_cond'] = bool(row['fill_right_cond'])
                    params['fill_right'] = row['fill_right']
                    params['xticks'] = row['xticks'].split(',')
        return params

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
