#!/usr/bin/env python3


class Document(object):
    '''
    Object representing an MEI document. Use methods prefixed with ``get`` to obtain portions of
    the document, automatically loading from files if required. Use methods preifxed with ``put``
    to submit a new portion to *replace* the existing portion outright.
    '''

    def __init__(self):
        '''
        The initialization method accepts no arguments.
        '''
        pass

    def get_everything(self):
        '''
        Load all portions of the MEI document from files. This method effectively caches the
        document in memory for faster access later.

        .. note:: Unlike the other ``get``-prefixed methods, this method returns nothing.
        '''
        pass

    def get_head(self):
        '''
        Load and return the MEI header metadata.

        :returns: The ``<head>`` portion of the MEI document.
        :rtype: :class:`lxml.etree.Element`
        '''
        pass

    def put_head(self, new_head):
        '''
        Save new header metadata.

        :param: new_head: A ``<head>`` element that should replace the existing one.
        :type new_head: :class:`lxml.etree.Element`
        '''
        pass

    def get_ui(self):
        '''
        Load and return Lychee-specific user interface data.

        :returns: Some element... ???
        :rtype: :class:`lxml.etree.Element`
        '''
        pass

    def put_ui(self, new_ui):
        '''
        Save new Lychee-specific user interface data.

        :param new_ui: Some element... ???
        :type new_ui: :class:`lxml.etree.Element`
        '''
        pass

    def get_score(self):
        '''
        Load and return the whole score, excluding metadata and "inactive" ``<section>`` elements.

        :returns: A ``<music>`` element.
        :rtype: :class:`lxml.etree.Element`
        '''
        pass

    def put_score(self, new_music):
        '''
        Save a new score in place of the existing one.

        :param new_music:
        :type new_music: :class:`lxml.etree.Element`
        '''
        pass

    def get_section(self, section_id):
        '''
        Load and return a section of the score.

        Returns ``None`` if there is no ``<section>`` with the given ``@xml:id``.

        :returns: The section with an ``@xml:id`` matching ``section_id``.
        :rtype: :class:`lxml.etree.Element`
        '''
        raise NotImplementedError('call get_score()')

    def put_section(self, section_id, new_section):
        '''

        In the future, you will be able to submit a section that is an element other than
        ``<section>``. For now, doing so will raise a :exc:`NotImplementedError`.

        :param new_section: A replacement for the section with ``section_id``.
        :type new_section: :class:`lxml.etree.Element`
        '''
        raise NotImplementedError('call put_score()')
