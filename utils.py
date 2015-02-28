# -*- coding: utf 8 -*-
"""
Helper functions.

"""
import re

import xlrd

from defaults import SYNONYMS
from matplotlib import colors


def hex_to_name(hexx):
    """
    Convert hex to a color name, using matplotlib's colour names.
    """
    for n, h in colors.cnames:
        if h == hexx.upper():
            return n
    return None


def name_to_hex(name):
    """
    Convert a color name to hex, using matplotlib's colour names.
    """
    return colors.cnames[name].lower()


def rgb_to_hex(rgb):
    """
    Utility function to convert (r,g,b) triples to hex.
    http://ageo.co/1CFxXpO

    """
    h = '#%02x%02x%02x' % tuple(rgb)
    return h.upper()


def hex_to_rgb(hexx):
    """
    Utility function to convert hex to (r,g,b) triples.
    http://ageo.co/1CFxXpO
    """
    h = hexx.strip('#')
    l = len(h)

    return tuple(int(h[i:i+l//3], 16) for i in range(0, l, l//3))


def get_abbreviations_from_xls(fname):
    """
    Given a filename to an Excel spreadsheet containing abbreviations,
    return a dictionary with abbrev:definition key:value pairs.
    """
    book = xlrd.open_workbook(fname)
    abbreviations = {}
    for s in range(book.nsheets):
        sh = book.sheet_by_index(s)
        abbrs = [c.value.encode('utf-8') for c in sh.col(0)]
        defns = [c.value.encode('utf-8') for c in sh.col(1)]
        for i, a in enumerate(abbrs):
            abbreviations[a] = defns[i]

    return abbreviations


def find_word_groups(text, tokens, proximity=2):
    """
    Given a string and a list of regex tokens, finds and combines words into
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
    regex = re.compile(r'(\b' + r'\b|\b'.join(tokens) + r'\b)', flags=f)
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
            new_groups.append(g + "-" + groups[i+1])
            new_starts.append(starts[i])
            skip = True
        else:
            if g not in new_groups:
                new_groups.append(g)
                new_starts.append(starts[i])
            skip = False

    return new_groups


def find_synonym(word, synonyms=SYNONYMS):

    # Make the reverse look-up table.
    reverse_lookup = {}
    for k, v in synonyms.iteritems():
        for i in v:
            reverse_lookup[i] = k

    # Now check words against this table.
    if word in reverse_lookup:
        return reverse_lookup[word]
    else:
        return word
