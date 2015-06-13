#!/usr/bin/env python3

from lychee import signals

# this is what starts a test "action"
signals.ACTION_START.emit(inbound_format='LilyPond')
