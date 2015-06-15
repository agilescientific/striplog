#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines intervals for holding components.

:copyright: 2015 Agile Geoscience
:license: Apache 2.0
"""

import re
import warnings
import numbers
from functools import total_ordering

from .component import Component


class IntervalError(Exception):
    """
    Generic error class.
    """
    pass


@total_ordering
class Interval(object):
    """
    Used to represent a lithologic or stratigraphic interval, or single point,
    such as a sample location.

    Initialize with a top (and optional base) and a description and/or
    an ordered list of components.

    Args:
        top (float): Required top depth. Required.
        base (float): Base depth. Optional.
        lexicon (dict): A lexicon. See documentation. Optional unless you only
            provide descriptions, because it's needed to extract components.
        max_component (int): The number of components to extract. Default 1.
        abbreviations (bool): Whether to parse for abbreviations.

    """
    def __init__(self, top, base=None,
                 description='',
                 lexicon=None,
                 components=None,
                 max_component=1,
                 abbreviations=False):

        self.top = float(top)
        if base:
            self.base = float(base)
        else:
            self.base = self.top

        self.description = str(description)

        if components:
            self.components = list(components)
        else:
            self.components = None

        if self.description and (not self.components):
            if lexicon:
                comps = self.__parse_description(lexicon,
                                                 max_component=max_component,
                                                 abbreviations=abbreviations)
                self.components = comps
            else:
                with warnings.catch_warnings():
                    warnings.simplefilter("always")
                    w = "You must provide a lexicon to generate "
                    w += "components from descriptions."
                    warnings.warn(w)
                self.components = []

        if self.components:
            self.primary = self.components[0]
        else:
            self.primary = None

    def __repr__(self):
        s = str(self)
        return "Interval({0})".format(s)

    def __str__(self):
        s = "top: {top}, base: {base}, "
        s += "description: '{description}', "
        s += "components: {components}"
        return s.format(**self.__dict__)

    # Let's make addition combine the intervals into a new one, or
    # add thickness to the interval (if )
    def __add__(self, other):
        if isinstance(other, self.__class__):
            top = min(self.top, other.top)
            base = max(self.base, other.base)
            prop = 100 * max(self, other).thickness / (base-top)
            d1 = max(self, other).description.strip(' .,')
            d2 = min(self, other).description.strip(' .,')
            d = '{:.1f}% {} with {:.1f}% {}'.format(prop, d1, 100-prop, d2)
            c = max(self, other).components + min(self, other).components
            return Interval(top, base, description=d, components=c)
        elif isinstance(other, Component):
            top = self.top
            base = self.base
            d = self.description + ' with ' + other.summary()
            c = self.components + [other]
            return Interval(top, base, description=d, components=c)
        elif isinstance(other, numbers.Number):
            top = self.top
            base = self.base + other
            d = self.description
            c = self.components
            return Interval(top, base, description=d, components=c)
        else:
            raise IntervalError("You can only add intervals or thicknesses.")

    # Must supply __eq__ and one other rich comparison for
    # the total_ordering function to provide the others.
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.thickness == other.thickness:
                return True
        return False

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            if self.thickness < other.thickness:
                return True
        return False

    @property
    def thickness(self):
        """
        Returns the thickness of the interval.

        Returns:
            Float: The thickness.
        """
        return abs(self.base - self.top)

    @property
    def kind(self):
        """
        The type of Interval: a 'point' (where base = top),
        or an 'interval', where thickness > 0.

        Returns:
            str: Either 'point' or 'interval'.
        """
        if self.thickness > 0:
            return 'point'
        return 'interval'

    def summary(self, fmt=None, initial=False):
        """
        Returns a summary of the interval.

        Args:
            fmt (str): A format string. Optional.
            initial (bool): Whether to capitalize the first letter.

        Returns:
            str: An English-language summary.

        TODO:
            Allow formatting of the entire string, not just the rock.
        """
        s = [r.summary(fmt=fmt, initial=initial) for r in self.components]
        summary = " with ".join(s)
        return "{0:.2f} m of {1}".format(self.thickness, summary)

    @staticmethod
    def __split_description(text):
        """
        Split a description into parts, each of which can be turned into
        a single component.
        """
        # Protect some special sequences.
        t = re.sub(r'(\d) ?in\. ', r'\1 inch ', text)  # Protect.
        t = re.sub(r'(\d) ?ft\. ', r'\1 feet ', t)  # Protect.

        # Transform all part delimiters to 'with'.
        t = re.sub(r'\;?\.? ?((under)? \d+%) (?=\w)', r' with \1 ', t)
        t = re.sub(r'\. ', r' with ', t)

        # Split.
        f = re.IGNORECASE
        pattern = re.compile(r'.(?:with|contain(?:s|ing)?)', flags=f)
        parts = filter(None, pattern.split(t))

        return [i.strip() for i in parts]

    def __parse_description(self, lexicon,
                            max_component=1,
                            abbreviations=False):
        """
        Turns a description into a lists of components. The items in the
        list are in the order they were found in the description, which is
        usually order of importance.
        """
        if abbreviations:
            text = lexicon.expand_abbreviations(self.description)
        else:
            text = self.description

        components = []
        for p, part in enumerate(self.__split_description(text)):
            if p == max_component:
                break
            components.append(Component.from_text(part, lexicon))

        return components
