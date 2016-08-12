.. _views:

Views Processing (Partial Document Updates)
===========================================

.. warning::
    The :mod:`views` module and its submodules are a very early prototype.
    The module's interface will be changed significantly during proper implementation.
    Please refer to `T87 <https://goldman.ncodamusic.org/T87>`_ for more information.

The :mod:`lychee.views` module will provide a musically-aware "diff" implementation. That is,
*Lychee* will be able to show the musical differences between two Lychee-MEI ``<section>`` elements.
Building on the unique capabilities of *Lychee*, we predict significant interest from external
developers, and we intend to offer a suitable interface to the :mod:`views` module in the future.

Our initial development focusses on using *Lychee* as the backend for *nCoda*---a situation more
difficult to implement than the external use cases we know of.


Maintaining "Views" on a Document
---------------------------------

The principal use case of the :mod:`views` module, as required for *nCoda*, allows *Lychee* to
simultaneously track discrete musical fragments in different formats. Each fragment provides a "view"
of the internal music document, and the Views workflow steps allow *Lychee* to reconcile which parts
of each "view" correspond to which parts of the internal music document. The Inbound Views step
allows *Lychee* to change the smallest possible portion of the internal document. The Outbound Views
step allows *Lychee* to convert and broadcast the smallest possible portion of external documents.

An action with views processing looks approximately like this:

#. Inbound conversion.
#. Inbound views ("What part of the music was updated?")
#. Document assembly.
#. VCS (optional).
#. Outbound views ("Send out this part of the music.")
#. Outbound conversion.

The views processing steps determine which part of the internal Lychee-MEI score to update during an
inbound change, and which part of the external format's data to update as a result. Knowing which
part of the score is modified, *Lychee* will only send updates for external formats if the portion
of the document *currently in view* has been modified. This ability to understand *views on a
document* allows *Lychee* to work effectively in situations where full-document conversion would be
too time-consuming.

Regardless, *Lychee* is also capable of working with complete documents.


Scenarios
^^^^^^^^^

Scenario 1:
    A user creates a new note with a score-based point-and-click interface. The LilyPond
    representation of that moment, also visible, should be updated with only the single new
    note---the whole internal document will not be converted from scratch. This requires sending a
    single LMEI ``<note>`` element to the outbound LilyPond converter, along with instructions on
    where to place the note (row and column in the text file).

Scenario 2:
    A user selects a two-measure musical passage, then requests the Abjad representation of those
    measures. Even though the inbound stage is skipped, the outbound Abjad converter should only
    receive two measures. When the Abjad objects are modified, *Lychee* will know which elements to
    change of the internal document.

Scenario 3:
    A user opens a score from the MEI sample encodings. *Lychee* converts the score to Lychee-MEI
    and caches the views information required to ensure the first two examples are possible.


Inbound Views
^^^^^^^^^^^^^

During the inbound stage, the views processing modules fit a view into the complete score. During an
interactive notation editing session, the inbound views modules determine how much of the score is
affected by an edit, and provide this information to the outbound views modules.

.. warning::
    These details are likely to change.
    Please refer to `T87 <https://goldman.ncodamusic.org/T87>`_ for more information.

Modules for the :mod:`inbound` direction must provide a function
``place_view(converted, document, session)``, with the parameters are the same as specified for
:const:`lychee.signals.inbound.VIEWS_START` (being the converted music, the external-format music,
and the current :class:`~lychee.workflow.session.InteractiveSession` instance). In order to allow
proper operation of the workflow signals, :func:`place_view` **must** return ``None`` and use the
following three signals as described:

- :const:`~lychee.signals.inbound.VIEWS_STARTED` immediately after receiving control, to confirm
  that a views processing module was selected correctly.
- :const:`~lychee.signals.inbound.VIEWS_ERROR` for errors during processing, with a description of
  the error. Note that this signal should be used for recoverable errors; if execution must stop
  because of an error, we recommend raising an exception as per standard Python practice.
