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
- document: manage the MEI document in memory, coordinating with its representation in files
- vcs: manage revisions with Mercurial
- views: manage partial "views" on a per-format basis
- signals: coordinate event-driven programming
- tui: textual interface for commandline, "one-shot" use

For example, you would access the MEI-to-LilyPond converter with
``from lychee.converters import mei_to_ly``.


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

Every action Lychee performs will use the same basic workflow with four steps: inbound, document,
vcs, and outbound.

The **inbound** step converts from an arbitrary format to Lychee-MEI. When running in interactive
mode, the ``views`` module is given information on what portion of the document is being updated.

The **document** step manages changes to the internal MEI document, determining which specific files
must be modified, and creating or deleting them as required. In some situations, this step will be
skipped entirely if, for example, the user requested to see a different changeset from the VCS,
which won't require any changes in this step.

The **vcs** step manages the VCS repository in which the project is being managed. New changes will
be entered in a new revision, but other actions are possible depending on the user's actions. This
step may be skipped entirely if Lychee is configured not to use a VCS.

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

Note that converter modules will always convert between Lychee-MEI and another format. However, the
@xml:id values assigned by the converter modules will not conform to the Lychee-MEI guidelines; they
should instead be used by the converter module to help track the correlation between objects in
their LMEI and external representation. The ``views`` module is responsible for converting the
@xml:id attributes from format-specific to Lychee-MEI values (and will not work without its ability
to do so). For this reason, the converters' @xml:id attributes must not change unless an element is
changed (meaning it is new or it replaces an element in Lychee's existing internal representation)
and that the converter-assigned @xml:id must change if an element does change.

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

Special Case: Converting from UI
--------------------------------

Every change the user makes in the interface, if it's a change that may contribute to changing the
musical score proper, as stored in MEI, must be recorded in the MEI itself. What this means in
practice is that we're likely to need a separate MEI-like file (that will really hold data part of
a custom MEI extension) in the repository to hold these changes, and we'll have to find some way to
manage the abundance of information this will create.

Here's the problem: if we're using the VCS to manage the undo/redo stack (which we are---see
"Session Changesets" below) then it's likely that we'll end up generating a lot of changes that
won't convert successfully into MEI, and therefore can't be saved in the VCS and, by extension,
therefore can't be saved into the undo/redo stack. (Why so many changes that can't be converted to
valid MEI? Because I predict users will start writing something, pause to think part-way through,
and the pause will be long enough to cause a new undo/redo commit).

Therefore... ? I'm still thinking about how we can deal with this. It may just be a silly idea to
manage the undo/redo stack in a Mercurial repository!

Special Case: VCS Inbound
-------------------------

The ``lychee.converters.vcs_inbound`` module allows operations with the ``lychee.vcs`` module.
Possible user actions are described in the following section, "VCS: Mercurial Integration."

The Document Module
===================

The ``document`` module is responsible for managing and coordinating the in-memory ``Element``
representation of the MEI document with the in-files representation, and also negotiating updates
to portions of those document representations.

There are three "touch points" for where such document management is required:
    1. incorporating the inbound change to the document,
    1. "sectionalizing" that change into files, and
    1. sending updated portions of the document for outbound listeners.

Document manipulation will always take place in ``<section>`` elements. At first, this will be
restriected to top-level section---the ``<section>`` that is "highest" in the element hierarchy.
We will build the functionality to update subsections, but doing it initially seems too complicated.

The ``document`` module will handle requests for portions of the document in memory as ``Element``
objects, to be used by the inbound and outbound converters. The module will also save the
``Element`` structure into, and load it from, per-``<section>`` files. This sounds completely
straight-forward, but I expect that managing the cross-references between Lychee-MEI documents is
going to be complicated enough to warrant a separate module.

Initially, other modules will only be able to request (for modification or outbound converstion)
and submit (the modified) document as a whole. The VCS can determine for itself whether particular
per-``<section>`` files have been modified and should be committed. New elements submitted from the
inbound conversion will be assigned @xml:id values, and the ``views`` module will learn what they
are during outbound conversion.

In the medium term, hopefully before we release the prototype, modules will be able to request and
submit specific ``<section>`` elements. In the long term, Lychee should be able to take a "smallest
viable container" approach, working down to the ``<layer>``. We should limit the level of
optimization though, because the goal of requesting/using smaller document sections to begin with
is to reduce processing time spent with portions of the document that aren't being chaged. If the
partial-updates algorithm ends up costing just as much time, we're not really solving the problem.

