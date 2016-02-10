# -*- coding: utf 8 -*-
"""
Defines a suite a tests for images run with:

    py.test --mpl

To generate new test images, see the instructions in
striplog/run_tests.py

https://pypi.python.org/pypi/pytest-mpl/0.3
"""
from striplog import Striplog
from striplog import Legend, Component, Decor

import matplotlib.pyplot as plt
import pytest

params = {'tolerance': 20,
          'savefig_kwargs': {'dpi': 100},
          }


@pytest.mark.mpl_image_compare(**params)
def test_striplog_plot():
    """
    Tests mpl image of striplog
    """
    legend = Legend.builtin('NSDOE')

    imgfile = "tutorial/M-MG-70_14.3_135.9.png"

    striplog = Striplog.from_img(imgfile, 14.3, 135.9, legend=legend)

    fig = striplog.thickest(n=5).plot(legend=legend, return_fig=True)
    return fig


@pytest.mark.mpl_image_compare(**params)
def test_decor_plot():
    """
    Tests mpl image of decor
    """
    r = {'colour': 'grey',
         'grainsize': 'vf-f',
         'lithology': 'sand'}

    rock = Component(r)

    d = {'color': '#86F0B6',
         'component': rock,
         'width': 3}

    decor = Decor(d)

    fig = plt.figure(figsize=(4, 1))
    fig = decor.plot(fmt="{lithology!t} {colour} {grainsize}", fig=fig)
    return fig


@pytest.mark.mpl_image_compare(**params)
def test_pattern_fills():
    """
    Tests mpl image of decor
    """
    hatches = "pctLbs!=v^"
    decors = [Decor({'component': Component({'hatch': h}), 'hatch': h, 'colour': '#eeeeee'}) for h in hatches]

    fig = plt.figure(figsize=(1, 12))
    for i, d in enumerate(decors):
        ax = fig.add_subplot(len(decors), 1, i+1)
        ax = d.plot(ax=ax, fmt='')
    return fig
