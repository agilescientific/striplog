#!/usr/bin/env python
# -*- coding: utf 8 -*-
"""
Run all the tests.

This is the same as doing this on the command line:

  py.test --mpl --cov striplog

We have to run tests this way because we need to set the
matplotlib backend for travis.
"""
import pytest
import matplotlib
matplotlib.use('agg')

pytest.main("--mpl --cov striplog")
