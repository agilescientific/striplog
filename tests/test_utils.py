# -*- coding: utf 8 -*-
"""
Define a suite a tests for the utils module.
"""

from striplog.utils import null
from striplog.utils import partialmethod
from striplog.utils import rgb_to_hex, hex_to_rgb
from striplog.utils import hex_to_name, name_to_hex
from striplog.utils import hex_is_dark, text_colour_for_hex


def test_null():
    assert null(null) == null


def test_partial():
    def f(a, b):
        return a + b

    def g(a, b):
        return b

    p = partialmethod(f, b=0)
    q = partialmethod(g, b=None)

    # Can't see how to use utils.py lines 59-61.
    assert p(1)
    assert getattr(q, 'keywords', None)
    assert q(1) is None


def test_colours():
    assert rgb_to_hex([0, 0, 0]) == '#000000'
    assert rgb_to_hex([255, 128, 128]) == '#FF8080'
    assert hex_to_rgb('#000000') == (0, 0, 0)
    assert hex_to_rgb('#ff8080') == (255, 128, 128)  # case


def test_names():
    assert name_to_hex('red') == '#FF0000'
    assert name_to_hex('Red') == '#FF0000'
    assert hex_to_name('#FF0000') == 'red'
    assert hex_to_name('#ff0000') == 'red'
    assert hex_to_name('cerulean') is None


def test_hex_is_dark():
    assert not hex_is_dark('#FFFF00')
    assert hex_is_dark('#330000')
    assert text_colour_for_hex('#FFFF00') == '#000000'
    assert text_colour_for_hex('#121111') == '#FFFFFF'
