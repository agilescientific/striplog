#!/usr/bin/env python
# -*- coding: utf 8 -*-
"""
A striplog is a sequence of intervals.

:copyright: 2015 Agile Geoscience
:license: Apache 2.0
"""

import re
import StringIO
import csv
import operator

import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
from matplotlib import patches

from interval import Interval
import utils
import templates


class StriplogError(Exception):
    pass


class Striplog(object):
    """
    A Striplog is a sequence of intervals.

    We will build them from LAS files or CSVs.
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
        return self

    def next(self):  # __next__() in Python 3
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
        return self.__list[::-1]

    def __add__(self, other):
        result = self.__list + other.__list
        return Striplog(result)

    @classmethod
    def __intervals_from_loglike(self, loglike, offset=2):
        """
        Take a log-like stream of numbers or strings representing lithologies.

        Args:
           loglike (array-like): The input stream of loglike data.
           offset (int): Offset (down) from top at which to get lithology,
           to be sure of getting 'clean' pixels.

        Returns:
           ndarray. Two ndarrays: tops and lithologies.
        """
        loglike = np.array(loglike)
        all_edges = loglike[1:] == loglike[:-1]
        edges = all_edges[1:] & (all_edges[:-1] == 0)

        tops = np.where(edges)[0]
        tops = np.append(0, tops)

        liths = loglike[tops + offset]

        return tops, liths

    @classmethod
    def from_csv(cls, text,
                 lexicon=None,
                 source='CSV',
                 dlm=',',
                 ignore_las=False):
        """
        Convert an OTHER field containing interval data to an interval
        dictionary. Handles an arbitrary number of fields; it's up to you
        to know what they are.

        Args:
           text (str): The input text, given by ``well.other``.
           dlm (str): The delimiter, given by ``well.dlm``. Default: CSV

        Returns:
           dict. A dictionary with keys 'tops', 'bases', and 'liths'.

        Example:
            # Lithology interval data
            ~OTHER
            # TOP       BOT        LITH
              312.34,   459.61,    Sandstone
              459.71,   589.61,    Limestone
              589.71,   827.50,    Green shale
              827.60,   1010.84,   Fine sandstone
        """
        text = re.sub(r'(\n+|\r\n|\r)', '\n', text.strip())

        as_strings = []
        f = StringIO.StringIO(text)
        reader = csv.reader(f, delimiter=dlm, skipinitialspace=True)
        for row in reader:
            as_strings.append(row)

        result = {'tops': [], 'bases': [], 'liths': []}

        for i, row in enumerate(as_strings):
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

            # LITH
            this_lith = row[2].strip()

            # If this top is not the same as the last base, add a layer first.
            if (i > 0) and (this_top != result['bases'][-1]):
                result['tops'].append(result['bases'][-1])  # Last base.
                result['bases'].append(this_top)
                result['liths'].append('')

            # ASSIGN
            result['tops'].append(this_top)
            result['bases'].append(this_base)
            result['liths'].append(this_lith)

        # Build the list.
        list_of_Intervals = []
        for i, t in enumerate(result['tops']):
            b = result['bases'][i]
            d = result['liths'][i]
            interval = Interval(t, b, description=d, lexicon=lexicon)
            list_of_Intervals.append(interval)

        return cls(list_of_Intervals, source=source)

    @classmethod
    def from_img(cls, filename, start, stop, legend,
                 source="Image",
                 offset=2,
                 tolerance=0):
        """
        Read an image and generate Striplog.

        Args:
           filename (str): An image file, preferably high-res PNG.
           start (float or int): The depth at the top of the image.
           stop (float or int): The depth at the bottom of the image.
           offset (int): The number of pixels to skip at the top of each
              change in colour.
           tolerance (float): The Euclidean distance between hex colours,
              which has a maximum (black to white) of 25.98 in base 10.

        Returns:
           str. The CSV string from which to build the Striplog object.

        """
        im = np.array(Image.open(filename))
        col = im.shape[1]/10.  # One tenth of way across image.
        rgb = im[:, col, :3]
        loglike = np.array([utils.rgb_to_hex(t) for t in rgb])

        # Get the pixels and colour values at 'tops' (i.e. changes).
        pixels, hexes = cls.__intervals_from_loglike(loglike, offset=offset)

        # Scale pixel values to actual depths.
        length = float(loglike.size)
        tops = [start + (p/length) * (stop-start) for p in pixels]
        bases = tops[1:] + [stop]

        # Get the rocks corresponding to the colours.
        rocks = [legend.get_rock(h, tolerance=tolerance) for h in hexes]

        list_of_Intervals = []
        for i, t in enumerate(tops):
            interval = Interval(t, bases[i], components=[rocks[i]])
            list_of_Intervals.append(interval)

        return cls(list_of_Intervals, source="Image")

    @classmethod
    def from_las3(cls, string, lexicon, source="LAS", dlm=','):
        """
        Turn LAS3 'Lithology' section into a Striplog.

        NB Does not read an actual LAS file. Use the Well object for that.
        """
        f = re.DOTALL | re.IGNORECASE
        regex = r'^\~.+?Data.+?\n(.+?)(?:\n\n+|\n*\~|\n*$)'
        pattern = re.compile(regex, flags=f)
        csv_text = pattern.search(string).group(1)

        s = re.search(r'\.(.+?)\: ?.+?source', string)
        if s:
            source = s.group(1).strip()

        return cls.from_csv(csv_text, lexicon, source=source)

    def to_csv(self, dlm=",", header=True):
        """
        Returns a CSV string built from the summaries of the Intervals.

        Args:
           dlm (str): The delimiter.
           source (str): The sourse of the data.

        Returns:
           str. A string of comma-separated values.

        """
        data = ''

        if header:
            data += '{0:12s}{1:12s}'.format('Top', 'Base')
            data += '  {0:48s}'.format('Lithology')

        for i in self.__list:
            if i.primary:
                summary = i.primary.summary()
            else:
                summary = ''
            data += '{0:9.3f}'.format(i.top)
            data += '{0}{1:9.3f}'.format(dlm, i.base)
            data += '{0}  {1:48s}'.format(dlm, summary)
            data += '\n'

        return data

    def to_las3(self, dlm=",", source="Striplog"):
        """
        Returns an LAS 3.0 section string.

        Args:
           dlm (str): The delimiter.
           source (str): The sourse of the data.

        Returns:
           str. A string forming Lithology section of an LAS3 file.

        """
        data = self.to_csv(dlm=dlm, header=False)

        return templates.lithology.format(source=source, data=data)

    def plot_axis(self, ax, legend, ladder=False, default_width=1):
        """
        Plotting, but only the Rectangles. You have to set up the figure.
        Returns a matplotlib axis object.
        """
        for i in self.__list:
            origin = (0, i.top)
            colour = legend.get_colour(i.primary)
            thick = i.base - i.top

            if ladder:
                w = legend.get_width(i.primary) or default_width
            else:
                w = default_width

            rect = patches.Rectangle(origin, w, thick, color=colour)
            ax.add_patch(rect)

        return ax

    def plot(self, legend, width=1, ladder=False, aspect=10):
        """
        Hands-free plotting.
        """
        if ladder:
            width = legend.max_width

        fig = plt.figure(figsize=(width, aspect*width))

        # And a series of Rectangle patches for the striplog.
        ax = fig.add_subplot(111)

        self.plot_axis(ax=ax,
                       legend=legend,
                       ladder=ladder,
                       default_width=width)

        ax.set_xlim([0, width])
        ax.set_ylim([self.stop, self.start])
        ax.set_xticks([])

        fig.show()

        return None

    def find(self, search_term):
        """
        Look for a regex expression in the descriptions of the striplog.
        If there's no description, it looks in the summaries.

        If you pass a Rock, then it will search the components, not the
        descriptions.
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
    def thick(self):
        max_int = None
        for i in self:
            if i.thickness > max_int.thickness:
                max_int = i
        return max_int

    @property
    def thin(self):
        """
        Returns the thinnest interval.
        """
        min_int = None
        for i in self:
            if i.thickness < min_int.thickness:
                min_int = i
        return min_int

    @property
    def cum(self):
        """
        Returns the cumulative thickness of all rock-filled intervals.

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
        Returns the mean thickness of all rock-filled intervals.
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
