#!/usr/bin/env python3

__all__ = ['mei_to_ly', 'ly_to_mei', 'mei_to_abjad', 'abjad_to_mei', 'mei_to_lmei', 'lmei_to_mei']

from lychee.converters import *

INBOUND_CONVERTERS = {'lilypond': ly_to_mei.convert,
                      'abjad': abjad_to_mei.convert,
                      'mei': mei_to_lmei.convert}
'''
Mapping from the lowercase name of an inbound converter format to the :func:`convert` function that
converts from that format to Lychee-MEI.
'''
