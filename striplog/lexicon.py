#!/usr/bin/env python
# -*- coding: utf 8 -*-
"""
A lexicon is a dictionary of vocabulary to use for parsing
lithologic or stratigraphic decriptions. 

:copyright: 2015 Agile Geoscience
:license: Apache 2.0
"""

import json

import defaults


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
            setattr(self, k.lower(), v.lower())

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
