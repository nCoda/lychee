#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/test/test_registrar.py
# Purpose:                Tests for the "registrar" module.
#
# Copyright (C) 2016 Christopher Antila
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------
'''
Tests for the "registrar" module.
'''

from lxml import etree
import pytest

from lychee.converters.outbound import document as docout
from lychee import exceptions


class TestFormatPerson(object):
    '''
    Tests for document_outbound.format_person().
    '''

    def test_returns_none(self):
        '''
        When the argument is ``None``, format_person() should return ``None``.

        But when the argument is another invalid type, ``None`` is not returned.
        '''
        assert docout.format_person(None) is None
        with pytest.raises(AttributeError):
            docout.format_person(5)

    def test_full_persname(self):
        '''
        When given a full <persName> element without @nymref, the output is correct.
        '''
        person = etree.fromstring('''
            <mei:persName xml:id="p93773" xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:persName type="full">Danceathon Smith</mei:persName>
                <mei:persName type="given">Danceathon</mei:persName>
                <mei:persName type="family">Smith</mei:persName>
                <mei:persName type="other">Smanceathon Dith</mei:persName>
            </mei:persName>
            ''')
        expected = {'id': 'p93773', 'full': 'Danceathon Smith', 'given': 'Danceathon',
            'family': 'Smith', 'other': 'Smanceathon Dith'}
        actual = docout.format_person(person)
        assert expected == actual

    def test_with_nymref_1(self):
        '''
        When the <persName> element has a @nymref that starts with #, the output is correct.
        '''
        person = etree.fromstring('''
            <mei:persName nymref="#p93773" xmlns:mei="http://www.music-encoding.org/ns/mei"/>
            ''')
        expected = {'id': 'p93773'}
        actual = docout.format_person(person)
        assert expected == actual

    def test_with_nymref_2(self):
        '''
        When the <persName> element has a @nymref that doesn't start with #, the output is correct.
        '''
        person = etree.fromstring('''
            <mei:persName nymref="p93773" xmlns:mei="http://www.music-encoding.org/ns/mei"/>
            ''')
        expected = {'id': 'p93773'}
        actual = docout.format_person(person)
        assert expected == actual

    def test_ignore_bad_tags(self):
        '''
        When the full <persName> element contains unrelated elements, they are ignored.
        '''
        person = etree.fromstring('''
            <mei:persName xml:id="p93773" xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:persName type="full">Danceathon Smith</mei:persName>
                <mei:occupation type="lifelong">Speedboat Racer</mei:occupation>
            </mei:persName>
            ''')
        expected = {'id': 'p93773', 'full': 'Danceathon Smith'}
        actual = docout.format_person(person)
        assert expected == actual

    def test_ignore_bad_type(self):
        '''
        When the full <persName> element contains a <persName> with unknown @type, it is ignored.
        '''
        person = etree.fromstring('''
            <mei:persName xml:id="p93773" xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:persName type="full">Danceathon Smith</mei:persName>
                <mei:persName type="childhood">fffffffffffffffffff</mei:persName>
            </mei:persName>
            ''')
        expected = {'id': 'p93773', 'full': 'Danceathon Smith'}
        actual = docout.format_person(person)
        assert expected == actual

    def test_no_children_1(self):
        '''
        When the <persName> element has no child elements, or @xml:id or @nymref attribute.
        '''
        person = etree.fromstring('''
            <mei:persName xml:id="p93773" xmlns:mei="http://www.music-encoding.org/ns/mei"/>
            ''')
        with pytest.raises(exceptions.LycheeMEIWarning) as exc:
            docout.format_person(person)
        assert docout._MISSING_PERS_NAME_DATA == exc.value[0]

    def test_no_children_2(self):
        '''
        When the <persName> element has an @xml:id and one child element but it is not relevant.
        '''
        person = etree.fromstring('''
            <mei:persName xml:id="p93773" xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:score>GOOOOOAAAAAAAAAAL!!!!</mei:score>
            </mei:persName>
            ''')
        with pytest.raises(exceptions.LycheeMEIWarning) as exc:
            docout.format_person(person)
        assert docout._MISSING_PERS_NAME_DATA == exc.value[0]


class TestFormatTitleStmt(object):
    '''
    Tests for document_outbound.format_title_stmt().
    '''

    def test_returns_none(self):
        '''
        When the argument is ``None``, format_title_stmt() should return ``None``.

        But when the argument is another invalid type, ``None`` is not returned.
        '''
        assert docout.format_title_stmt(None) is None
        with pytest.raises(AttributeError):
            docout.format_title_stmt(5)

    def test_full_title(self):
        '''
        When given a full <titleStmt> element with all valid children, it's correct.
        '''
        title = etree.fromstring('''
            <mei:titleStmt xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:title type="main">Test Score in Lychee-MEI</mei:title>
                <mei:title type="subordinate">An experiment with XML.</mei:title>
                <mei:title type="abbreviated">Lychee-MEI Test</mei:title>
                <mei:title type="alternative">Some Excerpts of Sibelius' Fifth Symphony</mei:title>
            </mei:titleStmt>
            ''')
        expected = {
            'main': 'Test Score in Lychee-MEI',
            'subordinate': 'An experiment with XML.',
            'abbreviated': 'Lychee-MEI Test',
            'alternative': "Some Excerpts of Sibelius' Fifth Symphony",
        }
        actual = docout.format_title_stmt(title)
        assert expected == actual

    def test_ignore_bad_tags(self):
        '''
        When given <titleStmt> element with unknown children, they're ignored.
        '''
        title = etree.fromstring('''
            <mei:titleStmt xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:title type="main">Test Score in Lychee-MEI</mei:title>
                <mei:note pname="f" oct="2"/>
            </mei:titleStmt>
            ''')
        expected = {'main': 'Test Score in Lychee-MEI'}
        actual = docout.format_title_stmt(title)
        assert expected == actual

    def test_ignore_bad_type(self):
        '''
        When given <titleStmt> element where the child has an unknown @type, it's ignored.
        '''
        title = etree.fromstring('''
            <mei:titleStmt xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:title type="main">Test Score in Lychee-MEI</mei:title>
                <mei:title type="silly">Direct Deposit Enrolment Form</mei:title>
            </mei:titleStmt>
            ''')
        expected = {'main': 'Test Score in Lychee-MEI'}
        actual = docout.format_title_stmt(title)
        assert expected == actual

    def test_ignore_no_children_1(self):
        '''
        When given <titleStmt> element where the only child has an unknown @type, LycheeMEIWarning.
        '''
        title = etree.fromstring('''
            <mei:titleStmt xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:title type="silly">Direct Deposit Enrolment Form</mei:title>
            </mei:titleStmt>
            ''')
        with pytest.raises(exceptions.LycheeMEIWarning) as exc:
            docout.format_title_stmt(title)
        assert docout._MISSING_TITLE_DATA == exc.value[0]

    def test_ignore_no_children_2(self):
        '''
        When given <titleStmt> element where there are no children, LycheeMEIWarning.
        '''
        title = etree.fromstring('''
            <mei:titleStmt xmlns:mei="http://www.music-encoding.org/ns/mei"/>
            ''')
        with pytest.raises(exceptions.LycheeMEIWarning) as exc:
            docout.format_title_stmt(title)
        assert docout._MISSING_TITLE_DATA == exc.value[0]
