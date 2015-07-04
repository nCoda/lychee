Lychee: The MEI Arbiter
=======================

Lychee manages the MEI document during score editing sessions. Lychee performs nearly-instantaneous
conversion between various representations (Abjad, LilyPond, and MEI) with optional version control
integration, and connections to an event-driven notification system for use in GUI applications.

In a sense, Lychee is the core of the user-facing nCoda app, but it's being developed with
stand-alone use in mind so it may be used by a wider audience.

We need the following components. The names in this list should be understood as importable Python
module names.

- converters:
    - mei_to_ly: convert MEI to LilyPond
    - ly_to_mei: convert LilyPond to MEI
    - mei_to_abjad: convert MEI to Abjad
    - abjad_to_mei: convert Abjad to MEI
    - mei_to_lmei: convert arbitrary MEI to Lychee-MEI
    - lmei_to_mei: convert Lychee-MEI to single-file MEI suitable for export
    - mei_to_ui: output info about the user interface from MEI (see "Converting to UI" below)
    - ui_to_mei: collect info about the user interface from the UI
    - vcs_inbound: accepts operations for the VCS
- vcs: manage revisions with Mercurial
- views: manage partial "views" on a per-format basis
- signals: coordinate event-driven programming
- tui: textual interface for commandline, "one-shot" use

For example, you would access the MEI-to-LilyPond converter with
``from lychee.converters import mei_to_ly``.

Lychee-MEI and "Arbitrary Format"
---------------------------------

Lychee-MEI is a valid subset of MEI. **Lychee-MEI** restricts MEI to encoding strategies that are
easier and safer for computers to process. We will discover new qualifications for Lychee-MEI as we
go along; for now it involves the following characteristics:

- file management:
    - every MEI ``<section>`` is kept in its own file, to ease version control
    - clients are therefore encouraged to use sections generously
    - a "complete" MEI file holds cross-references to all section files, in an arbitrary order
    - a "playlist" MEI file holds cross-references to "active" section files, in score order
- others:
    - tupletSpan, beamSpan, slur, and other elements that may refer to object spans with @startid
      and @endid, and are therefore inherently ambiguous and error-prone, must make use of @plist
      to reduce the possibility of ambiguity and erors
    - use semantic ``@xml:id`` values as described below
    - MEI extension to incorporate commands specific to LilyPond
    - MEI extension to incorporate user metadata (about editing sessions, UI settings, etc.)
    - the <multiRest> element isn't allowed in Lychee-MEI; on conversion from MEI to Lychee-MEI,
      these must be converted to multiple <mRest> elements
    - <dot> element are forbidden in favour of @dot attributes (we may need ``<dot>`` when dealing
      with particular repertoire or critical editions, later, but for now it's an unnecessary
      complication to support)

When this "description" document refers to a music document in an **arbitrary format**, it means the
music document is encoded in one of the formats supported by Lychee (Abjad, LilyPond, MEI) without a
restriction on the particular format used at the moment.

Semantic XML IDs
^^^^^^^^^^^^^^^^

The ``@xml:id`` of an MEI object should be---partially at least---semantic in terms of describing
that object's position within the complete document. We will generate ``@xml:id`` values according
to a pattern concatenating identifiers for section, measure, staff, layer, and an "element" value.
A generic ``@xml:id`` could be ``@xml:id="SXXXXXXX-mXXXXXXX-sXXXXXXX-lXXXXXXX-eXXXXXXX"``.
Consider this example:

.. sourcecode:: xml

    <section xml:id="Sme-m-s-l-e1234567">
        <measure xml:id="S1234567-mme-s-l-e8974095">
            <staff xml:id="S1234567-m8974095-sme-l-e8290395">
                <layer xml:id="S1234567-m8974095-s8290395-lme-e7389825">
                    <note xml:id="S1234567-m8974095-s8290395-l7389825-e7290542" />
                </layer>
            </staff>
            <slur xml:id="S1234567-m8974095-s-l-e3729884" />
        </measure>
    </section>

From this you can see:

- every element has a unique "e" part
- elements that determine the id of contained elements have "me" at the level of their id that
  corresponds to that element's tag. For example, the staff has ``-sme-l-e8290395`` in its id. This
  is saying "the staff is me, and elements I contain should have '8290395' in their id."
