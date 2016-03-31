#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/workflow/steps.py
# Purpose:                Functions to combine as "steps" in a workflow action.
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
Functions to combine as "steps" in a workflow action.

.. caution:: We intend the functions in this module to be used by primarily an
    :class:`~lychee.workflow.session.InteractiveSession` instance, which knows the proper sequencing
    and error-handling strategies. We invite you to use this module too when you are extending and
    working with Lychee, but be careful---mistakes in the order or the input data can cause loss or
    corruption of the Lychee-MEI document and repository.

The module defines several "steps," which follow a determinate order but are not all mandatory:

#. inbound conversion
#. inbound views
#. document
#. VCS
#. outbound views
#. outbound conversion

Also note that the steps need not necessarily happen in order, sequentially, or only once per Lychee
"action." For example, the VCS step can happen simultaneously with most of the outbound
views/conversion steps. The views/conversion steps themselves are likely to happen several times,
possibly simultaneously, depending on which outbound formats are registered.
'''

from lxml import etree

import lychee
from lychee import converters
from lychee import document
from lychee import exceptions
from lychee.namespaces import mei
from lychee import signals


# translatable strings
_INVALID_INBOUND_DTYPE = 'Invalid "dtype" for inbound conversion: "{0}"'
_UNEXP_ERR_INBOUND_CONVERSION = 'Unexpected error during inbound conversion'
_UNEXP_ERR_INBOUND_VIEWS = 'Unexpected error during inbound views processing'
_INVALID_OUTBOUND_DTYPE = 'Invalid "dtype" for outbound conversion: "{0}"'


def do_inbound_conversion(session, dtype, document):
    '''
    Run the "inbound conversion" step.

    :param session: A session instance for the ongoing notation session.
    :type session: :class:`lychee.workflow.session.InteractiveSession`
    :param str dtype: The inbound data type as specified in the
        :const:`lychee.converters.INBOUND_CONVERTERS` mapping.
    :param document: The incoming (partial) document for conversion.
    :type document: As required by the converter.

    This function chooses an inbound converter then runs it. Resulting data is emitted from the
    converter with the :const:`~lychee.signals.inbound.CONVERSION_FINISH` signal and not returned
    by this function. If an error occurs during conversion, this function emits the
    :const:`~lychee.signals.inbound.CONVERSION_ERROR` signal with an error message, then the
    :const:`~lychee.signals.inbound.CONVERSION_FINISH` signal with ``None``.
    '''
    try:
        _choose_inbound_converter(dtype)
        signals.inbound.CONVERSION_START.emit(document=document)
    except Exception as exc:
        if isinstance(exc, exceptions.InvalidDataTypeError):
            msg = exc.args[0]
        else:
            msg = _UNEXP_ERR_INBOUND_CONVERSION
        signals.inbound.CONVERSION_ERROR.emit(msg=msg)
        signals.inbound.CONVERSION_FINISH.emit(converted=None)
    finally:
        flush_inbound_converters()


def do_inbound_views(session, dtype, document, converted):
    '''
    Run the "inbound views" step.

    :param session: A session instance for the ongoing notation session.
    :type session: :class:`lychee.workflow.session.InteractiveSession`
    :param str dtype: The inbound data type as specified in the
        :const:`lychee.converters.INBOUND_CONVERTERS` mapping.
    :param document: The incoming (partial) document for conversion, as supplied to
        :func:`do_inbound_conversion`.
    :type document: As required by the converter.
    :param converted: The incoming (partial) document, already converted.
    :type converted: :class:`lxml.etree.Element`

    This function chooses an inbound views-processor then runs it. Resulting data is emitted from
    the processor with the :const:`~lychee.signals.inbound.VIEWS_FINISH` signal and not returned
    by this function. If an error occurs during processing, this function emits the
    :const:`~lychee.signals.inbound.VIEWS_ERROR` signal with an error message, then the
    :const:`~lychee.signals.inbound.VIEWS_FINISH` signal with ``None``.
    '''
    try:
        _choose_inbound_views(dtype)
        signals.inbound.VIEWS_START.emit(document=document, converted=converted)
    except Exception as exc:
        if isinstance(exc, exceptions.InvalidDataTypeError):
            msg = exc.args[0]
        else:
            msg = _UNEXP_ERR_INBOUND_VIEWS
        signals.inbound.VIEWS_ERROR.emit(msg=msg)
        signals.inbound.VIEWS_FINISH.emit(views_info=None)
    finally:
        flush_inbound_views()


def do_document(session, converted, views_info):
    '''
    Run the "document" step.

    :param session: A session instance for the ongoing notation session.
    :type session: :class:`lychee.workflow.session.InteractiveSession`
    :param converted:
    :param views_info:
    :returns: A list of the pathnames in this Lychee-MEI document.
    :rtype: list of str

    .. note:: This function is only partially implemented. At the moment, it simply replaces the
        active score with a new one containing only the just-converted ``<section>``.
    '''
    lychee.log('Beginning the "document" step.')

    score = etree.Element(mei.SCORE)
    score.append(converted)
    doc = session.get_document()
    doc.put_score(score)
    document_pathnames = doc.save_everything()

    lychee.log('Finished the "document" step.')

    return document_pathnames


def do_vcs(session, pathnames):
    '''
    Run the "VCS" step.

    :param session: A session instance for the ongoing notation session.
    :type session: :class:`lychee.workflow.session.InteractiveSession`
    :param pathnames: A list of the pathnames in this Lychee-MEI document (as returned by
        :func:`do_document`).
    :type pathnames: list of str
    :returns: ``None``
    '''
    # NOTE: why bother with the signal at all? Why not just call self._vcs_driver() ? Because
    # this way we can enable/disable the VCS step by changing who's listening to vcs.START.
    signals.vcs.START.emit(repo_dir=session.get_repo_dir(), pathnames=pathnames)
    signals.vcs.FINISHED.emit()


def do_outbound_steps(repo_dir, views_info, dtype):
    '''
    Run the outbound veiws and conversion steps for a single outbound "dtype."

    :param str repo_dir: Absolute pathname to the repository directory.
    :param views_info: ????????????
    :type views_info:  ????????????
    :param str dtype: The data type to use for outbound conversion, as specified in
        :const:`lychee.converters.OUTBOUND_CONVERTERS`.
    :returns: Post-conversion data as described below.
    :rtype: dict
    :raises: :exc:`lychee.exceptions.InvalidDataTypeError` when there is no module available for
        outbound conversion to ``dtype``.

    The outbound steps are designed to be run in parallel---whether or not they are. That's why all
    the parameter types are easily serializable, control is not given up between the views and
    conversion steps, and the result is returned rather than provided with a signal.

    **Returned Data**

    This function returns the data required for the outbound
    :const:`~lychee.converters.outbound.CONVERSION_FINISHED` signal. The actual return is a
    dictionary with three keys: `dtype`, `document`, and `placement`. The values are defined in
    that signal's documentation.
    '''

    if dtype in ('document', 'vcs'):
        # these dtypes don't have real "views" information, so we'll do them early
        converted = converters.OUTBOUND_CONVERTERS[dtype](repo_dir)
        return {'dtype': dtype, 'document': converted, 'placement': None}

    else:
        if dtype in converters.OUTBOUND_CONVERTERS:
            from_views = _do_outbound_views(repo_dir, views_info, dtype)
            converted = converters.OUTBOUND_CONVERTERS[dtype](from_views['convert'])
            return {'dtype': dtype, 'document': converted, 'placement': from_views['placement']}

        else:
            raise exceptions.InvalidDataTypeError(_INVALID_OUTBOUND_DTYPE.format(dtype))


def _vcs_driver(repo_dir, pathnames, **kwargs):
    '''
    Slot for vcs.START that actually runs the "VCS step," and will only be called when the VCS
    system is enabled.
    '''
    signals.vcs.INIT.emit(repodir=repo_dir)
    signals.vcs.ADD.emit(pathnames=pathnames)
    signals.vcs.COMMIT.emit(message=None)


def _choose_inbound_converter(dtype):
    '''
    Connect the "inbound.CONVERSION_START" signal to the appropriate converter according to the
    inbound data type.

    :param str dtype: The inbound data type as specified in the
        :const:`lychee.converters.INBOUND_CONVERTERS` mapping.
    :raises: :exc:`~lychee.exceptions.InvalidDataTypeError` when there is not inbound converter
        for the given ``dtype``.
    '''
    if dtype in converters.INBOUND_CONVERTERS:
        signals.inbound.CONVERSION_START.connect(converters.INBOUND_CONVERTERS[dtype])
    else:
        raise exceptions.InvalidDataTypeError(_INVALID_INBOUND_DTYPE.format(dtype))


def flush_inbound_converters():
    '''
    Clear any inbound converters that may be connected.
    '''
    for each_converter in converters.INBOUND_CONVERTERS.values():
        signals.inbound.CONVERSION_START.disconnect(each_converter)


def _dummy_inbound_views_slot(**kwargs):  # TODO: remove with T33
    signals.inbound.VIEWS_FINISH.emit(views_info='<dummy views info>')


def _choose_inbound_views(dtype):  # TODO: untested until T33
    '''
    Connect the "inbound.VIEWS_START" signal to the appropriate views processor according to the
    inbound data type.

    :param str dtype: The inbound data type as specified somewhere???????
    :raises: :exc:`~lychee.exceptions.InvalidDataTypeError` when there is not inbound views
        processor for the given ``dtype``.

    .. warning:: This function is not implemented. Refer to T33.
    '''
    signals.inbound.VIEWS_START.connect(_dummy_inbound_views_slot)


def flush_inbound_views():  # TODO: untested until T33
    '''
    Clear any inbound views processors that may be connected.

    .. warning:: This function is not implemented. Refer to T33.
    '''
    pass


def _do_outbound_views(repo_dir, views_info, dtype):  # TODO: untested until T33
    '''
    Private helper function for :func:`do_outbound_steps`.

    Parameters are the same given to :func:`do_outbound_steps`.

    :returns: A dictionary with two keys: ``'placement'`` as required for the ``CONVERSION_FINISHED``
        signal; and ``'convert'`` which is the LMEI document portion to be converted.
    :rtype: dict
    '''
    convert = None
    doc = document.Document(repo_dir)
    if len(doc.get_section_ids()) > 0:
        convert = doc.get_section(doc.get_section_ids()[0])

    return {'placement': '<filler placement info>', 'convert': convert}
