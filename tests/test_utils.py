"""
Define a suite a tests for the utils module.
"""
import pytest
import numpy as np

from striplog.utils import null
from striplog.utils import partialmethod
from striplog.utils import rgb_to_hex, hex_to_rgb
from striplog.utils import hex_to_name, name_to_hex
from striplog.utils import hex_is_dark, text_colour_for_hex
from striplog.utils import list_and_add
from striplog.utils import tops_from_loglike
from striplog.utils import binary_dilation, binary_erosion


def test_null():
    """Test the null function on itself.
    """
    assert null(null) == null


def test_binary():
    arr = [1,0,0,0,1,1,1,0,1]
    assert np.all(binary_dilation(arr, 1) == arr)
    assert np.all(binary_dilation(arr, 3) == [1,1,0,1,1,1,1,1,1])
    assert np.all(binary_erosion(arr, 3) == [0,0,0,0,0,1,0,0,0])


def test_partial():
    """Pretty sure this test doesn't test what I need. See coverage report.
    """
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
    """Test colour conversions.
    """
    assert rgb_to_hex([0, 0, 0]) == '#000000'
    assert rgb_to_hex([0, 0.5, 0.5]) == '#008080'
    assert rgb_to_hex([255, 128, 128]) == '#ff8080'
    assert hex_to_rgb('#000000') == (0, 0, 0)
    assert hex_to_rgb('#ff8080') == (255, 128, 128)  # case

    # And exceptions:
    with pytest.raises(Exception):
        _ = rgb_to_hex([0, 0, -1])
        assert _

    with pytest.raises(Exception):
        _ = rgb_to_hex([0, 0, 256])
        assert _

    with pytest.raises(Exception):
        _ = rgb_to_hex([0, 0.1, 2])
        assert _


def test_names():
    """Test colour names.
    """
    assert name_to_hex('red') == '#ff0000'
    assert name_to_hex('Red') == '#ff0000'
    assert hex_to_name('#ff0000') == 'red'
    assert hex_to_name('#ff0000') == 'red'
    assert hex_to_name('cerulean') is None


def test_hex_is_dark():
    """Test ability to recover correct colour for text.
    """
    assert not hex_is_dark('#ffff00')
    assert hex_is_dark('#330000')
    assert text_colour_for_hex('#ffff00') == '#000000'
    assert text_colour_for_hex('#121111') == '#ffffff'


def test_list_and_add():
    a = ['this', 'that', 'other']
    b = 'those'
    assert len(list_and_add(b, b)) == 2
    assert len(list_and_add(a, b)) == 4
    assert len(list_and_add(b, a)) == 4


def test_tops_from_loglike():
    a = [1,1,1,2,2,2,-1,-1,-1,np.nan,np.nan,-2,-2,-2]
    tops, values = tops_from_loglike(a)
    assert len(values) == 5

    a = [1,1,1,2,2,2,-1,-1,-1,-2,-2,-2,-2,-2]
    tops, values = tops_from_loglike(a)
    assert len(values) == 4