- the ``<slur>`` not inside a ``<staff>`` or ``<layer>`` simply has "s" and "l" without identifiers
- seven-digit unique identifiers for every object in the "e" part. We could use shorter ones too,
  because the "e" part doesn't need to be unique across all elements in the document---only within
  that combination of the document hierarchy. It's feasible but probably unnecessary to ensure
  uniqueness of the whole id by iterating through all the objects at a particular hierarchic level.
  Adding a second ``<note>`` to the example above would involve checking only the existing
  ``<note>`` for an id clash.

One other thing: this gives Lychee a systematic way to name files. The section example above could
be named "Sme-m-s-l-e1234567.mei".

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

Note that the "conversion" steps do not necessarily work as simple format converters for musical
information. For example, the ``mei_to_ui`` converter module issues changes for the user interface
according to changes in the MEI document. As another example, the ``vcs_inbound`` module allows
users to issue version control commands, like making a commit or switching to a different branch.

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

Each converter must be capable of accepting an incomplete document and producing the corresponding
incomplete output, or emitting an error signal if the incomplete input is insufficient to produce
corresponding valid output. For example, ``Element('note', {'pname': 'c'})`` given to the
``mei_to_ly`` module should result in ``'c'`` as output, even though the single Element is not a
complete and valid MEI document, and the single-character string is not a complete and valid
LilyPond document. Yet if ``mei_to_ly`` receives ``Element('slur', {'plist': '#123 #443'})`` as
input, there is not enough information to produce any sensible output, so the module ought to emit
an error signal.

Future modules will convert data between MEI and MusicXML, and MEI and music21.

Also note that a conversion through Lychee from one format to the same format, like
LilyPond-to-MEI-to-LilyPond, need not produce an identical file at the end. Although the content
must be identical, its formatting does not need to be.

Special Case: MEI-to-MEI Converter
----------------------------------

We will require an MEI-to-MEI conversion both for inbound and outbound conversions. On the way in,
this will be to convert (nearly?) any valid MEI document into a valid Lychee-MEI document. On the
way out, this will probably mostly be to substitute the appropriate files into the "playlist" file.

Special Case: Converting to UI
------------------------------

Another unusual situation is the storage of user interface settings and usage data in MEI. We will
need to extend MEI to deal with this information. It may then still be application-specific (not
transferrable between applications that use Lychee) and will not likely be incorporated into the
"upstream" MEI standard.

We can store all sorts of things here, so every musical document is like a "session" in an IDE (or
at least a "session" in the Kate text editor, if that helps anyone). We can even store things to
the detail of what proportion of the screen is occupied by various interface components. We can
still manage this with the generic workflow, and maybe in the style of the *React.js* GUI framework:
a user will make the motion to change a dial, and they'll think they changed the dial, but really
they caused a change that was put into Lychee, stored in the MEI file, and then the dial was told
by Lychee that it should update its position.

These "conversions" will be handled by the ``mei_to_ui`` and ``ui_to_mei`` modules.

Special Case: VCS Inbound
-------------------------

The ``lychee.converters.vcs_inbound`` module allows operations with the ``lychee.vcs`` module.
Possible user actions are described in the following section, "VCS: Mercurial Integration."

VCS: Mercurial Integration
==========================

One of the core nCoda features is integration with a VCS (version control system) through the
``lychee.vcs`` module. This will be a significant advantage for Frescobaldi users too, many of whom
have already been tracking their projects in VCS repositories for years. The ``vcs`` module serves
as an abstraction layer between Lychee and the VCS itself; this allows us to change the actual VCS
in use without affecting Lychee beyond the ``vcs`` module. We may also choose to support multiple
VCS programs simultaneously.

The initial default VCS will be Mercurial, which we have chosen primarily for two reasons: first,
it is written in Python, and therefore can provide tighter integration with Lychee, which is also
written in Python; second, it is written in Python, and can therefore be run with nCoda's in-browser
Python solution. Although the Git VCS is notably more popular than Mercurial in 2015, it lacks the
integration and cross-compilation possibilities of Mercurial, and is therefore less suitable as an
initial default for Lychee.

Interacting with the VCS
------------------------

