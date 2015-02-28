#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines intervals and rock for holding lithologies.

:copyright: 2015 Agile Geoscience
:license: Apache 2.0
"""

import re
import warnings

from utils import find_word_groups, find_synonym


class RockError(Exception):
    pass


class Rock(object):
    """
    Initialize with a dictionary of properties. You can use any
    properties you want, but the following are recognized by
    the summary() method:

        - lithology: a simple one-word rock type
        - colour, e.g. 'grey'
        - grainsize or range, e.g. 'vf-f'
        - modifier, e.g. 'rippled'
        - quantity, e.g. '35%', or 'stringers'
        - description, e.g. from cuttings

    You can include as many other things as you want, e.g.

        - porosity
        - cementation
        - lithology code

    """

    def __init__(self, properties):
        for k, v in properties.items():
            setattr(self, k.lower(), v.lower())

    def __repr__(self):
        s = str(self)
        return "Rock({0})".format(s)

    def __str__(self):
        s = []
        for key in self.__dict__:
            t = "{key}='{value}'"
            s.append(t.format(key=key, value=self.__dict__[key]))
        return ', '.join(s)

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
    def __parse_component(self, text, lexicon, first_only=True):
        """
        Takes a piece of text representing a lithologic description for one
        component of a rock, e.g. "Red vf-f sandstone" and turns it into a
        Rock object.
        """
        lithologies = lexicon['lithologies']
        amounts = lexicon['amounts']
        colours = lexicon['colours']
        grainsizes = lexicon['grainsizes']

        component = {}

        f = re.IGNORECASE
        p = re.compile(r'(\b' + r'\b|\b'.join(lithologies) + r'\b)', flags=f)
        l = p.findall(text)
        if l:
            if first_only:
                lith = [l[0]]  # First lithology only
            else:
                lith = l       # Will give a list of liths
        else:
            with warnings.catch_warnings():
                warnings.simplefilter("always")
                w = "No lithology in lexicon matching '{0}'".format(text)
                warnings.warn(w)
            lith = [None]

        lith = [find_synonym(i) for i in lith]
        if first_only:
            component['lithology'] = lith[0]
        else:
            component['lithology'] = lith[:]

        # Get 'amount' descriptor for component.
        p = re.compile(r'(\b' + r'\b|'.join(amounts) + r'\b)', flags=f)
        a = p.findall(text)
        if a:
            if first_only:
                component['amount'] = a[0]
            else:
                component['amount'] = a

        # Get colours of this component.
        c = find_word_groups(text, colours)
        if c:
            if first_only:
                component['colour'] = c[0]
            else:
                component['colour'] = c

        # Get grainsize of this component.
        g = find_word_groups(text, grainsizes)
        if g:
            if first_only:
                component['grainsize'] = g[0]
            else:
                component['grainsize'] = g

        return component

    @classmethod
    def from_text(cls, text, lexicon, first_only=True):
        rock_dict = cls.__parse_component(text, lexicon, first_only=first_only)
        if rock_dict['lithology']:
            return cls(rock_dict)
        else:
            return None

    def summary(self, fmt='%C %g %l', initial=True):
        """
        Given a rock dict and a format string,
        return a summary description of a rock.

        Args:
        rock (dict): A rock dictionary.
        fmt (str): Describes the format with
            a = amount
            c = colour
            g = grainsize
            l = lithology

        Returns:
        str. A summary string.

        Example:
        r = {'colour': 'Red',
             'grainsize': 'VF-F',
             'lithology': 'Sandstone'}

        summarize(r)  -->  'Red vf-f sandstone'
        """
        rock_dict = self.__dict__

        fields = {'a': 'amount',
                  'c': 'colour',
                  'g': 'grainsize',
                  'l': 'lithology'
                  }

        flist = fmt.split('%')

        fmt_items = []
        fmt_string = flist.pop(0)

        skip = 0
        for i, item in enumerate(flist):
            this_item = rock_dict.get(fields[item[0].lower()])
            if this_item:
                this_item = this_item.lower()
                if item.isupper():
                    this_item = this_item.capitalize()
                fmt_items.append(this_item)
                fmt_string += '{' + str(i-skip) + '}' + item[1:]
            else:
                skip += 1

        # The star trick lets us unpack from a list.
        summary = fmt_string.format(*fmt_items)

        if initial and summary:
            summary = summary[0].upper() + summary[1:]

        return summary
