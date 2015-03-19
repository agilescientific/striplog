#!/usr/bin/env python
# -*- coding: utf 8 -*-
"""
A vocabulary for parsing lithologic or stratigraphic decriptions. 

:copyright: 2015 Agile Geoscience
:license: Apache 2.0
"""

import json
import warnings
import re

import defaults

SPECIAL = ['synonyms', 'parts_of_speech']


class LexiconError(Exception):
    pass


class Lexicon(object):
    """
    A Lexicon is a dictionary of 'types' and regex patterns.

    Most commonly you will just load the default one.

    Args:
        params (dict): The dictionary to use.
    """

    def __init__(self, params):
        for k, v in params.items():
            k = re.sub(' ', '_', k)
            setattr(self, k, v)

        if not params.get('synonyms'):
            self.synonyms = None

        if not params.get('parts_of_speech'):
            self.parts_of_speech = None

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        keys = self.__dict__.keys()
        counts = [len(v) for k, v in self.__dict__.items()]
        s = "Lexicon("
        for i in zip(keys, counts):
            s += "'{0}': {1} items, ".format(*i)
        s += ")"
        return s

    @classmethod
    def default(cls):
        return cls(defaults.LEXICON)

    @classmethod
    def from_json_file(cls, json_file):
    	"""
    	Load a lexicon from a JSON file.

    	Args:
    	    json_file (str): The path to a JSON dump.
    	"""
    	with open('lexicon.json', 'r') as fp:
            return cls(json.load(fp))

    def find_word_groups(self, text, category, proximity=2):
        """
        Given a string and a category, finds and combines words into
        groups based on their proximity.

        Args:
            text (str): Some text.
            tokens (list): A list of regex strings.

        Returns:
            list. The combined strings it found.

        Example:
            COLOURS = [r"red(?:dish)?", r"grey(?:ish)?", r"green(?:ish)?"]
            s = 'GREYISH-GREEN limestone with RED or GREY sandstone.'
            find_word_groups(s, COLOURS) --> ['greyish green', 'red', 'grey']
        """
        f = re.IGNORECASE
        words = getattr(self, category)
        regex = re.compile(r'(\b' + r'\b|\b'.join(words) + r'\b)', flags=f)
        candidates = regex.finditer(text)

        starts, ends = [], []
        groups = []

        for item in candidates:
            starts.append(item.span()[0])
            ends.append(item.span()[1])
            groups.append(item.group().lower())

        new_starts = []  # As a check only.
        new_groups = []  # This is what I want.

        skip = False
        for i, g in enumerate(groups):
            if skip:
                skip = False
                continue
            if (i < len(groups)-1) and (starts[i+1]-ends[i] <= proximity):
                if g[-1] == '-':
                    sep = ''  # Don't insert spaces after hyphens.
                else:
                    sep = ' '
                new_groups.append(g + sep + groups[i+1])
                new_starts.append(starts[i])
                skip = True
            else:
                if g not in new_groups:
                    new_groups.append(g)
                    new_starts.append(starts[i])
                skip = False

        return new_groups

    def find_synonym(self, word):
        """
        Given a string and a dict of synonyms, returns the 'preferred'
        word.

        Args:
            word (str): A word.

        Returns:
            str: The preferred word, or the input word if not found.

        Example:
            >>> syn = {'snake': ['python', 'adder']}
            >>> find_synonym('adder', syn)
            'snake'
            >>> find_synonym('rattler', syn)
            'rattler'
        """
        if self.synonyms:
            # Make the reverse look-up table.
            reverse_lookup = {}
            for k, v in self.synonyms.items():
                for i in v:
                    reverse_lookup[i] = k

            # Now check words against this table.
            if word in reverse_lookup:
                return reverse_lookup[word]

        return word

    def get_component(self, text, required=False, first_only=True):
        """
        Takes a piece of text representing a lithologic description for one
        component of a rock, e.g. "Red vf-f sandstone" and turns it into a
        dictionary of attributes.

        TODO:
            Generalize this so that we can use any types of word, as specified
            in the lexicon.
        """
        component = {}

        for i, (category, words) in enumerate(self.__dict__.items()):

            # There is probably a more elegant way to do this.
            if category in SPECIAL:
                # There are special entries in the lexicon.
                continue

            groups = self.find_word_groups(text, category)
            # Could ask if we really want groups, or just words. Then need:        
            # p = re.compile(r'(\b' + r'\b|\b'.join(lithologies) + r'\b)', flags=f)
            #words = p.findall(text)

            if groups and first_only:
                groups = groups[:1]
            elif groups:
                # groups = groups
                pass
            else:
                groups = [None]
                if required:
                    with warnings.catch_warnings():
                        warnings.simplefilter("always")
                        w = "No lithology in lexicon matching '{0}'".format(text)
                        warnings.warn(w)

            filtered = [self.find_synonym(i) for i in groups]
            if first_only:
                component[category] = filtered[0]
            else:
                component[category] = filtered

        return component

    @property
    def categories(self):
        """
        Lists the categories in the lexicon, except the
        optional categories.

        Returns:
            list: A list of strings of category names.
        """
        keys = [k for k in self.__dict__.keys() if k not in SPECIAL]
        return keys
