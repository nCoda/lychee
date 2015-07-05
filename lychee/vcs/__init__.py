#!/usr/bin/env python3

from lychee.signals import vcs


def document_processor(**kwargs):
    vcs.STARTED.emit()
    print('{}.document_processor()'.format(__name__, kwargs))
    #vcs.ERROR.emit()
    vcs.FINISH.emit()
    print('{}.document_processor() after finish signal'.format(__name__))


vcs.START.connect(document_processor)
