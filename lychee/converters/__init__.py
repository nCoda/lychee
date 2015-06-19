#!/usr/bin/env python3

__all__ = ['mei_to_ly', 'ly_to_mei', 'mei_to_abjad', 'abjad_to_mei', 'mei_to_lmei', 'lmei_to_mei']

from lychee.converters import *
# TODO: we probably don't actually want to import all of these at runtime, because each convter
#       may have serious external dependencies

INBOUND_CONVERTERS = {'lilypond': ly_to_mei.convert,
                      'abjad': abjad_to_mei.convert,
                      'mei': mei_to_lmei.convert}
'''
Mapping from the lowercase name of an inbound converter format to the :func:`convert` function that
converts from that format to Lychee-MEI.
'''

OUTBOUND_CONVERTERS = {'lilypond': mei_to_ly.convert,
                       'abjad': mei_to_abjad.convert,
                       'mei': lmei_to_mei.convert}
'''
Mapping from the lowercase name of an outbound converter format to the :func:`convert` function that
converts from Lychee-MEI into hat format.
'''
