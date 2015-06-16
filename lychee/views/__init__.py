#!/usr/bin/env python3

from lychee.signals import inbound


def inbound_views_processor(dtype, doc, converted, **kwargs):
    inbound.VIEWS_STARTED.emit()
    print('{}.inbound_views_processor("{}", "{}", "{}")'.format(__name__, dtype, doc, converted))
    #inbound.VIEWS_ERROR.emit()
    inbound.VIEWS_FINISH.emit(views_info='<serialized views info>')
    print('{}.inbound_views_processor() after finish signal'.format(__name__))


inbound.VIEWS_START.connect(inbound_views_processor)
