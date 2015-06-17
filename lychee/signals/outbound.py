#!/usr/bin/env python3

import signalslot


WHO_IS_LISTENING = signalslot.Signal()
'''
The :class:`WorkflowManager` emits this signal before beginning the outbound processing steps, in
order to determine the outbound formats that are required at the moment. Every UI component that
wants an update should emit the :const:`I_AM_LISTENING` signal with the required data type, to
ensure the proper data type will be prepared.

UI components receive their data from the :const:`CONVERSION_FINISHED` signal, which is emitted
for every data type prepared. Therefore, slots on UI components must double-check they have been
called with the required data type, and not complain if the data is the wrong type, because they
will very often be called with data of the wrong type.

For as long as Lychee runs synchronously (which is likely to be always) the :const:`WHO_IS_LISTENING`
call and :const:`I_AM_LISTENING` response pattern will work just fine because outbound processing
cannot begin until all the :const:`WHO_IS_LISTENING` slots have finished execution.
'''

I_AM_LISTENING = signalslot.Signal(args=['dtype'])
'''
As described above, UI components should emit this signal with the proper data type to ensure they
will receive the data they require. It is safe to emit this signal multiple times with the same
argument---the :class:`WorkflowManager` will still only perform the conversion once per data type.

:kwarg str dtype: The requested data type ('abjad', 'lilypond', 'mei')
'''

VIEWS_START = signalslot.Signal(args=['dtype'])
'''
Emitted to begin outbound views processing. (This is emitted several times---once per data type).

:kwarg str dtypes: The desired outbound format.
'''

VIEWS_STARTED = signalslot.Signal()
'''
Emitted when outbound view processing begins.
'''

VIEWS_FINISH = signalslot.Signal(args=['dtype', 'views_info'])
'''
Emitted with the results of outbound views processing.

:kwarg str dtype: The data type this views information corresponds to.
:kwarg object views_info: The views information required for the "dtype" data format.
'''

VIEWS_FINISHED = signalslot.Signal()
'''
Emitted after the views processing has completed for *all* data types.
'''

VIEWS_ERROR = signalslot.Signal(args=['msg'])
'''
Emitted when there's an error while processing the outbound view.

:kwarg str msg: A descriptive error message for the log file.
'''

CONVERSION_START = signalslot.Signal(args=['views_info', 'l_mei'])
'''
Emitted to being outbound conversion. (This is emitted several times---once per data type).

:kwarg object views_info: The views information required for the "dtype" data format.
:kwarg l_mei: Whatever document is required to prepare the outbound data.
:type l_mei: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
'''

CONVERSION_STARTED = signalslot.Signal()
'''
Emitted when outbound conversion begins.
'''

CONVERSION_FINISH = signalslot.Signal(args=['converted'])
'''
Emitted with the results of an outbound conversion.

:kwarg object converted: The converted document, ready for UI components.
'''

CONVERSION_FINISHED = signalslot.Signal(args=['dtype', 'placement', 'document'])
'''
Emitted by the :class:`WorkflowManager` after all data types have been prepared, once per data type.
Slots should pay attention to the "dtype" value to know whether they are interested in the document
in the currently-offered format, or they wish to wait for another format.

To help ensure all UI components will be updated at approximately the same time, all outbound
formats are prepared before any :const:`CONVERSION_FINISHED` signal is emitted.

:param str dtype: The data type of the "document" argument ("abjad", "lilypond", or "mei"). Always
    in lowercase.
:param object placement: Information for the slot about which part of the document is being updated.
    Offered in a different format depending on the "dtype" of this call.
:param object document: The update (partial) document. The type depends on the value of "dtype."
'''

CONVERSION_ERROR = signalslot.Signal(args=['msg'])
'''
Emitted when there's an error during the outbound conversion step.

:kwarg str msg: A descriptive error message for the log file.
'''
