Workflow and Action Management
==============================

.. automodule:: lychee.workflow
    :members:

Program Modules
---------------

.. toctree::
    :maxdepth: 2

    workflow-session
    workflow-steps


Signals and Slots
-----------------

*Lychee* uses "signals and slots" to implement the observer pattern, a type of event-driven
programming. We prefer signals because they offer a loose coupling between program modules,
facilitating the insertion, removal, and substitution of modules at runtime. For example, users
might add support for the input data format of their choice. The observer pattern also allows
program modules to be notified on certain events: a quality control module might want to be notified
whenever a conversion fails, for example.

TODO: write basic terms (signal, slot, emit, connect)


Use in Lychee
^^^^^^^^^^^^^

Event-driven programming is typically reserved for GUI backends. *Lychee* uses the observer pattern
to manage control flow regardless of how it is started. While an
:class:`~lychee.workflow.session.InteractiveSession` instance runs the workflow via functions in the
:mod:`~lychee.workflow.steps` module, each step in turn emits and listens for a series of signals
in order to run the step.

The conversion, views processing, and VCS steps are all run with signals, and these modules must
therefore follow the relevant specification described below.

*Lychee* uses the `signalslot`_ package to implement the observer pattern. This package in turn is
modelled after the implementation in `Qt`_. *Lychee* extends :mod:`signalslot` with a custom
:class:`~lychee.signals.signal.Signal` class that uses *Fujian* to emit signals over a WebSocket
connection, if *Fujian* is available. *Lychee* could also be extended to integrate with PyQt signals
or another callback-based event-driven library.

For a proper description of the observer pattern, please refer to the `Qt documentation`_ on the topic.

.. _qt: https://doc.qt.io/qt-5/signalsandslots.html
.. _qt documentation: https://doc.qt.io/qt-5/signalsandslots.html
.. _signalslot: https://signalslot.readthedocs.org/


Example
^^^^^^^

Consider the following code excerpt, which does not use real *Lychee* functions or signals. We'll
inspect it closely in a moment.

.. sourcecode:: python

    # in "signals" module

    mei_updated = signalslot.Signal()
    made_commit = signalslot.Signal()
    lilypond_updated = signalslot.Signal()
    musicxml_updated = signalslot.Signal()

    # in "vcs" module

    def make_a_commit(pathname):
        hg.add(pathname)
        ref = hg.commit('Made a change to {}'.format(pathname))
        signals.made_commit.emit(ref)

    # in "output" module

    def output_lilypond(pathname):
        converted = mei_to_ly.output(pathname)
        signals.lilypond_updated.emit(converted)

    def output_musicxml(pathname):
        converted = mei_to_mxml.output(pathname)
        signals.musicxml_updated.emit(converted)

    # elsewhere

    signals.mei_updated.connect(vcs.make_a_commit)
    signals.mei_updated.connect(output.output_lilypond)

In the `signals` module, we define an "mei_updated" signal, which is emitted when the MEI document
has changed, and a "made_commit" signal, which is emitted when a new commit was made in the repository.

In the `vcs` module, :func:`make_a_commit` accepts the pathname of a modified file, make a commit,
then emits the "made_commit" signal.

In the `output` module, :func:`output_lilypond` and :func:`output_musicxml` accept the pathname to
a modified file, call another function to run the conversion, then emit signals to indicate the
conversion is finished.

In the "elsewhere" portion, the "mei_updated" signal is connected to :func:`make_a_commit` and
:func:`output_lilypond`. Therefore we know that, whenever an MEI file is updated, the "mei_updated"
signal will call the function to make a new commit and the function to output an updated LilyPond
snippet. The MusicXML output is currently disabled; calling :func:`connect` on the signal is enough
to enable it.

We can also see that, thanks to the signal interface in this simple example, extending the program
with new functionality would be trivial, and would not require modifications to existing functionality.
For example, we might add a :func:`push_commits` function, connected to the "made_commit" signal,
so that every new commit would be pushed to a remote server right away.


Signal Definitions
------------------

.. automodule:: lychee.signals
    :members:

Inbound Step
^^^^^^^^^^^^

.. automodule:: lychee.signals.inbound
    :members:

VCS Step
^^^^^^^^

.. automodule:: lychee.signals.vcs
    :members:

Outbound Step
^^^^^^^^^^^^^

.. automodule:: lychee.signals.outbound
    :members:
