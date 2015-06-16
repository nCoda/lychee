#!/usr/bin/env python3

from lychee.signals import inbound

def convert(**kwargs):
    '''
    Convert a LilyPond document into an MEI document.

    :param str document: The LilyPond document. Must be provided as a kwarg.
    :returns: The corresponding MEI document.
    :rtype: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
    '''
    inbound.CONVERSION_STARTED.emit()
    print('{}.convert(document="{}")'.format(__name__, kwargs['document']))
    #inbound.CONVERSION_ERROR.emit()
    inbound.CONVERSION_FINISH.emit(converted='<l-mei stuff>')
    print('{}.convert() after finish signal'.format(__name__))
