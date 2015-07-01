# -*- coding: utf 8 -*-
"""
Define a suite a tests for the utils module.
"""

from ..striplog.utils import rgb_to_hex


def test_tohex():
    black = rgb_to_hex([0, 0, 0])
    white = rgb_to_hex([255, 255, 255])
    pink = rgb_to_hex([255, 128, 128])

    assert black == '#000000'
    assert white == '#FFFFFF'
    assert pink == '#FF8080'
