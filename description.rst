Lychee: The MEI Arbiter
=======================

Lychee manages the MEI document during score editing sessions. Lychee performs nearly-instantaneous
conversion between various representations (Abjad, LilyPond, and MEI) with optional version control
integration, and connections to an event-driven notification system for use in GUI applications.

In a sense, Lychee is the core of the user-facing nCoda app, but it's being developed as an
independent library so it may be used by a wider audience.

We need the following components. The names in this list should be understood as importable Python
module names.

- converters:
    - mei_to_ly: convert MEI to LilyPond
    - ly_to_mei: convert LilyPond to MEI
    - mei_to_abjad: convert MEI to Abjad
    - abjad_to_mei: convert Abjad to MEI
    - mei_to_lmei: convert arbitrary MEI to Lychee-MEI
    - lmei_to_mei: convert Lychee-MEI to single-file MEI suitable for export
- vcs: manage revisions with Mercurial
- views: manage partial "views" on a per-format basis
- signals: coordinate event-driven programming
- tui: textual interface for commandline, "one-shot" use

For example, you would access the MEI-to-LilyPond converter with
``from lychee.converters import mei_to_ly``.

Lychee-MEI and "Arbitrary Format"
---------------------------------

Lychee-MEI is a valid subset of MEI. **Lychee-MEI** restricts MEI to encoding strategies that are
easier and safer for computers to process. This sub-format will be specified in the future; for now
it involves the following characteristics:

- file management:

    - every MEI ``<section>`` is kept in its own file, to ease version control
    - clients are therefore encouraged to use sections generously
    - a "complete" MEI file holds cross-references to all section files, in an arbitrary order
    - a "playlist" MEI file holds cross-references to "active" section files, in score order

- others:

    - tupletSpan, beamSpan, slur, and other elements that may refer to object spans with @startid
      and @endid, and are therefore inherently ambiguous and error-prone, must make use of @plist
      to reduce the possibility of ambiguity and erors

When this "description" document refers to a music document in an **arbitrary format**, it means the
music document is encoded in one of the formats supported by Lychee (Abjad, LilyPond, MEI) without a
restriction on the particular format used at the moment.

One-shot and Interactive Modes
------------------------------

Depending on the usage situation, Lychee may run in one-shot or interactive mode.

**One-shot mode** loads a complete document in an arbitrary format, optionally creates a new commit
in the VCS, and saves a complete document in an arbitrary format. The program begins and ends
execution with a single action. This situation corresponds to Lychee being run from the commandline,
or as a simple format converter.

**Interactive mode** starts execution and runs as a daemon, waiting for actions. An action is
initiated by triggering a signal in the ``signals`` module: Lychee accepts a complete or partial
document along with instructions about which part of the document is being sent; a new commit may
be created in the VCS, or a patch on the Mercurial Queue stack, or a similar event; finally,
additional signals are emitted from the ``signals`` module, indicating the updated material and its
position in the overall document, so that user interface components may update their appearance.
This situation corresponds to Lychee being run as the core of a GUI application, or in cooperation
with the core of a GUI application.

Generic Workflow
----------------

Every action Lychee performs will use the same basic workflow with three steps: inbound, document,
outbound.

The **inbound** step converts from an arbitrary format to Lychee-MEI. When running in interactive
mode, the ``views`` module is given information on what portion of the document is being updated.

The **document** step manages a change to the internal MEI document, and (if relevant) enters the
change in the VCS.

The **outbound** step converts from Lychee-MEI to (an) arbitrary format(s). When running in
interactive mode, the ``views`` module produces information on what portion of the document is
being updated.

Converters
==========

Each converter module, designed in the way most suitable for the module author's skills, provides a
public interface with a single function, convert(), that performs conversions as appropriate for
that module. Thus for example ``lychee.converters.mei_to_ly.convert()`` accepts an MEI document and
produces a LilyPond document.

**Inbound converters** result in a Lychee-MEI document as xml.etree.ElementTree.ElementTree objects
(or Element, in the case of partial documents), along with instructions on what part of the document
is being updated. (The ``views`` module determines which part of the Lychee-MEI this corresponds to).