Usual use cases of a VCS have users interacting with the VCS directly, in order to change the files
under version control. The situation is different in Lychee for a number of reasons. First, learning
how to use a VCS is actually a terrible burden on users, so we want to try simplifying it as much
as possible while still taking advantage of as many beenfits as possible. Second, at least in nCoda,
users will not manipulate the repository's files directly, so VCS changes must be communicated to
users through an outbound converter. Finally, again at least in nCoda, we don't expect users to
learn the VCS *technology*---just VCS *concepts*. What that means in practice is, for example,
that we would like users to know they can switch between "revisions" that they "saved," but
there is no reason to have them learn that in Mercurial you switch between "changesets" that you
"commit," and in Git you switch between "commits" that you "commit."

Session Changes
---------------

Lychee has an idea of **session changes**, which is a temporary revision. These were created to
represent single actions in the undo/redo stack. The idea is that every "change" a user makes will
be entered as a session change and, if it can be converted successfully, it will be reflected in
all the views the user has open. When a user chooses to "save" their work, all the existing session
changes will be compressed to a single revision (changeset/commit) and the session change revisions
will be discarded.

Session changes can be stored in Mercurial as a patch in a Mercurial Queue, as a changeset proper,
and possibly as other things. The simplest implementation solution will be best, so we should use
proper changesets if possible. In that case, we can use a bookmark to track the most recent
permanent changeset, and we'll need to "rewrite history" to rewrite the session changes as a single
permanent changeset. However, this may cause a lot of garbage in the repository, and it may be
impractical to clean up as often as might be required. In that case, we can investigate Mercurial
Queues (MQ) which basically amount to a per-user micro-VCS on top of the rest of Mercurial. The key
advantage here is that the MQ patch stack can be (1) completely deleted after a proper changeset is
created, or (2) committed in a changeset.

An interesting side-effect of representing the undo/redo stack with what we're calling session
changes is that, in effect, the undo/redo stack can potentially be shared between users and across
actual editing sessions. That's kind of weird, but I can imagine it may prove quite popular. It's
sort of like a complicated auto-save feature, but without much of the baggage that would come with
developing that separately.

One might rightly ask why we would bother differentiating between session changes and permanent
changesets. There are at least two reasons, one practical and one technical. The practical reason
is that a portion of users---most users, I hope---will find it significantly advantageous to be able
to create annotated changesets of their work, that server as milestones along the creative or
researchive process. The technical reason is that, as users work on a project for a long time, they
will accumulate a large number of session changes, and it would be tremendously inefficient to have
all of these stored permanently as changesets in the repository.

If we're crafty about it, we can allow users to group and rewrite session
changes in the same way as they may group and rewrite permanent revisions. That is to say, as users
may go along composing a new piece of music, they may realize sessionchange-0 to sessionchange-55
represent a single new artistic development and should be saved as a permanent changeset, even
though they've already started working on other things, and the most recent sesion change is 99. So
it's basically like "save some of what you did." But I don't know whether we can allow users to save
only their work in *x* files... we'll have to see about that.

Though not all users will be so eager to manage their revisions like this. We'll need to come up
with some limit, like 5,000 session changes, at which point Lychee will automatically suggest that
the user will "compress," say, the most recent 2,500 session changes into a single permanent
changeset. And if they choose not to do it, at some point, like 10,000 session changes, we might
just say to the user "stop being ridiculous, we need to cut down on these commits." But nicely.

Bookmarking
-----------

We have to do this too, but it's not a big deal. In Mercurial, "bookmarks" are basically equivalent
to Git's branches, so that's what's going on here.

Branching
---------

Mercurial also has a feature called "branches," and they're for permanently divergent sets of work.
For example, in Git you would make a "branch" for development, another "branch" for a stable release
series, and then "tags" for each release. In Mercurial, you would make a "bookmark" to track your
development, a "branch" for a stable release series, and "tags" for each release. In effect it's
mostly the same, just that Mercurial sort of forces branches to be permanent but bookmarks to be
movable and dynamic, whereas Git suggests using branches both for permanent and dynamism.

Anyway, the point is: is there a place for Mercurial branches? Is this distinction something that
we should expose to our users?

Collaboration and Merging
-------------------------

I don't know how to handle this yet.

Views: Does It Go Here?
=======================

