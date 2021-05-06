"""
Define a suite a tests for the Position module.
"""
import pytest

from striplog import Position
from striplog.position import PositionError


def test_incomplete_error():
    """ Test the PositionError.
    """
    with pytest.raises(PositionError):
        Position(middle=None, upper=1)


def test_incomplete_coords_error():
    """ Test the PositionError.
    """
    with pytest.raises(PositionError):
        Position(middle=1, x=1000)


def test_position():
    """ Test intervals.
    """
    meta = {'character': 'erosive',
            'rugosity': '3 m',
            }
    position = Position(middle=None,
                        upper=1,
                        lower=2,
                        x=1000,
                        y=2000,
                        meta=meta)
    assert position.z == 1.5
    assert position.span == (2, 1)
    assert position.uncertainty == 1.0
    position.invert()
    assert position.span == (1, 2)


def test_position_html():
    """For jupyter notebook
    """
    position = Position(**{'upper': 75, 'lower': 85})
    html = """<table><tr><td><strong>upper</strong></td><td>75.0</td></tr><tr><td><strong>middle</strong></td><td></td></tr><tr><td><strong>lower</strong></td><td>85.0</td></tr></table>"""
    assert position._repr_html_() == html
