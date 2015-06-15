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

import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
from matplotlib import patches
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

from .interval import Interval
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
    def __init__(self, list_of_Intervals, source=None):
        self.source = source
        self.start = list_of_Intervals[0].top
        self.stop = list_of_Intervals[-1].base

        self.__list = list_of_Intervals
        self.__index = 0  # Set up iterable.

    def __repr__(self):
        l = len(self.__list)
        details = "start={start}, stop={stop}".format(**self.__dict__)
        return "Striplog({0} Intervals, {1})".format(l, details)

    def __str__(self):
        s = [str(i) for i in self.__list]
        return '\n'.join(s)

    # Could use collections but doing this with raw magics.
    # Set up Striplog as an array-like iterable.
    def __getitem__(self, key):
        if not key:
            return
        elif type(key) is slice:
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

    def __len__(self):
        return len(self.__list)

    def __delitem__(self, key):
        del self.__list[key]

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

    def next(self):  # __next__() in Python 3
        """
        Supports iterable.

        __next__() in Python 3.
        """
        try:
            result = self.__list[self.__index]
        except IndexError:
            self.__index = 0
            raise StopIteration
        self.__index += 1
        return result

    def __contains__(self, item):
        for r in self.__list:
            if item in r.components:
                return True
        return False

    def __reversed__(self):
        # Not sure if this should return a Striplog or not.
        # Maybe it's nonsensical to even allow the operation.
        return self.__list[::-1]

    def __add__(self, other):
        if isinstance(other, self.__class__):
            result = self.__list + other.__list
            return Striplog(result)
        elif isinstance(other, Interval):
            result = self.__list + [other]
            return Striplog(result)
        else:
            raise StriplogError("You can only add striplogs or intervals.")

    @classmethod
    def __intervals_from_loglike(self, loglike, offset=2):
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

        tops = np.where(edges)[0]
        tops = np.append(0, tops)

        values = loglike[tops + offset]

        return tops, values

    @classmethod
    def from_csv(cls, text,
                 lexicon=None,
                 source='CSV',
                 dlm=',',
                 points=False,
                 abbreviations=False,
                 complete=False):
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
        f = StringIO(text)
        reader = csv.reader(f, delimiter=dlm, skipinitialspace=True)
        for row in reader:
            as_strings.append(row)

        result = {'tops': [], 'bases': [], 'descrs': []}

        for i, row in enumerate(as_strings):
            if len(row) == 2:
                row = [row[0], None, row[1]]

            # TOP
            this_top = float(row[0])

            # BASE
            # Base is null: use next top if this isn't the end.
            if not row[1]:
                if i < len(as_strings)-1:
                    this_base = float(as_strings[i+1][0])  # Next top.
                else:
                    this_base = this_top + 1  # Default to 1 m thick at end.
            else:
                this_base = float(row[1])

            # DESCRIPTION
            this_descr = row[2].strip()

            # Deal with making intervals or points...
            if not points:
                # Insert intervals where needed.
                if complete and (i > 0) and (this_top != result['bases'][-1]):
                    result['tops'].append(result['bases'][-1])
                    result['bases'].append(this_top)
                    result['descrs'].append('')
            else:
                this_base = None

            # ASSIGN
            result['tops'].append(this_top)
            result['bases'].append(this_base)
            result['descrs'].append(this_descr)

        # Build the list.
        list_of_Intervals = []
        for i, t in enumerate(result['tops']):
            b = result['bases'][i]
            d = result['descrs'][i]
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
        im = np.array(Image.open(filename))
        col = im.shape[1]/(100./offset)
        rgb = im[:, col, :3]
        loglike = np.array([utils.rgb_to_hex(t) for t in rgb])

        # Get the pixels and colour values at 'tops' (i.e. changes).
        pixels, hexes = cls.__intervals_from_loglike(loglike,
                                                     offset=pixel_offset)

        # Scale pixel values to actual depths.
        length = float(loglike.size)
        tops = [start + (p/length) * (stop-start) for p in pixels]
        bases = tops[1:] + [stop]

        # Get the components corresponding to the colours.
        comps = [legend.get_component(h, tolerance=tolerance) for h in hexes]

        list_of_Intervals = []
        for i, t in enumerate(tops):
            interval = Interval(t, bases[i], components=[comps[i]])
            list_of_Intervals.append(interval)

        return cls(list_of_Intervals, source="Image")

    @classmethod
    def from_array(cls, a,
                   lexicon=None,
                   source="",
                   points=False,
                   abbreviations=False):
        """
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
            data += '{0:9.3f}'.format(i.top)
            data += '{0}{1:9.3f}'.format(dlm, i.base)
            data += '{0}  {1:48s}'.format(dlm, '"'+text+'"')
            data += '\n'

        return data

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

    def to_log(self, step=1.0, start=None, stop=None, legend=None):
        """
        Return a fully sampled log from a striplog. Useful for crossplotting
        with log data, for example.

        Args:
            step (float): The step size. Default: 1.0.
            start (float): The start depth of the new log. You will want to
                match the logs, so use the start depth from the LAS file.
                Default: The start of the striplog.
            stop (float): The stop depth of the new log. Use the stop depth
                of the LAS file. Default: The stop depth of the striplog.
            legend (Legend): If you want the codes to come from a legend,
                provide one. Otherwise the codes come from the log, using
                integers in the other they are encountered. If you use a
                legend, they are assigned in the order of the legend.

        Returns:
            ndarray: Two ndarrays in a tuple, (depth, logdata).
        """
        # Make the preparations.
        if not start:
            start = self.start

        if not stop:
            stop = self.stop

        pts = np.floor((stop - start)/step)
        stop = self.start + step * pts
        depth = np.linspace(start, stop, pts+1)
        result = np.zeros_like(depth)

        # Make a look-up table for the log values.
        if legend:
            table = {j.component: i+1 for i, j in enumerate(legend)}
        else:
            table = {j[0]: i+1 for i, j in enumerate(self.top)}

        # Assign the values from the lookup table.
        for i in self:
            top_index = np.ceil((i.top-start)/step)
            base_index = np.ceil((i.base-start)/step)+1
            key = table.get(i.primary) or 0
            result[top_index:base_index] = key

        return depth, result

    def plot_axis(self,
                  ax,
                  legend,
                  ladder=False,
                  default_width=1,
                  match_only=None):
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

        Returns:
            axis: The matplotlib axis.
        """
        for i in self.__list:
            origin = (0, i.top)
            colour = legend.get_colour(i.primary, match_only=match_only)
            thick = i.base - i.top
            d = default_width

            if ladder:
                w = legend.get_width(i.primary, match_only=match_only) or d
                w = d * w/legend.max_width
            else:
                w = d

            rect = patches.Rectangle(origin, w, thick, color=colour)
            ax.add_patch(rect)

        return ax

    def plot(self,
             legend=None,
             width=1,
             ladder=False,
             aspect=10,
             interval=(1, 10),
             match_only=None):
        """
        Hands-free plotting.

        Args:
            legend (Legend): The Legend to use for colours, etc.
            width (int): The width of the plot, in inches. Default 1.
            ladder (bool): Whether to use widths or not. Default False.
            aspect (int): The aspect ratio of the plot. Default 10.
            interval (int or tuple): The (minor,major) tick interval for depth.
                Only the major interval is labeled. Default (1,10).
            match_only (list): A list of strings matching the attributes you
                want to compare when plotting.

        Returns:
            None: The plot is a side-effect.
        """
        fig = plt.figure(figsize=(width, aspect*width))

        # And a series of Rectangle patches for the striplog.
        ax = fig.add_axes([0, 0, 1, 1])

        if not legend:
            # Build a random-coloured legend.
            comps = [i[0] for i in self.top if i[0]]
            legend = Legend.random(comps)

        self.plot_axis(ax=ax,
                       legend=legend,
                       ladder=ladder,
                       default_width=width,
                       match_only=match_only)

        ax.set_xlim([0, width])
        ax.set_ylim([self.stop, self.start])
        ax.set_xticks([])

        if type(interval) is int:
            interval = (1, interval)

        minorLocator = MultipleLocator(interval[0])
        ax.yaxis.set_minor_locator(minorLocator)

        majorLocator = MultipleLocator(interval[1])
        majorFormatter = FormatStrFormatter('%d')
        ax.yaxis.set_major_locator(majorLocator)
        ax.yaxis.set_major_formatter(majorFormatter)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.yaxis.set_ticks_position('left')
        ax.get_yaxis().set_tick_params(which='both', direction='out')

        ax.patch.set_alpha(0)

        plt.show()

        return None

    def depth(self, d):
        """
        Get the interval at a particular depth.

        Args:
            d (Number): The depth to query.

        Returns:
            Interval: The interval at that depth, or None if
                the depth is outside the striplog's range.
        """
        for iv in self:
            if iv.top <= d <= iv.base:
                return iv
        return None

    def find(self, search_term):
        """
        Look for a regex expression in the descriptions of the striplog.
        If there's no description, it looks in the summaries.

        If you pass a Component, then it will search the components, not the
        descriptions or summaries.

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
                pattern = re.compile(search_term)
                if pattern.search(search_text):
                    hits.append(i)
            except TypeError:
                if search_term in iv.components:
                    hits.append(i)
        return self[hits]

    @property
    def thickest(self):
        """
        Returns the thickest interval.
        """
        max_int, max_thick = None, 0
        for i in self:
            if i.thickness > max_thick:
                max_int, max_thick = i, i.thickness
        return max_int

    @property
    def thinnest(self):
        """
        Returns the thinnest interval.
        """
        min_int, min_thick = None, 0
        for i in self:
            if i.thickness < min_thick:
                min_int, min_thick = i, i.thickness
        return min_int

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
    def top(self):
        """
        Summarize a Striplog with some statistics.
        """
        all_rx = set([iv.primary for iv in self])
        table = {r: 0 for r in all_rx}
        for iv in self:
            table[iv.primary] += iv.thickness

        return sorted(table.items(), key=operator.itemgetter(1), reverse=True)
