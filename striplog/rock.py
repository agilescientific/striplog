#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines intervals and rock for holding lithologies.

:copyright: 2015 Agile Geoscience
:license: Apache 2.0
"""


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
            if k and v:
                setattr(self, k.lower(), v.lower())

    def __repr__(self):
        s = str(self)
        return "Rock({0})".format(s)

    def __str__(self):
        s = []
        for key in self.__dict__:
            t = "'{key}':'{value}'"
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
    def from_text(cls, text, lexicon, required=None, first_only=True):
        """
        Generate a Rock from a text string, using a Lexicon.

        Args:
            text (str): The text string to parse.
            lexicon (Lexicon): The dictionary to use for the 
                categories and lexemes. 
            first_only (bool): Whether to only take the first
                match of a lexeme against the text string.

        Returns:
            Rock: A rock object, or None if there was no 
                must-have field.
        """
        rock_dict = lexicon.get_component(text, first_only=first_only)
        if required and required not in rock_dict:
            return None
        else:
            return cls(rock_dict)

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

        TODO:
            Make the Rock completely agnostic to its contents.
            We should be able to use it for fossils, tops, whatever.

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
