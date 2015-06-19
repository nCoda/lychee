#!/usr/bin/env python3

from lychee.signals import inbound, outbound


def inbound_views_processor(dtype, doc, converted, **kwargs):
    inbound.VIEWS_STARTED.emit()
    print('{}.inbound_views_processor("{}", "{}", "{}")'.format(__name__, dtype, doc, converted))
    #inbound.VIEWS_ERROR.emit()
    inbound.VIEWS_FINISH.emit(views_info='<serialized views info>')
    print('{}.inbound_views_processor() after finish signal'.format(__name__))

def outbound_views_processor(dtype, **kwargs):
    outbound.VIEWS_STARTED.emit()
    print('{}.outbound_views_processor("{}")'.format(__name__, dtype))
    #outbound.VIEWS_ERROR.emit()
    outbound.VIEWS_FINISH.emit(dtype=dtype, views_info='<serialized views info>')
    print('{}.outbound_views_processor() after finish signal'.format(__name__))


inbound.VIEWS_START.connect(inbound_views_processor)
outbound.VIEWS_START.connect(outbound_views_processor)
