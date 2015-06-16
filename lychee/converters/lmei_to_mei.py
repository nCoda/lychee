#!/usr/bin/env python3

from lychee.signals import inbound

def convert(**kwargs):
    '''
    Convert a Lychee-MEI document into an MEI document.

    :param document: The Lychee-MEI document. Must be provided as a kwarg.
    :type document: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
    :returns: The corresponding MEI document.
    :rtype: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
    '''
    inbound.CONVERSION_STARTED.emit()
    print('{}.convert(document="{}")'.format(__name__, kwargs['document']))
    #inbound.CONVERSION_ERROR.emit()
    inbound.CONVERSION_FINISH.emit(converted='<mei stuff>')
    print('{}.convert() after finish signal'.format(__name__))
