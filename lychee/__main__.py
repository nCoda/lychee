#!/usr/bin/env python3

from lychee import signals
from signals import outbound

# register these fake "listeners" that will pretend they want data in whatever formats
def generic_listener(dtype):
    print("I'm listening for {}!".format(dtype))
    outbound.I_AM_LISTENING.emit(dtype=dtype)

def abj_listener(**kwargs):
    generic_listener('abjad')

def ly_listener(**kwargs):
    generic_listener('lilypond')

def mei_listener(**kwargs):
    generic_listener('mei')

outbound.WHO_IS_LISTENING.connect(abj_listener)
outbound.WHO_IS_LISTENING.connect(ly_listener)
outbound.WHO_IS_LISTENING.connect(mei_listener)

# this is what starts a test "action"
signals.ACTION_START.emit(dtype='LilyPond', doc='c4. d8')
