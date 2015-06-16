#!/usr/bin/env python3

from lychee import signals

# this is what starts a test "action"
signals.ACTION_START.emit(dtype='LilyPond', doc='c4. d8')
