#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines intervals and rock for holding lithologies.

:copyright: 2015 Agile Geoscience
:license: Apache 2.0
"""
import re


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

    def summary(self, fmt=None, initial=True):
        """
        Given a rock dict and a format string,
        return a summary description of a rock.

        Args:
            rock (dict): A rock dictionary.
            fmt (str): Describes the format with a string. Use '%'
                to signal a field in the Rock, which is analogous 
                to a dictionary. If no format is given, you will 
                just get a list of attributes. 

        Returns:
            str: A summary string.

        Example:
        
            r = {'colour': 'Red',
                 'grainsize': 'VF-F',
                 'lithology': 'Sandstone'}

        summarize(r)  -->  'Red, vf-f, sandstone'
        """
        # TODO: Use nouns and adjectives properly.
        # TODO: Use {key} instead of %key.
        if not fmt:
            string, flist = '', []
            for item in self.__dict__:
                string += '{}, '
                flist.append(item)
            string = string.strip(', ')
        else:
            fmt = re.sub(r'%%', '_percent_', fmt)
            string = re.sub(r'\{(\w+)\}', '{}', fmt)
            string = re.sub(r'_percent_', '%', string)
            flist = re.findall(r'\{(\w+)\}', fmt)

        words = []
        for key in flist:
            word = self.__dict__.get(key.lower())
            if word and key[0].isupper():
                word = word.capitalize()
            if word and key.isupper():
                word = word.upper()
            if not word:
                word = ''
            words.append(word)

        summary = string.format(*words)

        if initial and summary:
            summary = summary[0].upper() + summary[1:]

        return summary
