#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines components for holding properties of rocks or samples or whatevers.

:copyright: 2015 Agile Geoscience
:license: Apache 2.0
"""
import re
import warnings

from component import Component


class Rock(Component):
    """
    Graceful deprecation for old class name.
    """
    def __init__(self, *args, **kwargs):

        with warnings.catch_warnings():
            warnings.simplefilter("always")
            w = "The 'Rock' class was renamed 'Component'. "
            w += "Please update your code."
            warnings.warn(w, DeprecationWarning)

        Component.__init__(*args, **kwargs)
