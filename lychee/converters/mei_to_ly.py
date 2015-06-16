#!/usr/bin/env python3

from lychee.signals import inbound

def convert(**kwargs):
    '''
    Convert an MEI document into a LilyPond document.

    :param document: The MEI document. Must be provided as a kwarg.
    :type document: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
    :returns: The corresponding LilyPond document.
    :rtype: str
    '''
    inbound.CONVERSION_STARTED.emit()
    print('lychee.converters.ly_to_mei.convert({})'.format(5))
    #inbound.CONVERSION_ERROR.emit()
    inbound.CONVERSION_FINISH.emit()
    print('lychee.converters.ly_to_mei.convert() after finish signal')
