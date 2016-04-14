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

Lychee-MEI and "Arbitrary Format"
---------------------------------

Lychee-MEI is a valid subset of MEI. **Lychee-MEI** restricts MEI to encoding strategies that are
easier and safer for computers to process. We will discover new qualifications for Lychee-MEI as we
go along; for now it involves the following characteristics:

- file management:
    - every MEI ``<section>`` is kept in its own file, to ease version control
    - clients are therefore encouraged to use sections generously
    - a "project" MEI file holds cross-references to all section files, in an arbitrary order
    - a "score" MEI file holds cross-references to "active" section files, in score order
- others:
    - use semantic ``@xml:id`` values as described below
    - MEI extension to incorporate commands specific to LilyPond
    - MEI extension to incorporate user metadata (about editing sessions, UI settings, etc.)
    - the ``<multiRest>`` element isn't allowed in Lychee-MEI; on conversion from MEI to Lychee-MEI,
      these must be converted to multiple ``<mRest>`` elements
      - ``<mRest>`` elements must be given a @dur attribute (and @dots if relevant)
    - ``<dot>`` element are forbidden in favour of @dot attributes (we may need ``<dot>`` when
      dealing with particular repertoire or critical editions, later, but for now it's an
      unnecessary complication to support)
    - when the @accid attribute is used on an element, the @accid.ges attribute must be used too;
      using @accid.ges doesn't require @accid, however
    - both @num and @numbase are required on every ``<tupletSpan>``
