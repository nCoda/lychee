External Format Converters
==========================

An external format converter changes the symbolic representation of musical data. **Inbound
converters** produce a Lychee-MEI document as an :class:`lxml.etree.Element` object, while
**outbound converters** consume a Lychee-MEI :class:`Element` and produce data in an external
format. Some outbound converters produce non-musical data, like :mod:`~lychee.converters.outbound.vcs_outbound`,
which effectively serializes version control data from Mercurial into a JSON object.

At the moment, most of the format converters are incomplete, and therefore do not accept all possible
documents. In addition, we intend to supplement these with more formats in the future.


Converter Module Interface
--------------------------

To maximize flexibility, each converter module is designed in the way most suitable for the module
author, and exposes only the :func:`convert` function described here. This allows different
programming paradigms and, more importantly, the use of external libraries.

.. function:: convert(document, **kwargs)

    Convert any part of a document into the corresponding document portion in another format.

    :param document: For inbound converters this is the document (portion) in an external format,
        usually a string. For outbound converters this is the Lychee-MEI document (portion),
        usually an :class:`lxml.etree.Element`. Refer to each module for its expected argument type.
    :param kwargs: Additional keyword arguments must be accepted and must be ignored.
    :returns: The corresponding document (portion) after conversion.
    :rtype: For inbound converters, this must be an :class:`lxml.etree.Element`. For outbound
        converters, this is usually a string. Refer to each module for the return type.
    :raises: Not yet decided.

    This function should accept the smallest and largest portions of notation that can reasonably be
    thought of as "one document" or "part of one document," and produce the corresponding output
    without guessing or removing context. For example, two complete musical scores is not acceptable.
    A single note should probably be accepted, but a single accidental (not attached to a note) is
    probably too small.

    The allowable document portions varies between converters, depending on the needs of the two
    data formats involved. In addition, a "round trip" conversion may not result in an identical
    document. For example, an LMEI ``<measure>`` converted to LilyPond and back to LMEI is unlikely
    to result in an LMEI ``<measure>``. Consider the LilyPond snippet ``fis4 gis4 a2 |`` which does
    end with a bar-check symbol, but it's not clear whether this should be one measure in 4/4 meter,
    two measures in 2/4 meter, or something else. The LilyPond-to-LMEI converter therefore should
    not assume the snippet is a ``<measure>``. It is still reasonable to include a ``<barLine>``
    element at the end.

.. note::
    Some converter modules do not comply with this interface yet.


.. _how-to-use-converters:

How to Use the Converters
-------------------------

If you are using a converter from outside *Lychee*:

#. Use the converter's :func:`convert` function.
#. If you must use another part of the converter, including by copying and reusing code, we recommend
   contacting the converter's author in order to find a mutually beneficial way to manage this
   situation.

If you are a *Lychee* developer:

#. If you are working on a :mod:`converters` submodule, you should prefer to use other converters
   via their :func:`convert` function, but you may use any function if required.
#. If you are working on the :mod:`lychee.workflow.steps` module, use :func:`convert` only. If this
   isn't possible, there is a design problem that should be discussed and solved so that
   :func:`convert` can be used.
#. If you are working on another module, you should use a function in the :mod:`~lychee.workflow.steps`
   module. If this isn't possible, there is a design problem that should be discussed and solved so
   the :mod:`steps` module can be used.


Converter Modules
-----------------

.. automodule:: lychee.converters
    :members:


Inbound Converters
^^^^^^^^^^^^^^^^^^

.. toctree::
    :maxdepth: 1

    converters-abjad_in
    converters-lilypond_in
    converters-mei_in


Outbound Converters
^^^^^^^^^^^^^^^^^^^

.. toctree::
    :maxdepth: 1

    converters-abjad_out
    converters-document_out
    converters-lilypond_out
    converters-mei_out
    converters-vcs_out
