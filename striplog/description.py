"""
Defines descriptions.

:copyright: 2016 Agile Geoscience
:license: Apache 2.0
"""


class DescriptionError(Exception):
    """
    Generic error class.
    """
    pass


class Description(object):
    """
    Used to represent a description.

    Will contain text processing methods.
    """
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text
