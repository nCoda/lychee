Basic Concepts
==============

*Lychee* manages an MEI document during a score editing session. *Lychee* performs
nearly-instantaneous conversion between various representations (Abjad, LilyPond, and MEI) with
optional version control integration, and connections to an event-driven notification system for
use in GUI applications.

While *Lychee* is developed primarily for use as the core of `nCoda`_, we are developing *Lychee*
with other use cases in mind so that our work benefits a larger audience.

.. _ncoda: https://ncodamusic.org/


Starter Example
---------------

We admit it: *Lychee* is a complex complex of software, but using it is simple! This example shows
one way to get started with *Lychee*.

.. sourcecode:: python
    :linenos:

    import lychee

    def print_converted(document, **kwargs):
        print(str(document))

    sess = lychee.workflow.session.InteractiveSession()
    lychee.signals.outbound.REGISTER_FORMAT.emit(dtype='verovio')
    lychee.signals.outbound.CONVERSION_FINISHED.connect(print_converted)
    lychee.signals.ACTION_START.emit(dtype='lilypond', doc=r"\score{\new Staff{d''2}}")

Line 6: create an :class:`~lychee.workflow.session.InteractiveSession` instance so *Lychee* sets up
the workflow.

Line 7: use :const:`~lychee.signals.outbound.REGISTER_FORMAT` to ask *Lychee* to produce
output suitable for *Verovio*.

Line 8: connect :func:`print_converted` so it is called when *Lychee* finishes outbound conversion.

Line 9: use :const:`~lychee.signals.ACTION_START` to submit a small LilyPond document to
*Lychee*. You should see :func:`print_converted` print out an MEI document ready for *Verovio*!


Program Modules
---------------

The following top-level modules constitute the core functionality of *Lychee*.

- :mod:`~lychee.converters`: A collection of encoding format converters between the internal
  :ref:`lychee_mei` format and various external representations (such as standard MEI, Abjad, and
  LilyPond). There are also modules to export data from the version control system, and information
  about the Lychee-MEI document itself.
- :mod:`~lychee.document`: Representation of a Lychee-MEI document. Manage files-on-disk, in-memory
  representations, and access document metadata without having to figure out all of Lychee-MEI.
- :mod:`~lychee.namespaces`: A collection of constants to be used as namespaced XML tag names and
  attribute names. Use these to avoid accidental use of non-namespaced tag names.
- :mod:`~lychee.signals`: Action definitions for use with Lychee's event-driven programming model.
- :mod:`~lychee.tui`: Commandline textual interface.
- :mod:`~lychee.vcs`: Handles interaction with Mercurial, the version control system used internally
  by *Lychee*.
- :mod:`~lychee.views`: Functionality for *Lychee* to track several discrete musical fragments
  simultaneously, and to allow partial updates to documents.
- :mod:`~lychee.workflow`: Functionality required to set up and manage a *Lychee* document editing
  session, and to run the various workflow steps.


Generic Workflow
----------------

*Lychee* uses the same generic workflow for every action. There are four steps: inbound, document,
VCS, and outbound. The inbound and outbound steps always have a conversion sub-step, and may also
have a views sub-step. Depending on the runtime configuration and the action requested, *Lychee*
may run only a single step, or up to all six.

The **inbound** step converts from an external format into Lychee-MEI (the **inbound conversion**).
This will usually be followed by the **inbound views** step, where *Lychee* determines which portion
of the Lychee-MEI document is modified by the incoming external document. The inbound step may be
skipped if there is no incoming change, for example if a user wants to see the existing document in
a different external format.

The **document** step creates, modifies, and deletes portions of the Lychee-MEI document according
to the inbound change. Both the in-memory and on-disk representations may be modified. The document
step may be skipped if there is no incoming change.

The **VCS** step manages the repository holding the Lychee-MEI document. This may involve committing
a new changeset, updating to another bookmark, or even computing a diff. The VCS step may be
skipped if there is no incoming change, if the VCS is disabled, or for many other reasons.

The **outbound** step produces documents in an external format according to the (newly-changed)
Lychee-MEI document. The **outbound views** step first determines which portion of the Lychee-MEI
document to send out, then then **outbound conversion** step runs the conversion and emits the
result. The outbound step may be skipped if no external formats are registered. The outbound views
step may be skipped for external formats where it does not apply (like
:mod:`~lychee.converters.vcs_outbound`). Also note that the outbound steps are repeated if more
than one external format is registered.
