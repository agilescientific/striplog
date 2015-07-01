# -*- coding: utf 8 -*-
"""
Define a suite a tests for the utils module.
"""

from striplog.utils import rgb_to_hex, hex_to_rgb
from striplog.utils import hex_to_name, name_to_hex


def test_colours():
    assert rgb_to_hex([0, 0, 0]) == '#000000'
    assert rgb_to_hex([255, 128, 128]) == '#FF8080'
    assert hex_to_rgb('#000000') == (0, 0, 0)
    assert hex_to_rgb('#ff8080') == (255, 128, 128)  # case


def test_names():
	assert name_to_hex('red') == '#FF0000'
	assert name_to_hex('Red') == '#FF0000'  # case
	assert hex_to_name('#FF0000') == 'red'
	assert hex_to_name('#ff0000') == 'red'  # case
