.. _basic:

Basic Concepts
==============

*Lychee* manages an MEI document during a score editing session. *Lychee* performs
nearly-instantaneous conversion between various representations (Abjad, LilyPond, and MEI) with
optional version control integration, and provides a connection point for user interfaces (whether
over the web, to a desktop application, or a commandline).

While *Lychee* is developed primarily for use as the core of `nCoda`_, we are developing *Lychee*
with other use cases in mind so that our work benefits a larger audience.

.. _ncoda: https://ncodamusic.org/


.. _basic-introduction:

Introduction, Audiences, API Stability
--------------------------------------

This documentation is designed for three types of *Lychee* users, each with their own needs:

#. People who want to use existing *Lychee* functionality for purposes we predicted, for example as
   the backend of *nCoda*. These users will primarily refer to the :ref:`workflow-session` section.
   Furthermore, the *Lychee* version numbers are designed for these users: once we reach version 1.0,
   any backward-incompatible change to the :ref:`workflow-session` API will be signalled with a
   new "major" version number, which we intend to be infrequent.
#. People who want to use existing *Lychee* functionality for purposes we did not predict. (No example
   use case here, or else we would have predicted it). In addition to the :ref:`workflow-session`
   API, we expect these users to be interested in the rest of the :ref:`workflow` APIs, the
   :ref:`lychee_mei` specification, the :ref:`document`, the :ref:`views` functionality, and the
   :ref:`vcs` section. (Indeed, this includes most of *Lychee*). **We have not yet decided what level of
   API stability to offer for these modules**: backward-incompatible changes may be signalled either
   with a new "major" or "minor" version number.
#. People developing *Lychee*, who may need to modify the behaviour of API functions, and who will
   be expected to use and develop internal interfaces where appropriate. In addition to the above,
   these users will be interested in class- and module-level private functions, including the inner
   workings of the format converters. Internal APIs may change at any time, so we have clearly marked
   them with a warning against use in external software. If you would like to use an internal *Lychee*
   API in external software, please ask us to consider making the internal API public!

There are two additional points worth making explicit. First, you may not fit cleanly into one of
the categories described above. Second, there's a good chance you won't need to read most of the
documentation here.


Starter Example
---------------

*Lychee* is a complex complex of software, but most functionality is simple enough to use! This
example shows one way to get started with *Lychee*.

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

.. note::
    Even this simple example shows our inconsistent use of the observer pattern (that is, the
    signals). We are gradually replacing this pattern with the :mod:`~lychee.workflow.session`
    module. While the observer pattern is well-suited for many potential real-world uses of *Lychee*,
    we originally used it at the wrong level of abstraction. Therefore, the signals are moving into
    user interface glue layers like `Fujian <https://fujian.ncodamusic.org/>`_ and the future
    :mod:`lychee.tui` module.


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
skipped if there is no incoming change, if the VCS is disabled, or for many other reasons. Do note
that the VCS step is disabled by default; you can enable it when you create an
:class:`~lychee.workflow.session.InteractiveSession` instance.

The **outbound** step produces documents in an external format according to the (newly-changed)
Lychee-MEI document. The **outbound views** step first determines which portion of the Lychee-MEI
document to send out, then then **outbound conversion** step runs the conversion and emits the
result. The outbound step may be skipped if no external formats are registered. The outbound views
step may be skipped for external formats where it does not apply (like
:mod:`~lychee.converters.vcs_outbound`). Also note that the outbound steps are repeated if more
than one external format is registered.