- spanners:
    - tupletSpan, beamSpan, slur, and other elements that may refer to spanner object with @startid
      and @endid, and are therefore inherently ambiguous and error-prone, must additionally use the
      @plist attribute to reduce the possibility of ambiguity and erors
    - spanners that may be encoded as either an element containing other elements (like ``<tuplet>``)
      or as a pointing element (like ``<tupletSpan>``) must use the pointing version
    - spanner elements must be sibling elements to the element indicated by its @startid attribute,
      and the spanner must precede the @startid element
    - the @plist attribute must include all child elements, not just immediate children (so in a
      nested tuplet, the highest-level <tupletSpan> will have in its @plist all of the notes/rests
      in that and all contained <tupletSpan> elements
    - collectively, these restrictions eliminate the need for a multiple-pass parser
    - for a spanner that contains another spanner, the element defining the inner spanner must
      appear in the document *after* the element defining the outer spanner. This is implied in the
      previous rules, but specified more clearly here for consistency.
- @n attributes:
    - for containers that require an @n attribute, the values must be enumerated from 1, incremented
      by 1, and start with the highest or left-most sub-container, as applicable
    - this means the first ``<section>`` will have ``@n="1"``, the next ``@n="2"``, and so on
        - an "inactive" ``<section>``, not part of the current "score," should have an ``@n="0"``
          value
    - this means the highst ``<staff>`` will have ``@n="1"``, the next ``@n="2"``, and so on
    - this means the ``<layer>`` of the "upper voice" will have ``@n="1"``, the "lower voice"
      ``@n="2"``, a subsequent "upper voice" ``@n="3"``, and so on (the goal being that "upper"
      voices with upward-pointing stems will have odd values of @n, and "lower" voices with
      downward-pointing stems will have even values of @n)
    - implication: when a sub-container is added or removed from a container (e.g., a ``<layer>``
      removed from  a ``<staff>``) the @n values of following sub-containers must be adjusted
    - additionally, the @n attribute of an element must be equal to the @n attribute of the
      corresponding element in other contexts (i.e., the principal flute's ``<staff>`` should be
      ``@n="1"`` in every ``<measure>``
    - because these rules specify extra precision for which standard MEI would require such
      attributes as @prev and @next, the LMEI-to-MEI converter should add those attributes
- ``<measure>`` elements:
    - This is a large and notable difference between MEI and Lychee-MEI that makes them incompatible
    - In MEI for mensural music, sections contain measures contain staves contain layers/voices. For
      non-mensural music sections contain staves contain layers/voices. This represents a fundamental
      difference between the element hierarchy for mensural and non-mensural music, where changing
      that characteristic forces significant change to a document's encoding into ``<staff>``
      elements: in non-mensural music, there will be one ``<staff>`` per part, but in mensural music
      every part has a new ``<staff>`` element for every measure. Thus, changing a score between
      mensural and non-mensural encodings represents a significant change to the document's encoding.
      Moreover, writing a document management tool that will correctly and consistently operate on
      *both* non-mensural and mensural music seems much more daunting in this situation.
    - Thus, while we understand and sympathize with the motivation for holding ``<staff>`` elements
      as children of ``<measure>`` elements in MEI, we find this to be less suitable for Lychee.
    - Therefore our nesting will work like this:
        ``<section>``
            ``<staff>``
                ``<measure>``
                    ``<layer>``
      Where the ``<measure>`` element is optional.
    - Therefore, a mensural Lychee-MEI document is incompatible with a mensural MEI document. We
      will use the MEI-to-MEI converter modules to convert between these two. Computationally, we
      don't expect a particular burden because (thanks to the rule about @n attributes) we can use
      a simple XPath query to find corresponding elements. Either all ``<measure>`` elements with
      the same @n attribute belong to "the same measure," or all ``<staff>`` elements with the same
      @n attribute belong to "the same staff."
- Limitations on ``<scoreDef>`` and ``<staffDef>``:
    - To the fullest extent possible, every ``<staffDef>`` must appear within a ``<scoreDef>``.
    - Also as much as possible, both elements must only appear as the first element within a
      ``<section>``. It may not always be possible to abide by this rule, so exceptions may be
      clarified in the future.
    - Every ``<staffDef>`` element must have an @n attribute that is the same as the corresponding
      ``<staff>`` element(s).
- Limitations on ``<meiHead>``:
    - All title parts must be contained in a single ``<title>`` element, and use of the @type
      attribute is mandatory, with the possible values being those suggested by the MEI Guidelines:
      main, subordinate, abbreviated, alternative, translated, uniform. This means every ``<meiHead>``
      element will contain at least two ``<title>`` elements.
    - The ``<respStmt>`` element contains ``<persName>`` elements referring to Lychee users.
      Contributors who have not used Lychee (or a Lychee client application) should be identified
      only with a more specific child element in the ``<titleStmt>``.
    - The ``<persName>`` in ``<respStmt>`` should use child elements with @type="full", @type="given",
      @type="other", and @type="family" attributes to encode name parts. Use as many as possible,
      but only with values provided specifically by end users. That is, if a user provides only their
      full name, it should not be automatically encoded as parts; likewise, if a user only provides
      their name in parts, it should not be automatically encoded as a full name.
    - The @xml:id on an outer ``<persName>`` element should simply be a UUID, and need not follow
      the semantic @xml:id assignment scheme used for musical elements. However, this value must be
      an NCName, and must therefore start with a letter.
    - If the arranger, author, composer, editor, funder, librettist, lyricist, or sponsor elements
      identify someone who is also represented in the ``<respStmt>``, then the ``<persName>`` in
      the specific identifier should use a @nymref attribute with the @xml:id value of the
      ``<persName>`` in the ``<respStmt>``.

When this "description" document refers to a music document in an **arbitrary format**, it means the
music document is encoded in one of the formats supported by Lychee (Abjad, LilyPond, MEI) without a
restriction on the particular format used at the moment.

Semantic XML IDs
^^^^^^^^^^^^^^^^

The ``@xml:id`` of an MEI object should be---partially at least---semantic in terms of describing
that object's position within the complete document. We will generate ``@xml:id`` values according
to a pattern concatenating identifiers for section, staff, measure, layer, and an "element" value.
A generic ``@xml:id`` could be ``@xml:id="SXXXXXXX-sXXXXXXX-mXXXXXXX-lXXXXXXX-eXXXXXXX"``.
Consider this example:

.. sourcecode:: xml

    <section xml:id="Sme-s-m-l-e1234567">
        <staff xml:id="S1234567-sme-m-l-e8974095">
            <measure xml:id="S1234567-s8974095-mme-l-e8290395">
                <layer xml:id="S1234567-s8974095-m8290395-lme-e7389825">
                    <note xml:id="S1234567-s8974095-m8290395-l7389825-e7290542" />
                </layer>
                <slur xml:id="S1234567-s8974095-m8290395-l-e3729884" />
            </measure>
        </staff>
    </section>

From this you can see:

- every element has a unique "e" part
- elements that determine the id of contained elements have "me" at the level of their id that
  corresponds to that element's tag. For example, the measure has ``-mme-l-e8290395`` in its id.
  This is saying "the measure is me, and elements I contain should have '8290395' in their id."
- the ``<slur>`` inside a ``<measure>`` but not ``<layer>`` simply has "l" without an identifier
- seven-digit unique identifiers for every object in the "e" part. We could use shorter ones too,
  because the "e" part doesn't need to be unique across all elements in the document---only within
  that combination of the document hierarchy. It's feasible but probably unnecessary to ensure
  uniqueness of the whole id by iterating through all the objects at a particular hierarchic level.
  Adding a second ``<note>`` to the example above would involve checking only the existing
  ``<note>`` for an id clash.

One other thing: this gives Lychee a systematic way to name files. The section example above could
be named "Sme-s-m-l-e1234567.mei".

Cross-References with Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Lychee-MEI shall maintain a file called ``all_files.mei`` in which cross-reference links are kept
to all other MEI files in the repository. These cross-references shall use the ``<ptr>`` element.

- the @target attribute holds a URL to the other file, relative to ``all_files.mei``
- @targettype may be ``"section"``, ``"score"``, ``"ui"``, or ``"head"``, as appropriate
- @xlink:actuate shall be ``"onRequest"``
- @xlink:show shall be ``"embed"``

<meiCorpus>
    <meiHead>
        <ptr targettype="head" target="meihead.xml" xlink:actuate="onRequest" xlink:show="embed"/>
    </meiHead>
    <mei>
        <ptr targettype="score" target="score.xml" xlink:actuate="onRequest" xlink:show="embed"/>
        <ptr targettype="section" target="Sme-s-m-l-e4837298.mei" xlink:actuate="onRequest" xlink:show="embed"/>
        <ptr targettype="section" target="Sme-s-m-l-e9376275.mei" xlink:actuate="onRequest" xlink:show="embed"/>
        ...
    </mei>
</meiCorpus>

Note that this isn't valid MEI. It should be, and I'll figure out how later, but I just can't seem
to find a useful place for a <ptr> like this.

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

This documentation has been moved to the "lychee.views.__init__" module.


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
