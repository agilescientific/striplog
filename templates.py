# -*- coding: utf-8 -*-
"""
Reader for template strings.

Replaces Mac OS newlines with \n characters.
"""
import re


def get_template(name):
    with open(name + '_template.txt') as f:
        text = re.sub(r'\r\n', r'\n', f.read())
        text = re.sub(r'\{([FISDE°].*?)\}', r'{{\1}}', text)
        return text

LAS = get_template('LAS')
cuttings = get_template('cuttings')
lithology = get_template('lithology')
curve = get_template('curve')