VCS: Mercurial Integration
==========================

One of the core nCoda features is integration with a VCS (version control system) through the
``lychee.vcs`` module. This is a significant advantage for Frescobaldi users too, many of whom
have held their projects in VCS repositories for years. The ``vcs`` module is an abstraction layer
between Lychee and the VCS itself. This allows changing the actual VCS we use without affecting
Lychee beyond the ``vcs`` module. We may also support choosing between VCS programs at runtime.

The initial VCS is Mercurial, which we have chosen primarily because it is written in Python, which
yields two significant advantages. First, we can import Mercurial as a module directly into
``lychee.vcs``. Second, Mercurial can use nCoda's in-browser Python runtime without having to
cross over into another language. Even though the Git VCS is notably more popular than Mercurial
in 2015, the it poses unnecessary integration challenges for an initial solution.

Interacting with the VCS
------------------------

In their usual use cases, users will interecat with the VCS directly to manage the files under
version control. In Lychee, users will interact with the VCS indirectly through our GUI. We should
take this opportunity to relieve our users of the burden of learning advanced version control
topics. In particular, we want to allow users to learn about version control concepts without
having to remember command names or the differences between a *changeset* and a *commit*.

In addition, nCoda users will not be managing the *files* in their projects, since the focus is
rather on *musical sections*. Although each section is effectively stored in a file, Lychee will
use additional files for its own purposes, as described above in the "Lychee-MEI" section. For this
reason, even Frescobaldi users will usually want to be isolated from the files themselves, although
it will be easier for them to access the files and the VCS directly if they desire.

Session Changesets
------------------

A *session changeset* is a changeset (revision, commit) that we intend to be temporary---it should
not outlive a user's current session. A session changeset represents a single action in the user's
undo/redo stack. The idea is that every "change" a user makes will be entered as a changeset and,
if it can be converted successfully, it will be used to update all the views a user has open. When
a user chooses to "save" their work, all the existing session changesets will be "folded" into a
single, permanent changeset.

We can do this using Mercurial's "histedit" command, which is shipped by default, and bookmarks. We
will need to keep three bookmarks through the editing session, which may refer to one, two, or three
changesets. One, called "latest," marks the most recent changeset of either type. Another,
"permanent," marks the most recent permanent changeset from the start of the user's session (that
is, it will not move during a session). The final, "session_permanent," marks the most recent
changeset a user has "saved."

If we only track two bookmarks ("latest" and "permanent") then we effectively discard the undo/redo
stack every time a user "saves." Tracking three bookmarks allows us to undo actions that happened
before the most recent "save."

When a user ends their session, we can use "histedit" to "fold" the changesets between the
"permanent" and "session_permanent" changesets into a single changeset. (In Git, we would use
"interactive rebase" to "squash" the commits between the two "branches" into a single commit).
Any new changesets will be uploaded to the shared nCoda server, and/or somehow exported locally
to the user's own computer.

If a user wants to "save" while their "latest" changeset is "before" their "permanent_session"
changeset, or has effectively created a new "branch," we can offer to create for them a "branch"
in the GUI, which will be depicted similarly to Git branches (but differently than Mercurial
branches).

An interesting side-effect of representing the undo/redo stack with changesets is that, in effect,
users can share the undo/redo stack between users and across actual editing sessions. I think we
should disallow this, at least initially. Session changesets will be marked as "draft" (changing to
"public" when they are made "permanent" at the end of a session).

A drawback to this approach is that session changesets will be preserved in the repository's ``.hg``
directory so that users can revise their revised changesets. While this makes some sense for
programmers using Mercurial, Lychee will generate a new changeset with every user action, leading
to a large number of unused changesets relatively quickly. Furthermore, since users won't be
accessing their repository directly, these backup files are an outright waste of space. Thankfully,
these backups don't appear to be synchronized or pushed to servers, though we will have to confirm
this before too long. If it comes to it, we can simply delete the backup files.

We will also need to make some replacement "hgeditor" script that will allow us to handle the
"histedit" changeset revision file preparation without having to ask the user to open a text editor.

Branching and Bookmarking
-------------------------

In Mercurial, "bookmarks" are mostly equivalent to Git's "branches," while Mercurial's "branches"
represent a permanent diversion in development. Unlike with bookmarks (and Git branches) a changeset
permanently records information about the branch to which it was committed.