- :const:`~lychee.signals.inbound.VIEWS_FINISH` with results when views processing completes
  successfully. Because the function must return ``None``, this signal is the only way to provide
  views data back to the caller. It is possible to complete processing and emit :const:`VIEWS_FINISH`
  after reporting a recoverable error with :const:`VIEWS_ERROR`.


Outbound Views
^^^^^^^^^^^^^^

During the outbound stage, the views processing modules produce a view with the required music.
During an interactive notation editing session, the oubound views modules ensure that changing a
single note in the score doesn't result in re-converting the entire score from scratch for all
registered outbound formats.

.. warning::
    These details are likely to change.
    Please refer to `T87 <https://goldman.ncodamusic.org/T87>`_ for more information.

Modules for the :mod:`outbound` direction must provide a function ``get_view(repo_dir, views_info)``
where the parameters are the same as specified for :func:`lychee.workflow.steps.do_outbound_steps`
(being a string to the directory of the repository, and a string with the ``@xml:id`` of the element
for export). The function must return a two-tuple: the first element is the "views" information
required by the :const:`CONVERSION_FINISHED` signal; the second is the :class:`~lxml.etree.Element`
indicated by the ``views_info`` argument, along with any required changes to ``@xml:id`` attributes.


Example
^^^^^^^

.. note::
    This example assumes that inbound converter modules must produce deterministic ``@xml:id``
    attributes. This requirement may be lifted in the future.

This example uses a simple Abjad-like data format. The inbound converter receives three
:class:`Note` objects:

    >>> inbound = [Note('c4'), Note('d4'), Note('e4')]
    >>> inbound_mei = convert(inbound)

The inbound converter produces Lychee-MEI *but* with non-conformant ``@xml:id`` attributes.
The ``@xml:id`` attributes provided by the converter are designed to be unique in the score,
for example by computing a cryptographic hash involving all of the element's attributes.
(Note that inbound converters must produce IDs that are consistent across user sessions and Python
interpreters, so using the built-in :func:`id` function is clever but not acceptable).

    >>> inbound_mei[0].get('xml:id')
    'z1de512a9c446cd'
    >>> inbound_mei[1].get('xml:id')
    'a66d9902885d427'
    >>> inbound_mei[2].get('xml:id')
    'accb45e81aeee72'

The :mod:`views` module replaces the ``@xml:id`` attributes with proper Lychee-MEI values. (And the
values of any attributes that refer to that ``@xml:id``). Aong the way, :mod:`views` also generates
mappings between the converter-supplied and corresponding Lychee-MEI ``@xml:id``.

    >>> external_to_lmei_ids = {}
    >>> lmei_to_external_ids = {}
    >>> for element in every_element_in_the_score:
    ...     this_id = make_new_xml_id(element)
    ...     external_to_lmei_ids[element.get('xml:id')] = this_id
    ...     lmei_to_external_ids[this_id] = element.get('xml:id')
    ...     element.set('xml:id', this_id)
    ...
    >>>

If we create a new document that's *mostly* the same, the :mod:`views` modules have the context they
needs to determine what part of the document has changed.

    >>> inbound = [Note('c4'), Note('d-4'), Note('e4')]
    >>> inbound_mei = convert(inbound)
    >>> inbound_mei[0].get('xml:id')
    'z1de512a9c446cd'
    >>> inbound_mei[1].get('xml:id')
    '8efa7afeab8a29b'
    >>> inbound_mei[2].get('xml:id')
    'accb45e81aeee72'

You can see how only the second note is different from the first example, which is reflected in the
ID values provided by the inbound converter. Even though all three Python objects are different from
the first example, the :mod:`views` module is able to determine that only the second object is
*meaningfully* different. This allows the document preparation, version control, and outbound stages
to continue with the smallest possible data to process.

.. note::
    Reminder: this example assumes that inbound converter modules must produce deterministic
    ``@xml:id`` attributes. This requirement may be lifted in the future.
