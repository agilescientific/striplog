#!/usr/bin/env python
# -*- coding: utf 8 -*-
"""
Helper functions for the striplog package.

"""

from matplotlib import colors


def hex_to_name(hexx):
    """
    Convert hex to a color name, using matplotlib's colour names.

    Args:
        hexx (str): A hexadecimal colour, starting with '#'.

    Returns:
        str: The name of the colour, or None if not found.
    """
    for n, h in colors.cnames:
        if h == hexx.upper():
            return n
    return None


def name_to_hex(name):
    """
    Convert a color name to hex, using matplotlib's colour names.

    Args:
        name (str): The name of a colour, e.g. 'red'.

    Returns:
        str: The hex code for the colour.
    """
    return colors.cnames[name].lower()


def rgb_to_hex(rgb):
    """
    Utility function to convert (r,g,b) triples to hex.
    http://ageo.co/1CFxXpO

    Args:
      rgb (tuple): A tuple or list of RGB values in the
        range 0-255 (i.e. not 0 to 1).

    Returns:
      str: The hex code for the colour.
    """
    h = '#%02x%02x%02x' % tuple(rgb)
    return h.upper()


def hex_to_rgb(hexx):
    """
    Utility function to convert hex to (r,g,b) triples.
    http://ageo.co/1CFxXpO

    Args:
        hexx (str): A hexadecimal colour, starting with '#'.

    Returns:
        tuple: The equivalent RGB triple, in the range 0 to 255.
    """
    h = hexx.strip('#')
    l = len(h)

    return tuple(int(h[i:i+l//3], 16) for i in range(0, l, l//3))
