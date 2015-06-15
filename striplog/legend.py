#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines a legend for displaying components.

:copyright: 2015 Agile Geoscience
:license: Apache 2.0
"""
from builtins import object
from io import StringIO
import csv
import warnings

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import patches
from matplotlib.colors import rgb2hex

from .component import Component
from . import utils
from .defaults import LEGEND


class LegendError(Exception):
    """
    Generic error class.
    """
    pass


class Decor(object):
    """
    A single display style. A Decor describes how to display a given set
    of Component properties.

    In general, you will not usually use a Decor on its own. Instead, you
    will want to use a Legend, which is just a list of Decors, and leave
    the Decors to the Legend.

    Args:
      params (dict): The parameters you want in the Decor. There must be a
        Component to attach the decoration to, and at least 1 other attribute.
        It's completely up to you, but you probably want at least a colour
        (hex names like #AAA or #d3d3d3, or matplotlib's English-language
        names listed at http://ageo.co/modelrcolour are acceptable.

        The only other parameter the class recognizes for now is 'width',
        which is the width of the striplog element.

    Example:
      my_rock = Component({ ... })
      d = {'component': my_rock, 'colour': 'red'}
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

        if not getattr(self, 'component', None):
            raise LegendError("You must provide a Component to decorate.")

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
        if c is not None:
            if type(c) in [list, tuple, np.ndarray]:
                try:
                    self.colour = rgb2hex(c)
                except TypeError:
                    raise LegendError("Colour not recognized: " + c)
            elif c[0] != '#':
                try:
                    self.colour = utils.name_to_hex(c)
                except KeyError:
                    raise LegendError("Colour not recognized: " + c)
            elif len(c) == 4:
                try:
                    self.colour = c[:2] + c[1] + 2*c[2] + 2*c[3]
                except TypeError:
                    raise LegendError("Colour not recognized: " + c)
            else:
                pass  # Leave the colour alone. Could assert here.
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

    def __add__(self, other):
        if isinstance(other, self.__class__):
            result = [self, other]
            return Legend(result)
        elif isinstance(other, Legend):
            result = [self] + other.__list
            return Legend(result)
        else:
            raise LegendError("You can only add legends or decors.")

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        s = {k: v for k, v in self.__dict__.items() if v}
        o = {k: v for k, v in other.__dict__.items() if v}
        if not cmp(s, o):
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    # If we define __eq__ we also need __hash__ otherwise the object
    # becomes unhashable. All this does is hash the frozenset of the
    # keys. (You can only hash immutables.)
    def __hash__(self):
        return hash(frozenset(self.__dict__.keys()))

    @classmethod
    def random(cls, component):
        """
        Returns a minimal Decor with a random colour.
        """
        colour = np.random.rand(3,)
        return cls({'colour': colour, 'component': component})

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
                 self.component.summary(),
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
    A look-up table to assist in the conversion of Components to
    a plot colour.

    Args:
        list_of_Decors (list): The decors to collect into a legend. In
            general, you will want to leave legend building to the constructor
            class methods, `Legend.default()`, and `Legend.from_csv(string)`.
            We can add others over time, such as `from_xls` and so on.
    """

    def __init__(self, list_of_Decors):
        self.table = [d.__dict__ for d in list_of_Decors]
        self.__list = list_of_Decors
        self.__index = 0
        self._iter = iter(self.__list)  # Set up iterable.

    def __repr__(self):
        s = str(self)
        return "Legend({0})".format(s)

    def __str__(self):
        s = [str(d) for d in self.__list]
        return '\n'.join(s)

    def __getitem__(self, key):
        if not key:
            return
        elif type(key) is slice:
            i = key.indices(len(self.__list))
            result = [self.__list[n] for n in range(*i)]
            return Legend(result)
        elif type(key) is list:
            result = []
            for j in key:
                result.append(self.__list[j])
            return Legend(result)
        else:
            return self.__list[key]

    def __setitem__(self, key, value):
        self.__list[key] = value

    def __iter__(self):
        return self

    def __next__(self):
        try:
            result = self.__list[self.__index]
        except IndexError:
            self.__index = 0
            raise StopIteration
        self.__index += 1
        return result

    def __len__(self):
        return len(self.__list)

    def __contains__(self, item):
        if isinstance(item, Decor):
            for d in self.__list:
                if item == d:
                    return True
        if isinstance(item, Component):
            for d in self.__list:
                if item == d.component:
                    return True
        return False

    def __add__(self, other):
        if isinstance(other, self.__class__):
            result = self.__list + other.__list
            return Legend(result)
        elif isinstance(other, Decor):
            result = self.__list + [other]
            return Legend(result)
        else:
            raise LegendError("You can only add legends or decors.")

    @classmethod
    def default(cls):
        """
        Generate a default legend. No arguments.

        Returns:
            Legend: The legend stored in `defaults.py`.
        """
        return cls.from_csv(LEGEND)

    @classmethod
    def random(cls, list_of_Components):
        """
        Generate a random legend for a given list of components.

        Returns:
            Legend: A legend with random colours.
        """
        list_of_Decors = [Decor.random(r) for r in list_of_Components]
        return cls(list_of_Decors)

    @classmethod
    def from_csv(cls, string):
        """
        Read CSV text and generate a Legend.

        Note:
            To edit a legend, the easiest thing to do is probably this:

            - `legend.to_csv()`
            - Edit the legend, call it `new_legend`.
            - `legend = Legend.from_csv(new_legend)`
        """
        f = StringIO(string)
        r = csv.DictReader(f, skipinitialspace=True)
        list_of_Decors = []
        for row in r:
            d, component = {}, {}
            for (k, v) in row.items():
                if k[:4].lower() == 'component':
                    component[k[5:]] = v.lower()
                else:
                    d[k] = v.lower()
            d['component'] = Component(component)
            list_of_Decors.append(Decor(d))

        return cls(list_of_Decors)

    def to_csv(self):
        """
        Renders a legend as a CSV string.

        No arguments.

        Returns:
            str: The legend as a CSV.
        """
        # We can't delegate this to Decor because we need to know the superset
        # of all Decor properties. There may be lots of blanks.
        header = []
        component_header = []
        for row in self:
            for j in row.__dict__.keys():
                header.append(j)
            for k in row.component.__dict__.keys():
                component_header.append(k)
        header = set(header)
        component_header = set(component_header)

        header = set(header)
        component_header = set(component_header)
        header.remove('component')
        header_row = ''
        if 'colour' in header:
            header_row += 'colour,'
            header.remove('colour')
            has_colour = True
        for item in header:
            header_row += item + ','
        for item in component_header:
            header_row += 'component ' + item + ','

        # Now we have a header row! Phew.
        # Next we'll go back over the legend and collect everything.
        result = header_row.strip(',') + '\n'
        for row in self:
            if has_colour:
                result += row.__dict__.get('colour', '') + ','
            for item in header:
                result += str(row.__dict__.get(item, '')) + ','
            for item in component_header:
                result += str(row.component.__dict__.get(item, '')) + ','
            result += '\n'

        return result

    @property
    def max_width(self):
        """
        The maximum width of all the Decors in the Legend. This is needed
        to scale a Legend or Striplog when plotting with widths turned on.
        """
        maximum = max([row.width for row in self.__list])
        return maximum or 0

    def get_colour(self, c, default='#eeeeee', match_only=None):
        """
        Get the display colour of a component.

        Args:
           c (component): The component to look up.
           default (str): The colour to return in the event of no match.
           match_only (list of str): The component attributes to include in the
               comparison. Default: All of them.

        Returns:
           str. The hex string of the matching Decor in the Legend.
        """
        if c:
            if match_only:
                # Filter the component only those attributes
                c = Component({k: getattr(c, k) for k in match_only})
            for decor in self.__list:
                if c == decor.component:
                    return decor.colour
        return default

    def get_width(self, c, default=0, match_only=None):
        """
        Get the display width of a component.

        Args:
           c (component): The component to look up.
           default (float): The width to return in the event of no match.
           match_only (list of str): The component attributes to include in the
               comparison. Default: All of them.

        Returns:
           float. The width of the matching Decor in the Legend.
        """
        if c:
            if match_only:
                # Filter the component only those attributes
                c = Component({k: getattr(c, k) for k in match_only})
            for decor in self.__list:
                if c == decor.component:
                    return decor.width
        return default

    def get_component(self, colour, tolerance=0, default=None):
        """
        Get the component corresponding to a display colour. This is for
        generating a Striplog object from a colour image of a striplog.

        Args:
           colour (str): The hex colour string to look up.
           tolerance (float): The colourspace distance within which to match.
           default (component or None): The component to return in the event
           of no match.

        Returns:
           component. The component best matching the provided colour.
        """
        if not (0 <= tolerance <= np.sqrt(195075)):
            raise LegendError('Tolerance must be between 0 and 441.67')

        for decor in self.__list:
            if colour.lower() == decor.colour:
                return decor.component

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
                best_match = decor.component
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
