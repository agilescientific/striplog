# -*- coding: utf 8 -*-
"""
Define a suite a tests for the Legend module.
"""
import pytest

from striplog import Striplog
from striplog import Legend, Lexicon, Interval, Component
from striplog.legend import LegendError

legend = Legend.default()

imgfile = "tutorial/M-MG-70_14.3_135.9.png"
striplog = Striplog.from_img(imgfile, 14.3, 135.9, legend=legend)


# def test_legend_plot():

# def test_decor_plot():

@pytest.mark.mpl_image_compare(baseline_dir='baseline_images',
                               filename='five_thickest_ax.png')

def test_striplog_plot():
	"""Tests mpl image of striplog
	"""
	fig = striplog.thickest(n=5).plot(legend=legend, return_fig=True)
	return fig
