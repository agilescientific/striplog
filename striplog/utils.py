#!/usr/bin/env python
# -*- coding: utf 8 -*-
"""
Helper functions for the striplog package.

"""
from string import Formatter
from functools import partial

import numpy as np

from . import defaults


class CustomFormatter(Formatter):

    def __init__(self):
        super(CustomFormatter, self).__init__()

    def get_field(self, field_name, args, kwargs):
        """
        Return an underscore if the attribute is absent.
        Not all components have the same attributes.
        """
        try:
            s = super(CustomFormatter, self)
            return s.get_field(field_name, args, kwargs)
        except KeyError:
            return ("_", field_name)

    def convert_field(self, value, conversion):
        """
        Define some extra field conversion functions.
        """
        try:  # If the normal behaviour works, do it.
            s = super(CustomFormatter, self)
            return s.convert_field(value, conversion)
        except ValueError:
            funcs = {'s': str,    # Default.
                     'r': repr,   # Default.
                     'a': ascii,  # Default.
                     'u': str.upper,
                     'l': str.lower,
                     'c': str.capitalize,
                     't': str.title,
                     'm': np.mean,
                     'µ': np.mean,
                     'v': np.var,
                     'd': np.std,
                     '+': np.sum,
                     '∑': np.sum,
                     'x': np.product,
                     }
            return funcs.get(conversion)(value)


class partialmethod(partial):
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return partial(self.func,
                       instance,
                       *(self.args or ()),
                       **(self.keywords or {})
                       )


def null(x):
    """
    Null function.
    """
    return x


def hex_to_name(hexx):
    """
    Convert hex to a color name, using matplotlib's colour names.

    Args:
        hexx (str): A hexadecimal colour, starting with '#'.

    Returns:
        str: The name of the colour, or None if not found.
    """
    for n, h in defaults.COLOURS.items():
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
    return defaults.COLOURS[name.lower()]


def rgb_to_hex(rgb):
    """
    Utility function to convert (r,g,b) triples to hex.
    http://ageo.co/1CFxXpO

    Args:
      rgb (tuple): A sequernce of RGB values in the
        range 0-255 or 0-1.

    Returns:
      str: The hex code for the colour.
    """
    r, g, b = rgb[:3]
    if 0 < r*g*b < 1:
        rgb = tuple([int(round(val * 255)) for val in [r, g, b]])
    else:
        rgb = (r, g, b)
    result = '#%02x%02x%02x' % rgb
    return result.upper()


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


def hex_is_dark(hexx, percent=50):
    """
    Function to decide if a hex colour is dark.

    Args:
        hexx (str): A hexadecimal colour, starting with '#'.

    Returns:
        bool: The colour's brightness is less than the given percent.
    """
    r, g, b = hex_to_rgb(hexx)
    luma = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 2.55  # per ITU-R BT.709

    return (luma < percent)


def text_colour_for_hex(hexx, percent=50, dark='#000000', light='#FFFFFF'):
    """
    Function to decide what colour to use for a given hex colour.

    Args:
        hexx (str): A hexadecimal colour, starting with '#'.

    Returns:
        bool: The colour's brightness is less than the given percent.
    """
    return light if hex_is_dark(hexx, percent=percent) else dark
