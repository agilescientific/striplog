"""
Define a suite a tests for the Decor class in the LEgend module.
"""
import pytest

from striplog import Decor
from striplog import Legend
from striplog.legend import LegendError
from striplog import Component

r = {'colour': 'grey',
     'grainsize': 'vf-f',
     'lithology': 'sand'}

r3 = {'colour': 'red',
      'grainsize': 'vf-f',
      'lithology': 'sandstone'}


def test_decor():
    """Test decor basics.
    """
    rock = Component(r)
    rock3 = Component(r3)

    d = Decor({'colour': '#FF0000',
               'component': rock})
    d1 = Decor({'colour': '#F80',
               'component': rock3})
    d2 = Decor({'colour': '(255, 128, 0)',
               'component': rock3})
    d3 = Decor({'colour': 'orange',
               'component': rock3})

    l = d + d3
    assert isinstance(l, Legend)
    assert len(l) == 2
    assert d.rgb == (255, 0, 0)
    assert Decor.random(rock3).colour != ''
    assert d1.colour == '#ff8800'
    assert d2.colour == '#ff8000'
    assert d3.colour == '#ffa500'


def test_decor_html():
    """For jupyter notebook
    """
    r = {'lithology': 'sand'}
    rock = Component(r)
    d = {'color': '#267022', 'component': rock, 'width': 3}
    decor = Decor(d)
    component_row = """<tr><td><strong>component</strong></td><td style="color:black; background-color:white"><table><tr><td><strong>lithology</strong></td><td>sand</td></tr></table></td></tr>"""
    hatch_row = """<tr><td><strong>hatch</strong></td><td style="color:black; background-color:white">None</td></tr>"""
    colour_row = """<tr><td><strong>colour</strong></td><td style="color:#ffffff; background-color:#267022">#267022</td></tr>"""
    width_row = """<tr><td><strong>width</strong></td><td style="color:black; background-color:white">3.0</td></tr>"""
    html = decor._repr_html_()
    assert component_row in html
    assert hatch_row in html
    assert colour_row in html
    assert width_row in html


def test_decor_errors():
    """Test decor errors.
    """
    rock = Component(r)

    # No component
    with pytest.raises(LegendError):
        Decor({'colour': 'red'})

    # No decoration
    with pytest.raises(LegendError):
        Decor({'component': rock})

    # Bad colour
    with pytest.raises(LegendError):
        Decor({'colour': 'blurple',
               'component': rock})
