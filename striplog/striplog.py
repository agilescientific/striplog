#!/usr/bin/env python
# -*- coding: utf 8 -*-
"""
A striplog is a sequence of intervals.

:copyright: 2015 Agile Geoscience
:license: Apache 2.0
"""
import re
from io import StringIO
import csv
import operator
import warnings
from collections import Counter
from functools import reduce
from copy import deepcopy

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from .interval import Interval, IntervalError
from .component import Component
from .legend import Legend
from . import utils
from . import templates


class StriplogError(Exception):
    """
    Generic error class.
    """
    pass


class Striplog(object):
    """
    A Striplog is a sequence of intervals.

    We will build them from LAS files or CSVs.

    Args:
        list_of_Intervals (list): A list of Interval objects.
        source (str): A source for the data. Default None.
    """
    def __init__(self, list_of_Intervals, source=None, order='auto'):

        if not list_of_Intervals:
            m = "Cannot create an empty Striplog."
            raise StriplogError(m)

        if order.lower()[0] == 'a':  # Auto
            # If bases == tops, then this is a bunch of 'points'.
            if all([iv.base.z == iv.top.z for iv in list_of_Intervals]):
                order = 'none'
                self.order = 'none'
            # We will tolerate zero-thickness intervals mixed in.
            elif all([iv.base.z >= iv.top.z for iv in list_of_Intervals]):
                order = 'depth'
                self.order = 'depth'
            elif all([iv.base.z <= iv.top.z for iv in list_of_Intervals]):
                order = 'elevation'
                self.order = 'elevation'
            else:
                m = "Could not determine order from tops and bases."
                raise StriplogError(m)

        if order.lower()[0] == 'n':
            self.order = 'none'
            # Sanity check
            fail = any([iv.base.z != iv.top.z for iv in list_of_Intervals])
            if fail:
                m = "'None' order specified but tops != bases."
                raise StriplogError(m)
            # Order force
            list_of_Intervals.sort(key=operator.attrgetter('top'))

        elif order.lower()[0] == 'd':
            self.order = 'depth'
            # Sanity check
            fail = any([iv.base.z < iv.top.z for iv in list_of_Intervals])
            if fail:
                m = "Depth order specified but base above top."
                raise StriplogError(m)
            # Order force
            list_of_Intervals.sort(key=operator.attrgetter('top'))

        else:
            self.order = 'elevation'
            fail = any([iv.base.z > iv.top.z for iv in list_of_Intervals])
            if fail:
                m = "Elevation order specified but base above top."
                raise StriplogError(m)
            # Order force
            r = True
            list_of_Intervals.sort(key=operator.attrgetter('top'), reverse=r)

        self.source = source

        self.__list = list_of_Intervals
        self.__index = 0  # Set up iterable.

    def __repr__(self):
        l = len(self.__list)
        details = "start={}, stop={}".format(self.start, self.stop)
        return "Striplog({0} Intervals, {1})".format(l, details)

    def __str__(self):
        s = [str(i) for i in self.__list]
        return '\n'.join(s)

    # Could use collections but doing this with raw magics.
    # Set up Striplog as an array-like iterable.
    def __getitem__(self, key):
        if type(key) is slice:
            i = key.indices(len(self.__list))
            result = [self.__list[n] for n in range(*i)]
            return Striplog(result)
        elif type(key) is list:
            result = []
            for j in key:
                result.append(self.__list[j])
            return Striplog(result)
        else:
            return self.__list[key]

    def __delitem__(self, key):
        if (type(key) is list) or (type(key) is tuple):
            # Have to compute what the indices *will* be as
            # the initial ones are deleted.
            indices = [x-i for i, x in enumerate(key)]
            for k in indices:
                del self.__list[k]
        else:
            del self.__list[key]
        return

    def __insert(self, index, item):
        if isinstance(item, self.__class__):
            # Add them one at a time.
            for i, iv in enumerate(item):
                self.__list.insert(index+i, iv)
        elif isinstance(item, Interval):
            # Add it.
            self.__list.insert(index, item)
            return
        else:
            raise StriplogError("You can only insert striplogs or intervals.")

    def __len__(self):
        return len(self.__list)

    def __setitem__(self, key, value):
        if not key:
            return
        try:
            for i, j in enumerate(key):
                self.__list[j] = value[i]
        except TypeError:
            self.__list[key] = value
        except IndexError:
            raise StriplogError("There must be one Interval for each index.")

    def __iter__(self):
        return iter(self.__list)

    def __next__(self):
        """
        Supports iterable.

        """
        try:
            result = self.__list[self.__index]
        except IndexError:
            self.__index = 0
            raise StopIteration
        self.__index += 1
        return result

    def next(self):
        """
        Retains Python 2 compatibility.
        """
        return self.__next__()

    def __contains__(self, item):
        for r in self.__list:
            if item in r.components:
                return True
        return False

    def __reversed__(self):
        return Striplog(self.__list[::-1])

    def __add__(self, other):
        if isinstance(other, self.__class__):
            result = self.__list + other.__list
            return Striplog(result)
        elif isinstance(other, Interval):
            result = self.__list + [other]
            return Striplog(result)
        else:
            raise StriplogError("You can only add striplogs or intervals.")

    @property
    def start(self):
        if self.order == 'depth':
            return self[0].top.z
        else:
            return self[-1].base.z

    @property
    def stop(self):
        if self.order == 'depth':
            return self[-1].base.z
        else:
            return self[0].top.z

    def __sort(self):
        """
        Sorts into 'natural' order: top-down for depth-ordered
        striplogs; bottom-up for elevation-ordered.

        Sorts in place.
        """
        self.__list.sort(key=operator.attrgetter('top'))
        return

    def __strict(self):
        """
        Checks if striplog is monotonically increasing in depth.

        """
        def conc(a, b):
            return a + b

        # Check boundaries, b
        b = np.array(reduce(conc, [[i.top.z, i.base.z] for i in self]))

        return all(np.diff(b) >= 0)

    @property
    def cum(self):
        """
        Returns the cumulative thickness of all filled intervals.

        It would be nice to use sum() for this (by defining __radd__),
        but I quite like the ability to add striplogs and get a striplog
        and I don't think we can have both, its too confusing.

        Not calling it sum, because that's a keyword.
        """
        total = 0.0
        for i in self:
            total += i.thickness
        return total

    @property
    def mean(self):
        """
        Returns the mean thickness of all filled intervals.
        """
        return self.cum / len(self)

    @property
    def components(self):
        """
        Returns the list of compenents in the striplog.
        """
        return [i[0] for i in self.unique if i[0]]

    @property
    def unique(self):
        """
        Summarize a Striplog with some statistics.
        """
        all_rx = set([iv.primary for iv in self])
        table = {r: 0 for r in all_rx}
        for iv in self:
            table[iv.primary] += iv.thickness

        return sorted(table.items(), key=operator.itemgetter(1), reverse=True)

    @property
    def top(self):
        # For backwards compatibility.
        with warnings.catch_warnings():
            warnings.simplefilter("always")
            w = "Striplog.top is deprecated; please use Striplog.unique"
            warnings.warn(w)
        return self.unique

    @classmethod
    def __loglike_from_image(self, filename, offset):
        """
        Get a log-like stream of RGB values from an image.

        Args:
            filename (str): The filename of a PNG image.

        Returns:
            ndarray: A 2d array (a column of RGB triples) at the specified
            offset.

        TODO:
            Generalize this to extract 'logs' from images in other ways, such
            as giving the mean of a range of pixel columns, or an array of
            columns. See also a similar routine in pythonanywhere/freqbot.
        """
        im = plt.imread(filename)
        col = im.shape[1]/(100./offset)
        return im[:, col, :3]

    @classmethod
    def __tops_from_loglike(self, loglike, offset=0):
        """
        Take a log-like stream of numbers or strings,
        and return two arrays: one of the tops (changes), and one of the
        values from the stream.

        Args:
            loglike (array-like): The input stream of loglike data.
            offset (int): Offset (down) from top at which to get lithology,
                to be sure of getting 'clean' pixels.

        Returns:
            ndarray: Two arrays, tops and values.
        """
        loglike = np.array(loglike)
        all_edges = loglike[1:] == loglike[:-1]
        edges = all_edges[1:] & (all_edges[:-1] == 0)

        tops = np.where(edges)[0] + 1
        tops = np.append(0, tops)

        values = loglike[tops + offset]

        return tops, values

    @classmethod
    def __intervals_from_tops(self, tops, values, basis, components):
        """
        Take a sequence of tops in an arbitrary dimension, and provide a list
        of intervals from which a striplog can be made.
        """
        # Scale tops to actual depths.
        length = float(basis.size)
        start, stop = basis[0], basis[-1]
        tops = [start + (p/(length-1)) * (stop-start) for p in tops]
        bases = tops[1:] + [stop]

        list_of_Intervals = []
        for i, t in enumerate(tops):
            component = deepcopy(components[values[i]])
            interval = Interval(t, bases[i], components=[component])
            list_of_Intervals.append(interval)

        return list_of_Intervals

    @classmethod
    def from_csv(cls, text,
                 lexicon=None,
                 source='CSV',
                 dlm=',',
                 points=False,
                 abbreviations=False,
                 complete=False,
                 order='depth',
                 columns=None,
                 ):
        """
        Convert a CSV string into a striplog. Expects 2 or 3 fields:
            top, description
            OR
            top, base, description

        Args:
            text (str): The input text, given by ``well.other``.
            lexicon (Lexicon): A lexicon, required to extract components.
            source (str): A source. Default: 'CSV'.
            dlm (str): The delimiter, given by ``well.dlm``. Default: ','
            points (bool): Whether to treat as points or as intervals.
            abbreviations (bool): Whether to expand abbreviations in the
                description. Default: False.
            complete (bool): Whether to make 'blank' intervals, or just leave
                gaps. Default: False.
            columns (tuple or list): The names of the columns.

        Returns:
            Striplog: A ``striplog`` object.

        Example:
            # TOP       BOT        LITH
            312.34,   459.61,    Sandstone
            459.71,   589.61,    Limestone
            589.71,   827.50,    Green shale
            827.60,   1010.84,   Fine sandstone

        Todo:
            Automatic abbreviation detection.
        """

        text = re.sub(r'(\n+|\r\n|\r)', '\n', text.strip())

        as_strings = []
        try:
            f = StringIO(text)  # Python 3
        except TypeError:
            f = StringIO(unicode(text))  # Python 2
        reader = csv.reader(f, delimiter=dlm, skipinitialspace=True)
        for row in reader:
            as_strings.append(row)

        if not columns:
            if order[0].lower() == 'e':
                columns = ('base', 'top', 'description')
            else:
                columns = ('top', 'base', 'description')

        result = {k: [] for k in columns}

        # Set the indices for the fields.
        tix = columns.index('top')
        bix = columns.index('base')
        dix = columns.index('description')

        for i, row in enumerate(as_strings):

            # THIS ONLY WORKS FOR MISSING TOPS!
            if len(row) == 2:
                row = [row[0], None, row[1]]

            # TOP
            this_top = float(row[tix])

            # THIS ONLY WORKS FOR MISSING TOPS!
            # BASE
            # Base is null: use next top if this isn't the end.
            if row[1] is None:
                if i < len(as_strings)-1:
                    this_base = float(as_strings[i+1][0])  # Next top.
                else:
                    this_base = this_top + 1  # Default to 1 m thick at end.
            else:
                this_base = float(row[bix])

            # DESCRIPTION
            this_descr = row[dix].strip()

            # Deal with making intervals or points...
            if not points:
                # Insert intervals where needed.
                if complete and (i > 0) and (this_top != result['base'][-1]):
                    result['top'].append(result['base'][-1])
                    result['base'].append(this_top)
                    result['description'].append('')
            else:
                this_base = None  # Gets set to Top in striplog creation

            # ASSIGN
            result['top'].append(this_top)
            result['base'].append(this_base)
            result['description'].append(this_descr)

        # Build the list.
        list_of_Intervals = []
        for i, t in enumerate(result['top']):
            b = result['base'][i]
            d = result['description'][i]
            interval = Interval(t, b, description=d,
                                lexicon=lexicon,
                                abbreviations=abbreviations)
            list_of_Intervals.append(interval)

        return cls(list_of_Intervals, source=source)

    @classmethod
    def from_img(cls, filename, start, stop, legend,
                 source="Image",
                 offset=10,
                 pixel_offset=2,
                 tolerance=0):
        """
        Read an image and generate Striplog.

        Args:
            filename (str): An image file, preferably high-res PNG.
            start (float or int): The depth at the top of the image.
            stop (float or int): The depth at the bottom of the image.
            legend (Legend): A legend to look up the components in.
            source (str): A source for the data. Default: 'Image'.
            offset (Number): The percentage of the way across the image from
                which to extract the pixel column. Default: 10.
            pixel_offset (int): The number of pixels to skip at the top of
                each change in colour. Default: 2.
            tolerance (float): The Euclidean distance between hex colours,
                which has a maximum (black to white) of 441.67 in base 10.
                Default: 0.

        Returns:
            Striplog: The ``striplog`` object.
        """
        rgb = cls.__loglike_from_image(filename, offset)
        loglike = np.array([utils.rgb_to_hex(t) for t in rgb])

        # Get the pixels and colour values at 'tops' (i.e. changes).
        tops, hexes = cls.__tops_from_loglike(loglike,
                                              offset=pixel_offset)
        hexes_reduced = list(set(hexes))

        # Get the components corresponding to the colours.
        components = [legend.get_component(h, tolerance=tolerance)
                      for h in hexes_reduced]

        # Turn them into integers.
        values = [hexes_reduced.index(i) for i in hexes]

        basis = np.linspace(start, stop, loglike.size)

        list_of_Intervals = cls.__intervals_from_tops(tops,
                                                      values,
                                                      basis,
                                                      components)

        return cls(list_of_Intervals, source="Image")

    @classmethod
    def _from_array(cls, a,
                    lexicon=None,
                    source="",
                    points=False,
                    abbreviations=False):
        """
        DEPRECATING

        Turn an array-like into a Striplog. It should have the following
        format (where `base` is optional):

            [(top, base, description),
             (top, base, description),
             ...
             ]

        Args:
            a (array-like): A list of lists or of tuples, or an array.
            lexicon (Lexicon): A language dictionary to extract structured
                objects from the descriptions.
            source (str): The source of the data. Default: ''.
            points (bool): Whether to treat as point data. Default: False.

        Returns:
            Striplog: The ``striplog`` object.
        """

        with warnings.catch_warnings():
            warnings.simplefilter("always")
            w = "from_array() is deprecated."
            warnings.warn(w)

        csv_text = ''
        for interval in a:
            interval = [str(i) for i in interval]
            if (len(interval) < 2) or (len(interval) > 3):
                raise StriplogError('Elements must have 2 or 3 items')
            descr = interval[-1].strip('" ')
            interval[-1] = '"' + descr + '"'
            csv_text += ', '.join(interval) + '\n'

        return cls.from_csv(csv_text,
                            lexicon,
                            source=source,
                            points=points,
                            abbreviations=abbreviations)

    @classmethod
    def from_log(cls, log,
                 cutoff=None,
                 components=None,
                 legend=None,
                 right=False,
                 basis=None,
                 source='Log'):
        """
        Turn a 1D array of integers into a striplog, given a cutoff.

        Args:
            log (array-like): A 1D array or a list of integers.
            cutoff (number or array-like): The log value(s) at which to bin
                the log. Optional. If you don't provide one, 
            components (array-like): A list of components or a legend.
            right (bool): Which side of the cutoff to send things that are
                equal to, i.e. right on, the cutoff.

        Returns:
            Striplog: The `striplog` object.

        TODO:
            Implement the log blocking function in a well-handling library,
            instead of here. Then we can just use from_blocky_log().
        """
        if not components:
            if not legend:
                m = 'You must provide a legend or list of components'
                raise StriplogError(m)

        if legend is not None:
            try:  # To treat it like a legend.
                components = [deepcopy(decor.component) for decor in legend]
            except AttributeError:  # It's just a list of components.
                pass

        if cutoff is not None:

            # First make sure we have enough components.
            try:
                n = len(cutoff)
            except TypeError:
                n = 1
            if len(components) < n+1:
                m = 'For n cutoffs, you need to provide at least'
                m += 'n+1 components.'
                raise StriplogError(m)

            # Digitize.
            try:  # To use cutoff as a list.
                a = np.digitize(log, cutoff, right)
            except ValueError:  # It's just a number.
                a = np.digitize(log, [cutoff], right)

        else:
            a = log

        tops, values = cls.__tops_from_loglike(a)

        if basis is None:
            m = 'You must provide a depth or elevation basis.'
            raise StriplogError(m)

        list_of_Intervals = cls.__intervals_from_tops(tops,
                                                      values,
                                                      basis,
                                                      components)

        return cls(list_of_Intervals, source=source)

    @classmethod
    def from_las3(cls, string, lexicon=None,
                  source="LAS",
                  dlm=',',
                  abbreviations=False):
        """
        Turn LAS3 'lithology' section into a Striplog.

        Args:
            string (str): A section from an LAS3 file.
            lexicon (Lexicon): The language for conversion to components.
            source (str): A source for the data.
            dlm (str): The delimiter.
            abbreviations (bool): Whether to expand abbreviations.

        Returns:
            Striplog: The ``striplog`` object.

        Note:
            Handles multiple 'Data' sections. It would be smarter for it
            to handle one at a time, and to deal with parsing the multiple
            sections in the Well object.

            Does not read an actual LAS file. Use the Well object for that.
        """
        f = re.DOTALL | re.IGNORECASE
        regex = r'\~\w+?_Data.+?\n(.+?)(?:\n\n+|\n*\~|\n*$)'
        pattern = re.compile(regex, flags=f)
        text = pattern.search(string).group(1)

        s = re.search(r'\.(.+?)\: ?.+?source', string)
        if s:
            source = s.group(1).strip()

        return cls.from_csv(text, lexicon,
                            source=source,
                            dlm=dlm,
                            abbreviations=abbreviations)

    # Outputter
    def to_csv(self, use_descriptions=False, dlm=",", header=True):
        """
        Returns a CSV string built from the summaries of the Intervals.

        Args:
            use_descriptions (bool): Whether to use descriptions instead
                of summaries, if available.
            dlm (str): The delimiter.
            header (bool): Whether to form a header row.

        Returns:
            str: A string of comma-separated values.
        """
        data = ''

        if header:
            data += '{0:12s}{1:12s}'.format('Top', 'Base')
            data += '  {0:48s}'.format('Lithology')

        for i in self.__list:
            if use_descriptions and i.description:
                text = i.description
            elif i.primary:
                text = i.primary.summary()
            else:
                text = ''
            data += '{0:9.3f}'.format(i.top.z)
            data += '{0}{1:9.3f}'.format(dlm, i.base.z)
            data += '{0}  {1:48s}'.format(dlm, '"'+text+'"')
            data += '\n'

        return data

    # Outputter
    def to_las3(self, use_descriptions=False, dlm=",", source="Striplog"):
        """
        Returns an LAS 3.0 section string.

        Args:
            use_descriptions (bool): Whether to use descriptions instead
                of summaries, if available.
            dlm (str): The delimiter.
            source (str): The sourse of the data.

        Returns:
            str: A string forming Lithology section of an LAS3 file.
        """
        data = self.to_csv(use_descriptions=use_descriptions,
                           dlm=dlm,
                           header=False)

        return templates.section.format(name='Lithology',
                                        short="LITH",
                                        source=source,
                                        data=data)

    # Outputter
    def to_log(self,
               step=1.0,
               start=None,
               stop=None,
               basis=None,
               field=None,
               field_function=None,
               legend=None,
               legend_field=None,
               match_only=None,
               undefined=0,
               return_meta=False):
        """
        Return a fully sampled log from a striplog. Useful for crossplotting
        with log data, for example.

        Args:
            step (float): The step size. Default: 1.0.
            start (float): The start depth of the new log. You will want to
                match the logs, so use the start depth from the LAS file.
                Default: The basis if provided, else the start of the striplog.
            stop (float): The stop depth of the new log. Use the stop depth
                of the LAS file. Default: The basis if provided, else the stop
                depth of the striplog.
            legend (Legend): If you want the codes to come from a legend,
                provide one. Otherwise the codes come from the log, using
                integers in the order of prevalence. If you use a legend,
                they are assigned in the order of the legend.
            legend_field (str): If you want to get a log representing one of
                the fields in the legend, such as 'width' or 'grainsize'.
            match_only (list): If you only want to match some attributes of
                the Components (e.g. lithology), provide a list of those
                you want to match.
            return_meta (bool): Also return the depth basis (np.linspace),
                and the component table.

        Returns:
            ndarray: Two ndarrays in a tuple, (depth, logdata). Logdata
                has type numpy.int.
        """
        # Make the preparations.
        if basis is not None:
            start, stop = basis[0], basis[-1]
            step = basis[1] - start
        else:
            start = start or self.start
            stop = stop or self.stop
            pts = np.ceil((stop - start)/step) + 1
            basis = np.linspace(start, stop, pts)

        if field:
            result = np.zeros_like(basis)
        else:
            result = np.zeros_like(basis, dtype=np.int)

        if undefined == np.nan:
            result[:] = np.nan

        # Make a look-up table for the log values.
        if legend:
            table = [j.component for j in legend]
        else:
            table = [j[0] for j in self.unique]
        table.insert(0, Component({}))

        start_ix = self.read_at(start, index=True)
        stop_ix = self.read_at(stop, index=True)
        if stop_ix is not None:
            stop_ix += 1

        # Assign the values.
        for i in self[start_ix:stop_ix]:
            c = i.primary
            if match_only:
                c = Component({k: getattr(c, k, None)
                               for k in match_only})

            if legend and legend_field:
                # Use the legend field.
                try:
                    key = legend.getattr(c, legend_field, undefined)
                except ValueError:
                    key = undefined
            elif field:  # Get data directly from that field in the components.
                f = field_function or utils.null
                try:
                    key = f(getattr(c, field, undefined))
                except ValueError:
                    key = undefined
            else:  # Use the lookup table.
                try:
                    key = table.index(c)
                except ValueError:
                    key = undefined

            top_index = np.ceil((max(start, i.top.z)-start)/step)
            base_index = np.ceil((min(stop, i.base.z)-start)/step)

            try:
                result[top_index:base_index+1] = key
            except:  # Have a list or array or something.
                result[top_index:base_index+1] = key[0]

        if return_meta:
            return result, basis, table
        else:
            return result

    def to_flag(self, **kwargs):
        """
        A wrapper for to_log() that returns a boolean array.
        """
        return self.to_log(**kwargs).astype(bool)

    # Outputter
    def plot_axis(self,
                  ax,
                  legend,
                  ladder=False,
                  default_width=1,
                  match_only=None,
                  **kwargs):
        """
        Plotting, but only the Rectangles. You have to set up the figure.
        Returns a matplotlib axis object.

        Args:
            ax (axis): The matplotlib axis to plot into.
            legend (Legend): The Legend to use for colours, etc.
            ladder (bool): Whether to use widths or not. Default False.
            default_width (int): A width for the plot if not using widths.
                Default 1.
            match_only (list): A list of strings matching the attributes you
                want to compare when plotting.
            **kwargs are passed through to matplotlib's `patches.Rectangle`.

        Returns:
            axis: The matplotlib.pyplot axis.
        """
        for i in self.__list:
            origin = (0, i.top.z)
            d = legend.get_decor(i.primary, match_only=match_only)
            thick = i.base.z - i.top.z

            if ladder:
                w = d.width or default_width
                try:
                    w = default_width * w/legend.max_width
                except:
                    w = default_width
            else:
                w = default_width

            # Allow override of lw
            this_patch_kwargs = kwargs.copy()
            lw = this_patch_kwargs.pop('lw', 0)
            ec = this_patch_kwargs.pop('ec', 'k')

            rect = mpl.patches.Rectangle(origin,
                                         w,
                                         thick,
                                         fc=d.colour,
                                         lw=lw,
                                         hatch=d.hatch,
                                         ec=ec,  # edgecolour for hatching
                                         **this_patch_kwargs)
            ax.add_patch(rect)

        return ax

    # Outputter
    def plot(self,
             legend=None,
             width=1.5,
             ladder=False,
             aspect=10,
             ticks=(1, 10),
             match_only=None,
             ax=None,
             return_fig=False,
             **kwargs):
        """
        Hands-free plotting.

        Args:
            legend (Legend): The Legend to use for colours, etc.
            width (int): The width of the plot, in inches. Default 1.
            ladder (bool): Whether to use widths or not. Default False.
            aspect (int): The aspect ratio of the plot. Default 10.
            ticks (int or tuple): The (minor,major) tick interval for depth.
                Only the major interval is labeled. Default (1,10).
            match_only (list): A list of strings matching the attributes you
                want to compare when plotting.
            **kwargs are passed through to matplotlib's `patches.Rectangle`.

        Returns:
            figure: The matplotlib.pyplot figure.
        """
        if not legend:
            # Build a random-coloured legend.
            legend = Legend.random(self.components)

        if ax is None:
            return_ax = False
            fig = plt.figure(figsize=(width, aspect*width))
            ax = fig.add_axes([0.35, 0.05, 0.6, 0.95])
        else:
            return_ax = True

        ax = self.plot_axis(ax=ax,
                            legend=legend,
                            ladder=ladder,
                            default_width=width,
                            match_only=match_only,
                            **kwargs
                            )
        ax.set_xlim([0, width])

        # Rely on interval order.
        lower, upper = self[-1].base.z, self[0].top.z
        rng = abs(upper - lower)

        ax.set_ylim([lower, upper])
        ax.set_xticks([])

        # Make sure ticks is a tuple.
        try:
            ticks = tuple(ticks)
        except TypeError:
            ticks = (1, ticks)

        # Avoid MAXTICKS error.
        while rng/ticks[0] > 1000:
            mi, ma = 10*ticks[0], ticks[1]
            if ma <= mi:
                ma = 10 * mi
            ticks = (mi, ma)

        # Carry on plotting...
        minorLocator = mpl.ticker.MultipleLocator(ticks[0])
        ax.yaxis.set_minor_locator(minorLocator)

        majorLocator = mpl.ticker.MultipleLocator(ticks[1])
        majorFormatter = mpl.ticker.FormatStrFormatter('%d')
        ax.yaxis.set_major_locator(majorLocator)
        ax.yaxis.set_major_formatter(majorFormatter)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.yaxis.set_ticks_position('left')
        ax.get_yaxis().set_tick_params(which='both', direction='out')

        ax.patch.set_alpha(0)

        if return_ax:
            return ax
        elif return_fig:
            return fig
        else:
            return

    def read_at(self, d, index=False):
        """
        Get the index of the interval at a particular 'depth' (though this
            might be an elevation or age or anything.

        Args:
            d (Number): The 'depth' to query.
            index (bool): Whether to return the index instead of the interval.

        Returns:
            Int: The interval, or if index==True the index of the interval, at
                the specified 'depth', or None if the depth is outside the
                striplog's range.
        """
        for i, iv in enumerate(self):
            if iv.spans(d):
                return i if index else iv
        return None

    # For backwards compatibility
    def depth(self, d):
        with warnings.catch_warnings():
            warnings.simplefilter("always")
            w = "depth() is deprecated; please use read_at()"
            warnings.warn(w)
        return self.read_at(d)

    def extract(self, log, basis, name, function=None):
        """
        'Extract' a log into the components of a striplog.

        Args:
            log (array_like). A log or other 1D data.
            basis (array_like). The depths or elevations of the log samples.
            name (str). The name of the attribute to store in the components.
            function (function). A function that takes an array as the only
                input, and returns whatever you want to store in the 'name'
                attribute of the primary component.
        Returns:
            None. The function works on the striplog in place.
        """
        # Build a dict of {index: [log values]} to keep track.
        intervals = {}
        previous_ix = -1
        for i, z in enumerate(basis):
            ix = self.read_at(z, index=True)
            if ix is None:
                continue
            if ix == previous_ix:
                intervals[ix].append(log[i])
            else:
                intervals[ix] = [log[i]]
            previous_ix = ix

        # Set the requested attribute in the primary comp of each interval.
        for ix, data in intervals.items():
            f = function or utils.null
            d = f(np.array(data))
            setattr(self[ix].primary, name, d)

        return None

    def find(self, search_term, index=False):
        """
        Look for a regex expression in the descriptions of the striplog.
        If there's no description, it looks in the summaries.

        If you pass a Component, then it will search the components, not the
        descriptions or summaries.

        Case insensitive.

        Args:
            search_term (string or Component): The thing you want to search
                for. Strings are treated as regular expressions.
        Returns:
            Striplog: A striplog that contains only the 'hit' Intervals.
        """
        hits = []
        for i, iv in enumerate(self):
            try:
                search_text = iv.description or iv.primary.summary()
                pattern = re.compile(search_term, flags=re.IGNORECASE)
                if pattern.search(search_text):
                    hits.append(i)
            except TypeError:
                if search_term in iv.components:
                    hits.append(i)
        if index:
            return hits
        else:
            return self[hits]

    def __find_incongruities(self, op, index):
        """
        Finds gaps and overlaps in a striplog. Private; called by
        find_gaps() and find_overlaps().

        Args:
            op (operator): operator.gt or operator.lt
            index (bool): If True, returns indices of intervals with
            gaps after them.

        Returns:
            Striplog: A striplog of all the gaps. A sort of anti-striplog.

        """
        hits = []
        intervals = []

        if self.order == 'depth':
            one, two = 'base', 'top'
        else:
            one, two = 'top', 'base'

        for i, iv in enumerate(self[:-1]):
            next_iv = self[i+1]
            if op(getattr(iv, one), getattr(next_iv, two)):
                hits.append(i)

                top = getattr(iv, one)
                base = getattr(next_iv, two)
                iv_gap = Interval(top, base)
                intervals.append(iv_gap)

        if index and hits:
            return hits
        elif intervals:
            return Striplog(intervals)
        else:
            return

    def find_overlaps(self, index=False):
        """
        Find overlaps in a striplog.

        Args:
            index (bool): If True, returns indices of intervals with
            gaps after them.

        Returns:
            Striplog: A striplog of all the overlaps as intervals.

        """
        return self.__find_incongruities(op=operator.gt, index=index)

    def find_gaps(self, index=False):
        """
        Finds gaps in a striplog.

        Args:
            index (bool): If True, returns indices of intervals with
            gaps after them.

        Returns:
            Striplog: A striplog of all the gaps. A sort of anti-striplog.

        """
        return self.__find_incongruities(op=operator.lt, index=index)

    def prune(self, limit=None, n=None, percentile=None):
        """
        Remove intervals below a certain limit thickness. In place.

        Args:
            limit (float): Anything thinner than this will be pruned.
            n (int): The n thinnest beds will be pruned.
            percentile (float): The thinnest specified percentile will be
                pruned.
        """
        if not (limit or n or percentile):
            m = "You must provide a limit or n or percentile for pruning."
            raise StriplogError(m)
        if limit:
            prune = [i for i, iv in enumerate(self) if iv.thickness < limit]
        if n:
            prune = self.thinnest(n=n, index=True)
        if percentile:
            n = np.floor(len(self)*percentile/100)
            prune = self.thinnest(n=n, index=True)

        del self[prune]  # In place delete

        return

    def anneal(self):
        """
        Fill in empty intervals by growing from top and base.

        Note that this operation happens in-place and destroys any information
        about the Position (e.g. metadata associated with the top or base). See
        issue #54.
        """
        gaps = self.find_gaps(index=True)

        if not gaps:
            return

        for gap in gaps:
            before = self[gap]
            after = self[gap + 1]

            if self.order == 'depth':
                t = (after.top.z-before.base.z)/2
                before.base = before.base.z + t
                after.top = after.top.z - t
            else:
                t = (after.base-before.top)/2
                before.top = before.top.z + t
                after.base = after.base.z - t

        # These were in-place operations so we don't return anything
        return

    def fill(self, component):
        """
        Fill gaps with the component provided.
        """
        pass

    def intersect(self, other):
        """
        Makes a striplog of all intersections.
        """
        if not isinstance(other, self.__class__):
            m = "You can only intersect striplogs with each other."
            raise StriplogError(m)

        result = []
        for iv in self:
            for jv in other:
                try:
                    result.append(iv.intersect(jv))
                except IntervalError:
                    # The intervals don't overlap
                    pass
        return Striplog(result)

    def merge_overlaps(self):
        """
        Merges overlaps by merging overlapping Intervals.

        TODO: This function will not work if any interval overlaps more than
            one other intervals at either its base or top.

        """
        overlaps = np.array(self.find_overlaps(index=True))

        if not overlaps.any():
            return

        for overlap in overlaps:
            before = self[overlap].copy()
            after = self[overlap + 1].copy()

            # Get rid of the before and after pieces.
            del self[overlap]
            del self[overlap]

            # Make the new piece.
            new_segment = before.merge(after)

            # Insert it.
            self.__insert(overlap, new_segment)

            overlaps += 1

        return

    def thickest(self, n=1, index=False):
        """
        Returns the thickest interval(s) as a striplog.

        Args:
            n (int): The number of thickest intervals to return. Default: 1.
            index (bool): If True, only the indices of the intervals are
                returned. You can use this to index into the striplog.
        """
        s = sorted(range(len(self)), key=lambda k: self[k].thickness)
        indices = s[-n:]
        if index:
            return indices
        else:
            if n == 1:
                # Then return an interval
                i = indices[0]
                return self[i]
            else:
                return self[indices]

    def thinnest(self, n=1, index=False):
        """
        Returns the thinnest interval(s) as a striplog.

        TODO:
            If you ask for the thinnest bed and there's a tie, you will
            get the last in the ordered list.
        """
        s = sorted(range(len(self)), key=lambda k: self[k].thickness)
        indices = s[:n]
        if index:
            return indices
        else:
            if n == 1:
                i = indices[0]
                return self[i]
            else:
                return self[indices]

    def histogram(self, interval=1.0, lumping=None, summary=False, sort=True):
        """
        Returns the data for a histogram. Does not plot anything.

        Args:
            interval (float): The sample interval; small numbers mean big bins.
            lumping (str): If given, the bins will be lumped based on this
                attribute of the primary components of the intervals encount-
                ered.
            summary (bool): If True, the summaries of the components are
                returned as the bins. Otherwise, the default behaviour is to
                return the Components themselves.
            sort (bool): If True (default), the histogram is sorted by value,
                starting with the largest.

        Returns:
            Tuple: A tuple of tuples of entities and counts.

        TODO:
            Deal with numeric properties, so I can histogram 'Vp' values, say.
        """
        d_list = np.arange(self.start, self.stop, interval)
        raw_readings = []
        for d in d_list:
            if lumping:
                x = self.read_at(d).primary[lumping]
            else:
                x = self.read_at(d)
                if not x:
                    continue
                if summary:
                    x = x.primary.summary()
                else:
                    x = x.primary
            raw_readings.append(x)
        c = Counter(raw_readings)
        ents, counts = tuple(c.keys()), tuple(c.values())

        if sort:
            z = zip(counts, ents)
            counts, ents = zip(*sorted(z, key=lambda t: t[0], reverse=True))

        return ents, counts

    def invert(self, copy=False):
        """
        Inverts the striplog, changing its order and the order of its contents.
        """
        if copy:
            new_intervals = []
            for i in self:
                new_intervals.append(i.invert(copy=True))
            return Striplog(new_intervals)  # Should get order automatically.
        else:
            for i in self:
                i.invert()
            self.__sort()
            o = self.order
            self.order = {'depth': 'elevation', 'elevation': 'depth'}[o]
            return

    def crop(self, extent, copy=False):
        """
        Crop to a new depth range.

        Args:
            extent (tuple): The new start and stop depth. Must be 'inside'
            existing striplog.

        Returns:
            Operates in place by deault; if copy is True, returns a striplog.
        """
        try:
            if extent[0] is None:
                extent = (self.start, extent[1])
            if extent[1] is None:
                extent = (extent[0], self.stop)
        except:
            m = "You must provide a 2-tuple for the new extents. Use None for"
            m += " the existing start or stop."
            raise StriplogError(m)

        first_ix = self.read_at(extent[0], index=True)
        last_ix = self.read_at(extent[1], index=True)

        first = self[first_ix].split_at(extent[0])[1]
        last = self[last_ix].split_at(extent[1])[0]

        new_list = self.__list[first_ix:last_ix+1].copy()
        new_list[0] = first
        new_list[-1] = last

        if copy:
            return Striplog(new_list)
        else:
            self.__list = new_list
            return