I suggest we create a new branch for every user who wants to work on the same document. Merging
between branches is permitted, but the permanent record will help us keep track of who works on
what. It may lead to a situation where popular scores take a lot of time and space to clone for
new users, but there should be a way around this with some of Facebook's Mercurial extensions.

Collaboration and Merging
-------------------------

We can use the same mechanisms for viewing changes and differences between "branches," whether
created by a single user with bookmarks or by many users with branches. In the beginning, we can
offer simple merge conflict resolution with ours/theirs-style resolution. Later, we can find a way
to let users resolve merges by themselves.

Views: Does It Go Here?
=======================

A **view** is a (portion of) a Lychee-MEI document, stored in another format (Abjad, LilyPond, MEI).
The ``views`` module tracks correlation between musical objects separately for every format, in two
mappings between a Lychee-MEI-compliant @xml:id value assinged by the ``views`` module itself and
the @xml:id values assigned by ``converters`` submodules. Therefore, it is the responsiblity of the
``views`` module to assign Lychee-MEI-compliant @xml:id attributes to the LMEI data it receives.

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

How It Works: Example
---------------------

This example converts from an Abjad/LilyPond/music21-like data format that doesn't exist. The
inbound converter receives three Note objects:

    >>> inbound = [Note('c4'), Note('d4'), Note('e4')]

Each note has a ``_lychee_id`` attribute:

    >>> inbound[0]._lychee_id
    'note-123'
    >>> inbound[1]._lychee_id
    'note-456'
    >>> inbound[2]._lychee_id
    'note-789'

They're converted to Lychee-MEI *but* with @xml:id attributes that match the other format's
``_lychee_id``:

    >>> inbound_mei = convert(inbound)
    >>> inbound_mei[0].tag
    Note
    >>> inbound_mei[0].get('xml:id')
    'note-123'

The ``views`` module replaces the @xml:id attributes with proper Lychee-MEI values. (And the values
of any element/attribute that refers to that @xml:id). ALong the way, ``views`` also generates
mappings between the external format's "id" and the corresponding Lychee-MEI @xml:id.

    >>> extern_to_mei_ids = {}
    >>> mei_to_extern_ids = {}
    >>> for element in every_element_in_the_score:
    ...     this_id = make_new_xml_id()
    ...     extern_to_mei_ids[element.get('xml:id')] = this_id
    ...     mei_to_extern_ids[this_id] = element.get('xml:id')
    ...     element.set('xml:id', this_id)
    ...
    >>>

The next time there's a change in the external-format, the ``views`` module has the context it needs
to determine context for the changes.

    >>> new_inbound = [Note('c4'), Note('d-4'), Note('e4')]
    >>> new_inbound[0]._lychee_id
    'note-123'
    >>> new_inbound[1]._lychee_id
    'note-912'
    >>> new_inbound[2]._lychee_id
    'note-789'

As long as we have enough context, the ``views`` module can determine that the ``Note`` that
previously had the id ``456`` should be replaced, and the surrounding two notes remain unchanged.
In addition, if there's an inbound change originating from a view in another format, we can use the
``mei_to_extern_ids`` mapping to know the ``_lychee_id`` values of the external-format objects that
have been modified.

Note that the "context" will initially be the whole document and soon the nearest ``<section>``.
Ideally we'll be able to narrow this down to ``<measure>`` or other similarly-sized containers.

For Abjad
^^^^^^^^^

Abjad objects are slotted, meaning we cannot add arbitrary attributes at runtime. Hopefully the
Abjad developers will create a purpose-built attribute for our use to hold an "id" value to use in
the ``views`` module. We can avoid having to recreate these attributes from scratch every time the
application starts by using the ``jsonpickle`` package to serialize our Abjad score into a text
file. This JSON data can also be stored in the VCS repository, if one is in use.

For LilyPond
^^^^^^^^^^^^

Positions in LilyPond documents can be recorded with line and column numbers. This may cause
problems if users like to reformat their files often, but (1) there can be ways around this, and
(2) if our converters are slow enough that this causes a problem, then we have other, bigger
problems to worry about.


TUI: Commandline Interface
==========================

We can use the ``argparse`` module from the standard library.
https://docs.python.org/3.4/library/argparse.html

For the sketch this will be quite simple, and we can decide how to expand it later on, as required.
Obviously, no essential functionality should be kept in the ``tui`` module because it won't be used
when Lychee is operating on behalf of a GUI application like Frescobaldi or nCoda.
