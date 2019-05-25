# -*- coding: utf-8 -*-
"""
Define a suite a tests for the canstrat reader.
"""
import pytest

from striplog import Striplog


def test_canstrat():
    """Read a file.
    """
    s = Striplog.from_canstrat('tests/data/test_canstrat.dat')
    assert len(s) == 28
    assert abs(s[3].data['grains_mm'] - 0.0012) < 0.0000001
