"""
Replaced by component.py. Kept this for graceful deprecation.

:copyright: 2015 Agile Geoscience
:license: Apache 2.0
"""
import warnings

from .component import Component


def Rock(*args, **kwargs):
    """
    Graceful deprecation for old class name.
    """

    with warnings.catch_warnings():
        warnings.simplefilter("always")
        w = "The 'Rock' class was renamed 'Component'. "
        w += "Please update your code."
        warnings.warn(w, DeprecationWarning, stacklevel=2)

    return Component(*args, **kwargs)
