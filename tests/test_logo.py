"""
Defines a suite a tests for images run with:

    py.test --mpl

To generate new test images, see the instructions in
striplog/run_tests.py

https://pypi.python.org/pypi/pytest-mpl/0.3
"""
import pytest

from striplog import logo


params = {'tolerance': 20,
          'savefig_kwargs': {'dpi': 100},
          }


@pytest.mark.mpl_image_compare(**params)
def test_striplog_logo():
    """
    Tests mpl image of striplog logo.
    """
    fig = logo.plot()
    return fig
