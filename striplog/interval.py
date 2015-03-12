#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines intervals for holding rocks.

:copyright: 2015 Agile Geoscience
:license: Apache 2.0
"""

import re
import warnings
import numbers
from functools import total_ordering

from rock import Rock
#from striplog import Striplog


class IntervalError(Exception):
    pass

@total_ordering
class Interval(object):
    """
    Used to represent a lithologic or strigraphic interval, or a single point,
    such as a sample location. 

    Initialize with a top (and optional base) and a description and/or
    an ordered list of components, each of which is a Rock.

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
                                                 max_component=max_component)
                self.components = comps
            else:
                with warnings.catch_warnings():
                    warnings.simplefilter("always")
                    w = "You must provide a lexicon to generate "
                    w += "rock components from descriptions."
                    warnings.warn(w)
                self.components = []

        try:
            self.primary = self.components[0]
        except:
            raise IntervalError('There are no components.')

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
            d1 = max(self, other).description
            d2 = min(self, other).description
            d =  d1.strip(' .,') + '  with ' + d2.strip(' .,')
            c = max(self, other).components + min(self, other).components
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
        return abs(self.base - self.top)

    @property
    def kind(self):
        if self.thickness > 0:
            return 'top'
        return 'interval'

    def summary(self, fmt='%a %c %g %l', initial=False):
        """
        Returns a summary of the interval.

        Args:
            fmt (str): A format string. Optional.
            initial (bool): Whether to capitalize the first letter.

        Returns:
            str: An English-language summary.
        """
        s = [i.summary(fmt=fmt, initial=initial) for i in self.components]
        summary = " with ".join(s)
        return "{0} m of {1}".format(self.thickness, summary)

    def __split_description(self, text):
        """
        Split a description into its components.
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

    def __parse_description(self, lexicon, max_component=1):
        """
        Turns a description into a lists of rocks. The items in the list
        are in the order they were found in the description, which is
        usually order of importance.
            """
        text = self.description
        components = []
        for p, part in enumerate(self.__split_description(text)):
            if p > max_component - 1:
                break
            components.append(Rock.from_text(part, lexicon))

        return components
