#!/usr/bin/env python3

from lychee.signals import inbound

def convert(**kwargs):
    '''
    Convert an MEI document into a Lychee-MEI document.

    :param document: The MEI document. Must be provided as a kwarg.
    :type document: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
    :returns: The corresponding Lychee-MEI document.
    :rtype: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
    '''
    inbound.CONVERSION_STARTED.emit()
    print('lychee.converters.mei_to_lmei.convert({})'.format(5))
    #inbound.CONVERSION_ERROR.emit()
    inbound.CONVERSION_FINISH.emit()
    print('lychee.converters.mei_to_lmei.convert() after finish signal')
