"""
Reader for template strings.

Replaces Mac OS newlines with \n characters.
"""
import re


def get_template(name):
    """
    Still unsure about best way to do this, hence cruft.
    """
    text = re.sub(r'\r\n', r'\n', name)
    text = re.sub(r'\{([FISDE°].*?)\}', r'{{\1}}', text)
    return text

__section = """~{name}_Parameter
{short} .   {source:16s} : {name} source          {S}
{short}D.   MD               : {name} depth reference {S}

~{name}_Definition
{short}T.M                   : {name} top depth       {F}
{short}B.M                   : {name} base depth      {F}
{short}D.                    : {name} description     {S}

~{name}_Data | {name}_Definition
{data}"""

section = get_template(__section)
