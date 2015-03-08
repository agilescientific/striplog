#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines a legend for displaying rocks.

:copyright: 2015 Agile Geoscience
:license: Apache 2.0
"""
import StringIO
import csv
import warnings

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import patches

from rock import Rock
import utils
from defaults import LEGEND_CSV


class LegendError(Exception):
    pass


class Decor(object):
    """
    A single display style. A Decor describes how to display a given set
    of Rock properties.

    In general, you will not usually use a Decor on its own. Instead, you
    will want to use a Legend, which is just a list of Decors, and leave
    the Decors to the Legend.

    Args:
      params (dict): The parameters you want in the Decor. There must be a
        Rock to attach the decoration to, and at least one other attribute.
        It's completely up to you, but you probably want at least a colour
        (hex names like #AAA or #d3d3d3, or matplotlib's English-language
        names listed at http://ageo.co/modelrcolour are acceptable.

        The only other parameter the class recognizes for now is 'width',
        which is the width of the striplog element.

    Example:
      d = {'rock': my_rock, 'colour': 'red'}
      my_decor = Decor(d)
    """
    def __init__(self, params):
        for k, v in params.items():
            k = k.lower().replace(' ', '_')
            try:
                v = v.lower()
            except AttributeError:
                v = v
            setattr(self, k, v)

        if not getattr(self, 'rock', None):
            raise LegendError("You must provide a Rock object to decorate.")

        if len(self.__dict__) < 2:
            raise LegendError("You must provide at least one decoration.")

        # Make sure we have a width, even if it's None.
        w = getattr(self, 'width', None)
        if w:
            self.width = float(self.width)
        else:
            self.width = None

        # Deal with American spelling.
        a = getattr(self, 'color', None)
        if a:
            setattr(self, 'colour', a)
            delattr(self, 'color')

        # Make sure the colour is correctly formatted, and allow
        # the use of matplotlib's English-language colour names.
        c = getattr(self, 'colour', None)
        if c:
            if c[0] != '#':
                try:
                    self.colour = utils.name_to_hex(c)
                except KeyError:
                    raise LegendError("Colour not recognized: " + c)
        else:
            self.colour = None

    def __repr__(self):
        s = str(self)
        return "Decor({0})".format(s)

    def __str__(self):
        s = []
        for key in self.__dict__:
            t = "{key}='{value}'"
            s.append(t.format(key=key, value=self.__dict__[key]))
        return ', '.join(s)

    @property
    def rgb(self):
        """
        Returns an RGB triple equivalent to the hex colour.
        """
        return utils.hex_to_rgb(self.colour)

    def plot(self):
        """
        Make a simple plot of the Decor.

        Args:
        widths (bool): Whether to use the widths in the plot.
        height (int): A scalar for the height, in inches.

        Returns:
        None. Instead the function creates a plot object as a side-effect.
        """

        u = 1  # A bit arbitrary; some sort of scale

        plt.figure(figsize=(1, 1))
        ax = plt.subplot(111)
        rect1 = patches.Rectangle((0, 0),
                                  u, u,
                                  color=self.colour)
        ax.add_patch(rect1)
        plt.text(1.2*u, 0.5*u,
                 self.rock.summary(),
                 fontsize=max(u, 15),
                 verticalalignment='center',
                 horizontalalignment='left')
        plt.xlim([0, u])
        plt.ylim([0, u])
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.invert_yaxis()

        plt.show()


class Legend(object):
    """
    A look-up table to assist in the conversion of Rocks to
    a plot colour.
    """

    def __init__(self, list_of_Decors):
        """
        This is not very elegant, but using csv, which is
        convenient, requires the use of a file-like.
        """
        self.table = [d.__dict__ for d in list_of_Decors]

        self.__list = list_of_Decors
        self.__index = 0  # Set up iterable.

    def __repr__(self):
        s = str(self)
        return "Legend({0})".format(s)

    def __str__(self):
        s = [str(d) for d in self.__list]
        return '\n'.join(s)

    def __getitem__(self, key):
        return self.__list[key]

    def __setitem__(self, key, value):
        self.__list[key] = value

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

    @classmethod
    def default(cls):
        """
        Generate a default legend.
        """
        return cls.from_csv(LEGEND_CSV)

    @classmethod
    def from_csv(cls, string):
        """
        Read CSV text and generate a Legend.
        """
        f = StringIO.StringIO(string)
        r = csv.DictReader(f, skipinitialspace=True)
        list_of_Decors = []
        for row in r:
            d, rock = {}, {}
            for k, v in row.iteritems():
                if k[:4].lower() == 'rock':
                    rock[k[5:]] = v.lower()
                else:
                    d[k] = v.lower()
            d['rock'] = Rock(rock)
            list_of_Decors.append(Decor(d))

        return cls(list_of_Decors)

    @property
    def max_width(self):
        """
        The maximum width of all the Decors in the Legend. This is needed
        to scale a Legend or Striplog when plotting with widths turned on.
        """
        return max([row.width for row in self.__list])

    def get_colour(self, rock, default='#EEEEEE'):
        """
        Get the display colour of a Rock.

        Args:
           rock (rock): The rock to look up.
           default (str): The colour to return in the event of no match.

        Returns:
           str. The hex string of the matching Decor in the Legend.
        """
        if rock:
            for decor in self.__list:
                if rock == decor.rock:
                    return decor.colour
        return default

    def get_width(self, rock, default=0):
        """
        Get the display width of a Rock.

        Args:
           rock (rock): The rock to look up.
           default (float): The width to return in the event of no match.

        Returns:
           float. The width of the matching Decor in the Legend.
        """
        if rock:
            for decor in self.__list:
                if rock == decor.rock:
                    return decor.width
        return default

    def get_rock(self, colour, tolerance=0, default=None):
        """
        Get the rock corresponding to a display colour. This is for generating
        a Striplog object from a colour image of a striplog.

        Args:
           colour (str): The hex colour string to look up.
           tolerance (float): The colourspace distance within which to match.
           default (rock or None): The rock to return in the event of no match.

        Returns:
           rock. The rock best matching the provided colour.
        """
        if not (0 <= tolerance <= np.sqrt(195075)):
            raise LegendError('Tolerance must be between 0 and 441.67')

        for decor in self.__list:
            if colour.lower() == decor.colour:
                return decor.rock

        # If we're here, we didn't find one yet.
        r1, g1, b1 = utils.hex_to_rgb(colour)

        # Start with a best match of black.
        best_match = '#000000'
        best_match_dist = np.sqrt(r1**2. + g1**2. + b1**2.)

        # Now compare to each colour in the legend.
        for decor in self.__list:
            r2, g2, b2 = decor.rgb
            distance = np.sqrt((r2-r1)**2. + (g2-g1)**2. + (b2-b1)**2.)
            if distance < best_match_dist:
                best_match = decor.rock
                best_match_dist = distance
                best_match_colour = decor.colour

        if best_match_dist <= tolerance:
            return best_match
        else:
            with warnings.catch_warnings():
                warnings.simplefilter("always")
                w = "No match found for {0} ".format(colour.lower())
                w += "with tolerance of {0}. Best match is ".format(tolerance)
                w += "{0}, {1}".format(best_match.summary(), best_match_colour)
                w += ", d={0}".format(best_match_dist)
                warnings.warn(w)

            return default

    def plot(self):
        """
        Make a simple plot of the legend.

        Simply calls Decor.plot() on all of its members.

        TODO: Build a more attractive plot.
        """
        for d in self.__list:
            d.plot()
