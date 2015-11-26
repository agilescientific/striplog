#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines intervals for holding components.

:copyright: 2015 Agile Geoscience
:license: Apache 2.0
"""
import operator
import re
import warnings
from functools import total_ordering

try:
    from functools import partialmethod
except:  # Python 2
    from utils import partialmethod

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
        if base is not None:
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

    def __repr__(self):
        s = str(self)
        return "Interval({0})".format(s)

    def __str__(self):
        s = "top: {top}, base: {base}, "
        s += "description: '{description}', "
        s += "components: {components}"
        return s.format(**self.__dict__)

    def __add__(self, other):
        """
        TODO:
            If adding components, should take account of 'amount', if present.
            Or 'proportion'? ...Could be specified by lexicon??
        """

        if isinstance(other, self.__class__):
            return self.union(other)

        elif isinstance(other, Component):
            top = self.top
            base = self.base
            d = self.description + ' with ' + other.summary()
            c = self.components + [other]
            return Interval(top, base, description=d, components=c)

        else:
            m = "You can only add components or intervals."
            raise IntervalError(m)

    # Must supply __eq__ and one other rich comparison for
    # the total_ordering function to provide the others.
    # Not sure if this should be comparing thicknesses, depths,
    # or...? Using elevation, so 'less than' means 'below'.
    # Note that it's only comparing tops to determine ordering.
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.top == other.top

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            if self.order == 'elevation':
                return self.top < other.top
            return self.top > other.top

    def _repr_html_(self):
        """
        Jupyter Notebook magic repr function.
        """
        items = ['top', 'description', 'summary', 'primary', 'base']
        rows = ''
        row = '<tr>{row1}<td><strong>{e}</strong></td><td>{v}</td></tr>'
        style = 'width:2em; background-color:#DDDDDD'
        extra = '<td style="{}" rowspan="{}"></td>'
        for i, e in enumerate(items):
            row1 = extra.format(style, len(items)) if not i else ''
            v = getattr(self, e)
            v = v._repr_html_() if e == 'primary' else v
            v = self.summary() if e == 'summary' else v
            rows += row.format(row1=row1, e=e, v=v)

        html = '<table>{}</table>'.format(rows)
        return html

    @property
    def primary(self):
        """
        Convenience function returning the first component.

        Returns:
            Component. The first one in the list of components.
        """
        if self.components:
            return self.components[0]
        else:
            return None

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

    @property
    def order(self):
        """
        Gives the order of this interval, based on relative values of
        top & base.
        """
        if self.top > self.base:
            return 'elevation'
        else:
            return 'depth'

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

    def invert(self, copy=False):
        """
        Inverts the interval. If it was depth-ordered (positive numbers
        increasing downwards.), it will now be elevation-ordered, and
        vice versa.

        Args:
            copy (bool): Whether to make a copy or not. Default: False.
        """
        if copy:
            d = self.__dict__.copy()
            del(d['top'])
            del(d['base'])
            return Interval(top=self.base, base=self.top, **d)
        else:
            old_base = self.base
            self.base = self.top
            self.top = old_base
            return

    def copy(self):
        """
        Returns a shallow copy of the interval.

        """
        return Interval(**self.__dict__.copy())

    def relationship(self, other):
        """
        Returns the relationship style.

        """
        o = {'depth': operator.lt, 'elevation': operator.gt}[self.order]
        top_inside = o(self.top, other.top) and o(other.top, self.base)
        base_inside = o(self.top, other.base) and o(other.base, self.base)
        above_below = o(other.top, self.top) and o(self.base, other.base)

        if top_inside and base_inside:
            return 'contains'
        elif above_below:
            return 'containedby'
        elif top_inside or base_inside:
            return 'partially'
        elif (self.top == other.base) or (self.base == other.top):
            return 'touches'
        else:
            return None

    def __overlaps(self, other, rel='any'):
        """
        Checks to see if and how two intervals overlap.

        """
        overlaps = ['partially', 'contains', 'containedby']
        acceptable = overlaps + ['touches', 'any']
        if rel not in acceptable:
            m = 'rel must be one of {}'.format(', '.join(acceptable))
            raise IntervalError(m)

        r = self.relationship(other)
        if r:
            if (r == rel) or ((rel == 'any') and (r in overlaps)):
                return True
        return False

    # Curry.
    any_overlaps = partialmethod(__overlaps, rel='any')
    partially_overlaps = partialmethod(__overlaps, rel='partially')
    completely_contains = partialmethod(__overlaps, rel='contains')
    is_contained_by = partialmethod(__overlaps, rel='containedby')
    touches = partialmethod(__overlaps, rel='touches')

    def __blend_descriptions(self, other):
        """
        Computes the description for combining two intervals. Make sure that
        the intervals are already adjusted to the correct thicknesses.

        Returns a string.
        """
        thin, thick = sorted([self, other], key=lambda k: k.thickness)
        total = thin.thickness + thick.thickness
        prop = 100 * thick.thickness / total

        d1 = thick.description.strip(' .,') or thick.summary()
        d2 = thin.description.strip(' .,') or thin.summary()
        if d1:
            d = '{:.1f}% {} with {:.1f}% {}'.format(prop, d1, 100-prop, d2)
        else:
            d = ''

        return d

    def _explode(self, other):
        """
        self must at least partially overlap other.

        If blend is False, you are essentially replacing self with other.

        Returns a tuple of Intervals.
        """
        if not self.order == other.order:
            m = 'self and other must have the same wayupness'
            raise IntervalError(m)

        uppermost = max(self, other).copy()
        lowermost = min(self, other).copy()  # Only based on tops.

        if self.partially_overlaps(other):
            upper, _ = uppermost.split_at(lowermost.top)
            middle, lower = lowermost.split_at(uppermost.base)
        else:
            upper_temp, lower = uppermost.split_at(lowermost.base)
            upper, _ = upper_temp.split_at(lowermost.top)
            middle = lowermost

        return upper, middle, lower  # middle has lowermost's properties

    def _combine(self, old_self, other, blend=True):
        """
        Private but not mangled function.

        Returns an Interval.
        """
        if blend:
            self.components = old_self.components + other.components
            self.description = old_self.__blend_descriptions(other)
        else:
            self.components = other.components
            self.description = other.description

        return self

    def intersect(self, other, blend=True):
        """
        self must at least partially overlap other.

        If blend is False, you are essentially replacing self with other.

        Returns an Interval.
        """
        if not self.any_overlaps(other):
            m = 'self must at least partially overlap other'
            raise IntervalError(m)

        _, intersection, _ = self._explode(other)

        return intersection._combine(self, other, blend=blend)

    def merge(self, other, blend=True):
        """
        self must at least partially overlap other.

        If blend is False, you are essentially replacing self with other.

        Returns a Striplog.
        """
        if not self.any_overlaps(other):
            m = 'self must at least partially overlap other'
            raise IntervalError(m)

        upper, middle, lower = self._explode(other)

        if self.top == upper.top:
            self_is_uppermost = True
        else:
            self_is_uppermost = False

        middle = middle._combine(self, other, blend=blend)

        if self.partially_overlaps(other) and (not blend):
            # Then we'll only have two pieces:
            if self_is_uppermost:
                result = [upper, other]
            else:
                result = [other, lower]
        else:
            result = [lower, middle, upper]

        from .striplog import Striplog  # Import here to avoid circular ref
        if self.order == 'depth':
            return Striplog(result[::-1])
        else:
            return Striplog(result)

    def union(self, other, blend=True):
        """
        Unions intervals. Self must at least touch or partially overlap other.

        Returns an Interval.
        """
        if not (self.touches(other) or self.any_overlaps(other)):
            m = 'self must at least touch or partially overlap other'
            raise IntervalError(m)

        top = max(self, other).top
        if self.partially_overlaps(other):
            bot = min(self, other).base
        else:
            bot = max(self, other).base

        result = self.copy()
        result.top = top
        result.base = bot

        return result._combine(self, other, blend=blend)

    def spans(self, d):
        """
        Determines if depth d is within this interval.

        """
        o = {'depth': operator.lt, 'elevation': operator.gt}[self.order]
        return (o(d, self.base) and o(self.top, d))

    def split_at(self, d):
        """
        Splits the interval. Returns a list of the two new intervals.

        Args:
            d (float): Level or 'depth' to split at.

        TODO:
            Should this return a Striplog, or just a tuple?

        """
        if not self.spans(d):
            m = 'd must be within interval'
            raise IntervalError(m)

        int1, int2 = self.copy(), self.copy()

        int1.base = d
        int2.top = d

        return int1, int2  # upper, lower

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
