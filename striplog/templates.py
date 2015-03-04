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

"""LAS = get_template('LAS')
cuttings = get_template('cuttings')
lithology = get_template('lithology')
curve = get_template('curve')"""


LAS = """~Version
VERS .              3.0       :CWLS LOG ASCII STANDARD - VERSION 3.0
WRAP .               NO       :ONE LINE PER DEPTH STEP
DLM  .            COMMA       :DELIMITING CHARACTER
PROG .  {prog:>12s}       :LAS Program name and version
CREA . {date:16s}     :LAS Creation date {{YYYY/MM/DD hh:mm}}

~Well 
#MNEM .UNIT  DATA             DESCRIPTION
#---- ------ --------------   -----------------------------
STRT .M      {start:8.3f}       :START DEPTH
STOP .M      {stop:8.3f}       :STOP DEPTH
STEP .M      {step:9.4f}      :STEP
NULL .       {null:9.4f}      :NULL VALUE

WELL .       {well:20s}  :WELL
FLD  .       UNDEFINED             :FIELD
CTRY .       CA                    :COUNTRY

PROV .       NOVA SCOTIA           :PROVINCE
UWI  .       {uwi:21s}  :UNIQUE WELL ID
LIC  .       {lic:21s}  :LICENSE NUMBER

~Parameter 
#MNEM .UNIT  VALUE            DESCRIPTION
#---- ------ --------------   -----------------------------

#Required parameters
RUN  .        ONE             :RUN NUMBER
PDAT .        GL              :PERMANENT DATUM
APD  .M       {KBRGL:8.3f}        :ABOVE PERM DATUM
DREF .        KB              :DEPTH REFERENCE
EREF .M       {KBRSS:8.3f}        :ELEVATION OF DEPTH

#Remarks
R1   .         Lithologic descriptions from cuttings.        :REMARK LINE 1
R2   .         Striplog lithologies                          :REMARK LINE 2
R3   .                                                       :REMARK LINE 3
R4   .                                                       :REMARK LINE 4
R5   .                                                       :REMARK LINE 5

{lith}

{curve}"""

cuttings = """~Cuttings_Parameter
CUT  .   {source}         : Cuttings source          {S}
CUTDR.   MD               : Cuttings depth reference {S}

~Cuttings_Definition
CUTT .M                   : Cuttings top depth       {F}
CUTB .M                   : Cuttings base depth      {F}
CUTD .                    : Cuttings description     {S}

~Cuttings_Data | Cuttings_Definition
{data}"""


lithology = """~Lithology_Parameter
LITH .   {source:16s} : Lithology source          {S}
LITHD.   MD               : Lithology depth reference {S}

~Lithology_Definition
LITHT.M                   : Lithology top depth       {F}
LITHB.M                   : Lithology base depth      {F}
LITHN.                    : Lithology name            {S}

~Lithology_Data | Lithology_Definition
{data}"""

curve = """~Curve
#MNEM .UNIT  LOG CODES        DESCRIPTION
#---- ------ --------------   -----------------------------
DEPT .m        00 001 00 00               :Depth Index - Measured Depth       
LITH .         00 000 00 00               :See remarks

~Ascii
{logs}"""
