#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/lmei_to_mei.py
# Purpose:                Converts a Lychee-MEI document to a more conventional MEI document.
#
# Copyright (C) 2016, 2017 Christopher Antila
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
Convert a Lychee-MEI document to a standard MEI document.

.. danger:: This module is not fully implemented yet.

.. warning::
    This module is intended for internal *Lychee* use only, so the API may change without notice.
    If you wish to use this module outside *Lychee*, please contact us to discuss the best way.

.. tip::
    We recommend that you use the converters indirectly.
    Refer to :ref:`how-to-use-converters` for more information.

.. note:: This is an outbound converter that does not emit signals directly. Refer to the
    :mod:`lychee.signals.outbound` module for more information.
'''

from fractions import Fraction

from lxml import etree

from lychee import exceptions
from lychee.namespaces import mei, xml

_ERR_INPUT_NOT_SECTION = 'LMEI-to-MEI did not receive a <section>'

_DURATION_HAVING_ELEMENTS = (mei.CHORD, mei.NOTE, mei.REST, mei.SPACE)


def convert(document, **kwargs):
    '''
    Convert a Lychee-MEI document into an MEI document.

    :param document: The Lychee-MEI document.
    :type document: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
    :returns: The corresponding MEI document.
    :rtype: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
    :raises: :exc:`lychee.exceptions.OutboundConversionError` when there is a forseeable error.
    '''
    if isinstance(document, etree._Element) and mei.SECTION == document.tag:
        return convert_raw(document)
    else:
        raise exceptions.OutboundConversionError(_ERR_INPUT_NOT_SECTION)


def convert_raw(document):
    '''
    Convert a Lychee-MEI document into an MEI document without verifying that it is an MEI section.
    '''
    document = create_measures(document)
    rewrite_beam_spans(document)
    return wrap_section_element(document)


def wrap_section_element(section):
    '''
    Wrap a <section> element in <score>, <mdiv>, <body>, <music>, and <mei> so that it can stand as
    an independent document.

    :param section: The <section> eleemnt to wrap.
    :type section: :class:`xml.etree.ElementTree.Element`
    :returns: The corresponding <mei> element.
    :rtype: :class:`xml.etree.ElementTree.Element`
    '''
    score = etree.Element(mei.SCORE)
    score.append(section)
    mdiv = etree.Element(mei.MDIV)
    mdiv.append(score)
    body = etree.Element(mei.BODY)
    body.append(mdiv)
    music = etree.Element(mei.MUSIC)
    music.append(body)
    post = etree.Element(mei.MEI)
    post.append(music)

    return post


def create_measures(lmei_section):
    '''
    Convert a Lychee-MEI <section> without <measure> elements into an MEI section by adding
    <measure> elements at the expected place in the standard MEI hierarchy.

    :param lmei_section: The <section> to convert.
    :type lmei_section: :class:`xml.etree.ElementTree.Element`
    :returns: A converted <section>.
    :rtype: :class:`xml.etree.ElementTree.Element`

    .. note:: During conversion, the LMEI <section> is not modified.

    **Known Limitations**

    - Does not process tuplets.
    - Uses one meter signature for all staves.
    - Uses one meter signature for the whole <section> (cannot change).
    - Assumes 4/4 meter unless indicated otherwise with @meter.count and @meter.unit
      on the *first* <staffDef>.
    '''

    # 0.) The poor man's deep copy.
    #     This allows us to reuse LMEI elements in the MEI output, rather than deep copying later.
    l_section = etree.fromstring(etree.tostring(lmei_section))

    # 1.) Assume or find a time signature.
    #     Limitation: one time signature for all <staff>.
    #     Limitation: one time signature for the whole <section>.
    #     Limitation: metre must be indicated with @meter.count and @meter.unit on <staffDef>.
    first_staff_def = l_section.find('.//{tag}'.format(tag=mei.STAFF_DEF))
    meter_count = float(first_staff_def.get('meter.count', 4))
    meter_unit = float(first_staff_def.get('meter.unit', 4))
    # NB: the "meter count factor" is the beat count we actually need in every measure
    meter_count_factor = meter_count / meter_unit

    # 1.a.) Make sure all the first <staffDef> knows the metre (in case we assumed it).
    first_staff_def.set('meter.count', str(int(meter_count)))
    first_staff_def.set('meter.unit', str(int(meter_unit)))

    # 2.) Set up the <section> and copy the <scoreDef> from LMEI to MEI.
    m_section = etree.Element(mei.SECTION)
    m_section.append(l_section.find(mei.SCORE_DEF))

    # 3.) For each LMEI <staff>
    m_measures = {}  # NB: in this dict, keys are measure number as int
    meas_nums = {}  # NB: in this dict, keys are staff[@n] and values are the measure number most
                    #     recently processed for that <staff>
    for l_staff in l_section.iterfind(mei.STAFF):
        # in case we already had a <staff> with this @n, measure numbers don't start at 1
        previous_measures = meas_nums.get(l_staff.get('n'), 0)
        highest_meas_num_in_this_staff = previous_measures

        # 4.) For each LMEI <layer>
        for l_layer in l_staff.iterfind(mei.LAYER):
            # 5.) Find enough stuff for an MEI <measure> and stick it in.
            #     Limitation: does not handle tuplets.
            meas_num = previous_measures + 1
            beat_count = 0.0
            # We can't use beat_count to tell us when we're at the start of a <measure> (and should
            # therefore make new <measure> and <layer> elements) because there may be elements
            # without duration at the start of a <measure>.
            things_in_this_measure = 0

            # Hold information about tuplets.
            # Keys are @xml:id of affected chord/note/rest/spacer (without leading #).
            # Value is a list of tuplet ratios as Fraction instances. When you multiply the @dur
            # of a note in a tuplet by these Fraction instances, you get the note's "beat count."
            # To save memory, remove values from the dictionary once the note is converted.
            tuplets = {}

            for l_elem in l_layer.iterfind('*'):
                if things_in_this_measure == 0:
                    # create a new measure, or find it from a previous <staff>
                    if meas_num in m_measures:
                        m_meas = m_measures[meas_num]
                    else:
                        m_meas = etree.SubElement(m_section, mei.MEASURE, n=str(meas_num))
                        m_measures[meas_num] = m_meas

                    # try to find this <staff> from a previous <layer>
                    m_staff = m_meas.find('{tag}[@n="{n}"]'.format(tag=mei.STAFF, n=l_staff.get('n')))
                    if m_staff is None:
                        m_staff = etree.SubElement(m_meas, mei.STAFF, n=l_staff.get('n'))
                    m_layer = etree.SubElement(m_staff, mei.LAYER, n=l_layer.get('n'))

                # count the duration of this element (if relevant)
                if l_elem.tag not in _DURATION_HAVING_ELEMENTS:
                    pass
                elif (beat_count == 0.0 and
                      l_elem.get('dur') == '1' and
                      l_elem.get(xml.ID) not in tuplets):
                    # whole note as first thing in measure will always take the whole measure
                    beat_count = meter_count_factor
                else:
                    # It's "scaled" according to the meter-count factor.
                    # Use float() so the division works properly.
                    scaled_dur = 1.0 / float(l_elem.get('dur'))

                    if l_elem.get('dots'):
                        last_value_added = scaled_dur
                        for _ in range(int(l_elem.get('dots'))):
                            last_value_added /= 2.0
                            scaled_dur += last_value_added

                    if l_elem.get(xml.ID) in tuplets:
                        for each_tuplet in tuplets[l_elem.get(xml.ID)]:
                            scaled_dur = scaled_dur * each_tuplet

                        del tuplets[l_elem.get(xml.ID)]

                    beat_count += scaled_dur

                # set up a <tupletSpan>
                if l_elem.tag == mei.TUPLET_SPAN:
                    plist = l_elem.get('plist', '')
                    plist = plist.replace('#', '')
                    if plist != '':
                        plist = plist.split(' ')
                        tuplet_ratio = Fraction(
                            int(l_elem.get('numbase', 0)),
                            int(l_elem.get('num', 0))
                        )
                        for each_xmlid in plist:
                            if each_xmlid in tuplets:
                                tuplets[each_xmlid].append(tuplet_ratio)
                            else:
                                tuplets[each_xmlid] = [tuplet_ratio]

                m_layer.append(l_elem)
                things_in_this_measure += 1

                if beat_count >= meter_count_factor:
                    highest_meas_num_in_this_staff = max(highest_meas_num_in_this_staff, meas_num)
                    beat_count = 0.0
                    meas_num += 1
                    things_in_this_measure = 0

        # update "meas_nums" for next time we hit a <staff> with this @n
        meas_nums[l_staff.get('n')] = highest_meas_num_in_this_staff

    return m_section


def rewrite_beam_spans(m_section):
    '''
    Modify the given section to replace <beamSpan> with <beam>, because Verovio doesn't support
    <beamSpan>.

    The element passed in does not actually need to be a section. It can be any parent of the
    elements we're interested in.
    '''
    xml_ids = {}
    for el in m_section.iterfind('.//*'):
        if el.get(xml.ID):
            xml_ids[el.get(xml.ID)] = el

    for m_beamspan in m_section.iterfind('.//' + mei.BEAM_SPAN):
        beamspan_parent = m_beamspan.getparent()
        beamspan_parent.remove(m_beamspan)

        plist = m_beamspan.get('plist')
        nodes = [xml_ids[x[1:]] for x in plist.split()]
        parent = nodes[0].getparent()
        insertion_index = parent.index(nodes[0])
        beam = etree.Element(mei.BEAM)
        for node in nodes:
            parent.remove(node)
            beam.append(node)
        parent.insert(insertion_index, beam)

    return m_section
