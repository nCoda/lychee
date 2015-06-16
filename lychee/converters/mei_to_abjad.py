#!/usr/bin/env python3

from lychee.signals import inbound

def convert(**kwargs):
    '''
    Convert an MEI document into an Abjad document.

    :param document: The MEI document. Must be provided as a kwarg.
    :type document: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
    :returns: The corresponding MEI document.
    :rtype: object
    '''
    inbound.CONVERSION_STARTED.emit()
    print('{}.convert(document="{}")'.format(__name__, kwargs['document']))
    #inbound.CONVERSION_ERROR.emit()
    inbound.CONVERSION_FINISH.emit(converted='<Abjad stuff>')
    print('{}.convert() after finish signal'.format(__name__))
