#!/usr/bin/env python3

from lychee.signals import document


def document_processor(**kwargs):
    document.STARTED.emit()
    print('{}.document_processor()'.format(__name__, kwargs))
    #document.ERROR.emit()
    document.FINISH.emit()
    print('{}.document_processor() after finish signal'.format(__name__))


document.START.connect(document_processor)