The largest remaining unsolved problem is how to manage "views" on an MEI document. A "view" is an
MEI document, or a portion of an MEI document, formatted in the way most suitable for another
module's input or output (for example, a measure from an Abjad score).

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

I don't know, but (1) we will probably need "views-trackers" for every supported external format,
and (2) there has already been some work in this area by, for example, the Frescobaldi people. There
may have been useful research conducted in other disciplines, or for unrelated applications.

In any case, the "view" will be considered for the "inbound" step, and once for every "outbound"
format. The ``views`` module will have to retain information about what portion of the document was
"inbounded" so it can properly process the outbound placement.

Per-format views-trackers will keep a bidirectional mapping between the location of an object in
arbitrary-format documents and the ``@xml:id`` attribute of its Lychee-MEI representation. This
information should be submitted to the VCS so that Lychee will not need to regenerate it. In any
case, the initial generation of correspondence data may be very time consuming.

Positions in LilyPond documents can be recorded with line and column numbers. Abjad correspondences
could be tracked with ``__id__`` values (but that might require significant work when the document
is first created).

Signals: Event-Driven Workflow Management
=========================================

Although signalling systems are conventionally used for event-driven programming, and they will
indeed be used for that in Lychee, they will also manage control flow through Lychee during one-shot
use. Another way to say this: whether run continuously with an event loop or in a single-action
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
are used by Frescobaldi (PyQt4 signals) and nCoda (???) for the user interfaces. For nCoda, we
should first try to use ``signals`` itself as the single signalling mechanism, but I expect we'll
have to complement it with a JavaScript-specific signalling library. In both cases, Lychee's
``signals`` module should act as the overall controller for Lychee-related activities, leaving the
other signalling mechanisms to serve as connection points between Lychee's client applications and
Lychee itself.

Signals-and-Slots: Description
------------------------------

For those who aren't familiar with the signal-and-slot mechanism, it's basically a combination of
inter-process communication (IPC) and regular function calls. Signals are defined and called with
function-like signatures, but (as with IPC) the caller doesn't know specifically which function is
called in the end. And there are no return values.

Consider an example signal, "mei_updated," which is defined as being triggered whenever the core
MEI document is finished being updated. When the MEI document has been updated, several independent
tasks may be required: the VCS may make a new commit; Verovio may be updated; a new LilyPond file
may be outputted. The problem is that the required tasks won't always be the same---it depends how
the program is configured to run at the moment. In nCoda, we won't usually be outputting a LilyPond
file, but in Frescobaldi we may not want to use the VCS. Furthermore, because of their dynamic
character, it's not necessarily obvious how to cause all of, and only the, desired functions to be
called.

The solution we will try is using the signals-and-slots mechanism, which acts in this case like an
intermediate, multiplexing function call. Some configuration management module "registers" a slot
with a signal. When the signal is "emitted," all the registered slots will be called in an
arbitrary order. It is the signal's responsibility to keep track of all its registered slots.

Consider this pseudocode elaboration of the "mei_updated" signal.

.. sourcecode:: python

    def update_mei(change_to_make):
        mei_file.write(change_to_make)
        signals.mei_updated.emit(mei_file.pathname)

    def make_a_commit(pathname):
        if settings.using('hg'):
            hg.add(pathname)
            ref = hg.commit('Made a change to {}'.format(pathname))
            signals.made_commit.emit(ref)

    def output_lilypond(pathname):
        if settings.using('lilypond'):
            mei_to_ly.output()
            signals.lilypond_updated.emit()

    signals.mei_updated.register(make_a_commit)
    signals.mei_updated.register(output_lilypond)

In this example, I've called the ``register()`` method on a signal to connect a slot. When some
other function, not shown here, calls ``update_mei()``, the "mei_updated" signal will be emitted,
causing both ``make_a_commit()`` and ``output_lilypond()`` to be called. They will both receive the
same argument that the signal was emitted with.

TUI: Commandline Interface
==========================

We can use the ``argparse`` module from the standard library.
https://docs.python.org/3.4/library/argparse.html

For the sketch this will be quite simple, and we can decide how to expand it later on, as required.
Obviously, no essential functionality should be kept in the ``tui`` module because it won't be used
when Lychee is operating on behalf of a GUI application like Frescobaldi or nCoda.
