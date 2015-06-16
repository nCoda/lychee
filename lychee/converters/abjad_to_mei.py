#!/usr/bin/env python3

from lychee.signals import inbound

def convert(**kwargs):
    '''
    Convert an Abjad document into an MEI document.

    :param object document: The Abjad document. Must be provided as a kwarg.
    :returns: The corresponding MEI document.
    :rtype: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
    '''
    inbound.CONVERSION_STARTED.emit()
    print('lychee.converters.abjad_to_mei.convert({})'.format(5))
    #inbound.CONVERSION_ERROR.emit()
    inbound.CONVERSION_FINISH.emit()
    print('lychee.converters.abjad_to_mei.convert() after finish signal')