**Outbound converters** start with (a portion of) a Lychee-MEI document, along with instructions on
what part of the document is being updated. (The ``views`` module determines which part of the
other representation this corresponds to).

LilyPond documents shall always be unicode strings. Abjad documents shall always be Abjad objects.

Each converter must be capable of accepting an incomplete document and producing the corresponding
incomplete output, and of emitting an error signal if the incomplete input is insufficient to
produce the corresponding valid output. For example, ``Element('note', {'pname': 'c'})`` given to
the ``mei_to_ly`` module should result in ``'c'`` as output, even though the single Element is not
a complete and valid MEI document, and the single-character string is not a complete and valid
LilyPond document. Yet if ``mei_to_ly`` receives ``Element('slur', {'plist': '#123 #443'})`` as
input, there is not enough information to produce any sensible output, so the module ought to emit
an error signal.

Future modules will convert data between MEI and MusicXML, and MEI and music21.

Special Case: MEI-to-MEI Converter
----------------------------------

We will require an MEI-to-MEI conversion both for inbound and outbound conversions. On the way in,
this will be to convert (nearly?) any valid MEI document into a valid Lychee-MEI document. On the
way out, this will probably mostly be to substitute the appropriate files into the "playlist" file.

VCS: Mercurial Integration
==========================

One of the core nCoda features is integration with the Mercurial VCS (version control system). This
will happen through the ``lychee.vcs`` module, and it will be a significant advantage for interested
Frescobaldi users too. In order to be sure we don't tie our projects' success to that of Mercurial,
to provide a somewhat simpler useage experience for Lychee programmers, and to protect us from
possible changes to Mercurial's Python libraries (which they warn may happen), we should offer this
functionality through a ``vcs`` wrapper module. This will also allow programmers to replace
Mercurial with another VCS, like Git, which is notably more popular than Mercurial, but unsuitable
for nCoda and suboptimal for any integration with Python.

Views: Does It Go Here?
=======================

The largest remaining unsolved problem is how to manage "views" on an MEI document. A "view" is an
MEI document, or a portion of an MEI document, formatted in the way most suitable for another
module's input or output.

Sample Uses
-----------

Example 1: a user creates a new note with the Verovio point-and-click interface, so the LilyPond
representation of that moment should be updated with only that single new note---the whole MEI
document should not need to be converted from scratch. This means sending a single MEI ``<note>``
element to the ``mei_to_ly`` module, including instructions on where the note belongs in the
LilyPond representation.

Example 2: a user selects a two-measure section of music, and asks for nCoda to show it the Abjad
representation of those measures. The ``mei_to_abjad`` module should only be sent two measures.

Example 3: a user uploads a score from the MEI 2013 sample encodings to nCoda. The ``mei_to_mei``
module should be able to "break down" that encoding into Lychee-MEI format and update the Verovio,
LilyPond, and Abjad views of the document.

How It Works
------------

I don't know.

The "view" will be considered twice for every action, and the ``views`` module called twice: once
on the "inbound" to Lychee-MEI, and once on the "outbound" from Lychee-MEI. In order to track the
corresponding sections between documents of different formats, the converter modules must also
provide to the ``views`` module the location of the modifications currently being "inbounded."

Somehow, the ``views`` module will have to retain a bidirectional mapping between locations in
arbitrary-format documents and the ``@xml:id`` attribute in the Lychee-MEI document collection. For
example, in LilyPond documents it would probably be a mapping with line and column numbers; for
Abjad it would probably be a mapping with object ``__id__`` values.

Arbitrary Ideas
---------------

This seems rocky still, and potentially very error-prone. It seems like Lychee would have to create
arbitrary-format documents bit by bit, in order to know the exact correspondences. There are ways to
let LilyPond and Abjad documents know the ``@xml:id`` of an MEI note (or similar): in LilyPond you
might write ``c4) %{id:7229879837498}%`` for example and in Abjad you might add an ``_mei_id``
attribute at runtime.

But 1: this means Abjad documents will have to be largely or partially amended after every update.

But 2: this means users will be faced with useless-to-them, space-consuming comments in their
LilyPond files. GUI editor widgets could help us with this, but then we would need two layers of
abstraction for the same purpose.

Signals: Event-Driven Workflow Management
=========================================

Although signalling systems are conventionally used for event-driven programming, and they will
indeed be used for that in Lychee, they will also manage control flow through Lychee during one-shot
use. Another way to say this: whether run continuously with an event loop, or in a single-action
context through the commandline interface, the ``lychee.signals`` module is responsible for managing
how control flows through the program.

The idea is to define a set of moments through the three-step workflow outlined above, with enough
detail that all required functionality can be triggered by, and will be able to trigger, relevant
signals.

All Lychee modules will be required to follow a signal specification, so that the ``signals`` module
acts as a central point of coordinated interaction between the modules. This will account for the
situation where, for example, two different functions must be run before progressing to the next
step in a workflow, but the order in which they are run is neither important nor deterministic.

Undoubtedly, we will have to design our workflow signals and the ``signals`` module carefully to
eliminate the possibility of a cyclic workflow.

One of the additional requirements for the ``signals`` module is to integrate cleanly and
effectively with other similar mechanisms. The most important concerns will be whatever mechanisms
are used by Frescobaldi (PyQt4 signals) and nCoda (???). For nCoda, we should first try to use
``signals`` itself as the single signalling mechanism, but I expect we'll have to complement it with
a JavaScript-specific signalling library. In both cases, Lychee's ``signals`` module should act as
the overall controller for Lychee-related moments, leaving the other signalling mechanisms to serve
as connection points between Lychee's client applications and Lychee itself.

Signals-and-Slots: Description
------------------------------

For those who aren't familiar with the signal-and-slot mechanism, it's basically a combination of
inter-process communication and inter-module function calls. Consider an example signal,
"mei_updated," which is defined to be triggered whenever the core MEI document is finished being
updated. When this happens, several independent tasks may be required: the VCS should make a new
commit; Verovio should be updated; a new LilyPond file should be outputted. The problem is, these
three things won't always be the same---it depends how the program is configured to run at the
moment: in nCoda, we won't usually be outputting a LilyPond file, but in Frescobaldi we may not
want to use the VCS. Furthermore, because of their dynamic character, it's not necessarily obvious
how to cause all of, and only the, desired functions to be called.

One solution, which I find compelling and we will therefore try to use, is to have signals and slots,
which I believe to have been introduced first with the Qt library. It's basically like an
intermediate, multiplexing function call. Modules that want to know about an event happening will
subscribe to the event's signal. Functions that cause the event will simply call the signal like
any other function. The ``signal`` module keeps track of who has registered for a signal, and when
a signal is triggered, it calls all the registered modules---but not in a known order.

Consider this pseudocode elaboration of the "mei_updated" signal.

.. sourcecode:: python

    def update_mei(change_to_make):
        mei_file.write(change_to_make)
        signals.mei_updated.trigger(mei_file.pathname)

    @signals.mei_updated
    def make_a_commit(pathname):
        if settings.using('hg'):
            hg.add(pathname)
            ref = hg.commit('Made a change to {}'.format(pathname))
            signals.made_commit.trigger(ref)

    @signals.mei_updated
    def output_lilypond(pathname):
        if settings.using('lilypond'):
            mei_to_ly.output()
            signals.lilypond_updated.trigger()

In the previous example, you can see how I've used Python decorators to connect the later two
functions to the "mei_updated" signal. That's just one way to do it. You can also see that those
functions will only do something useful if the runtime settings say they should. Although it's
quite simple, reading this example illustrates some of the ways we might use signals to allow
various parts of the program to interact, even though they don't have to know about each other at
all.

TUI: Commandline Interface
==========================

We can use the ``argparse`` module from the standard library.
https://docs.python.org/3.4/library/argparse.html

For the sketch this will be quite simple, and we can decide how to expand it later on, as required.
Obviously, no essential functionality should be kept in the ``tui`` module because it won't be used
when Lychee is operating on behalf of a GUI application like Frescobaldi or nCoda.
