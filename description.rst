Lychee: The MEI Arbiter
=======================

We need components to do the following functions. The names in this list should be understood as
module names, so you would access the MEI-to-LilyPond converter with
``from lychee.converters import mei_to_ly``.

- converters:
    - mei_to_ly: convert MEI to LilyPond
    - ly_to_mei: convert LilyPond to MEI
    - mei_to_abjad: convert MEI to Abjad
    - abjad_to_mei: convert Abjad to MEI
    - mei_to_mei: convert arbitrary MEI to arbiter-preferred format, and APF to single-file export
- vcs: manage revisions with Mercurial
- views: manage partial "views" on a per-format basis
- signals: coordinate event-driven programming
- tui: textual interface for commandline, "one-shot" use

Generic Workflow
----------------

Regardless of what action is being performed, I *think* we will always use the same three-step
workflow: inbound, document, outbound.

The **inbound** step converts from an arbitrary format to Lychee-MEI, and tells the ``views`` module
what portion of the document is being updated.

The **document** step manages a change to the internal MEI document, and (if relevant) enters the
change to the VCS.

The **outbound** step converts from Lychee-MEI to an arbitrary format, using the ``views`` module
to know which part of the document to update.

Converters
==========

Each converter module, designed in the way most suitable for the module author's skills, provides a
public interface with a single function, convert(), that performs conversions as appropriate for
that module. Thus for example ``lychee.converters.mei_to_ly.convert()`` accepts an MEI document and
produces a LilyPond document.

**Inbound converters** result in a Lychee-MEI document as xml.etree.ElementTree.ElementTree objects
(or Element, in the case of partial documents), along with instructions on what part of the document
is being updated. (The ``views`` module determines which part of the Lychee-MEI this corresponds to).

**Outbound converters** start with a (portion of a) Lychee-MEI document, along with instructions on
what part of the document is being updated. (The ``views`` module determines which part of the
other representation this corresponds to).

LilyPond documents shall always be unicode strings. Abjad documents shall always be ???.

Each converter must be capable of accepting an incomplete document and producing the corresponding
incomplete output, or signalling when the incomplete input is insufficient to produce any output.
For example, ``Element('note', {'pname': 'c'})`` given to the mei_to_ly module will result in
``'c'`` as output, even though the single Element is not a complete and valid MEI document, and the
single-character string is not a complete and valid LilyPond document. Yet if the mei_to_ly module
receives only ``Element('slur', {'plist': '#123 #443'})`` as input, there is not enough information
to produce any sensible output, so the module ought to signal an error.

Future modules will convert data between MEI and MusicXML, and MEI and music21.

Lychee-MEI
----------

It's a subset of MEI, designed to be easier and faster for Lychee software to process. It also has
a unique file layout, with every MEI ``<section>`` kept in its own file (and there will probably be
many sections per score), with a "complete" file that cross-references all the section files (though
in an arbitrary order), and a "playlist" file that cross-references sections files in order as
required to produce the "score itself" as it should appear in music notation.

I'll put an example here.

Special Case: MEI-to-MEI Converter
----------------------------------

We will require an MEI-to-MEI conversion both for inbound and outbound conversions. On the way in,
this will be to convert (nearly?) any valid MEI document into a valid Lychee-MEI document. On the
way out, this will probably mostly be to substitute the appropriate files into a "master file" and
just output it.

VCs: Mercurial Integration
==========================

One of the core nCoda features is integration with the Mercurial VCS (version control system). This
will happen through the ``lychee.vcs`` module, and it will be a significant advantage for interested
Frescobaldi users too. In order to be sure we don't tie our projects' success to that of Mercurial,
to provide a somewhat simpler useage experience for Lychee programmers, and to protect use from
possible changes to Mercurial's Python libraries (which they warn may happen), we should offer this
functionality through a ``vcs`` wrapper module. This will also allow programmers to replace
Mercurial with another VCS system, like Git, which is notably more popular than Mercurial, but
unsuitable for nCoda and suboptimal for integration with Python.

Views: Does It Go Here?
=======================

The largest remaining unsolved problem is how to manage "views" on an MEI document. A "view" is an
MEI document, or a portion of an MEI document, formatted in the way most suitable for another
module.

Example 1: a user creates a new note with the Verovio point-and-click interface, so the LilyPond
representation of that moment should be updated with only that single new note---the whole MEI
document should not need to be converted from scratch. This means sending a single MEI ``<note>``
element to the mei_to_ly module, including instructions on where the note belongs in the LilyPond
representation.

Example 2: a user selects a two-measure section of music, and asks for nCoda to show it the Abjad
representation of those measures. The mei_to_abjad module should only be sent two measures of music.

Example 3: a user uploads a score from the MEI 2013 sample encodings to nCoda. The mei_to_mei module
should be able to "break down" that encoding to follow the nCoda MEI conventions.

So I think the "view" will need to be considered twice for every action: once on the "inbound" from
the arbitrary input format, and once on the "outbound" to the arbitrary output format. It will be
the responsiblity of the ``views`` module to create and manage views, and ensure corresponding
sections are chosen for both the inbound and outbound trips.

Signals: Event-Driven Programming
=================================

Although signalling systems are conventionally used for event-driven programming, and they will
indeed be used for that in Lychee, they will also control flow through the program during
non-interactive use. Another way to say this: whether run continuously with an event loop, or in a
"one-shot" context through the commandline interface, the ``lychee.signals`` module is responsible
for managing control flow through the program.

The idea is that several "workflows" will be defined, with a corresponding set of signals. Other
modules will be required to follow a signal specification, so that ``signals`` will know how to
interact with them.

Undoubtedly, this may potentially cause problems in terms of cyclic execution and the like: what if
*both* updating the MEI file and updating LilyPond output files cause a commit, and triggering a
commit causes the LilyPond and MEI files to be updated? So we'll have to think carefully about how
to design control flow through our signals, and how to eliminate potentially ambiguous and cyclic
workflows.

One of the additional requirements for the ``signals`` module is to integrate cleanly and
effectively with other similar mechanisms. The most important concerns will be whatever mechanisms
are used by Frescobaldi (PyQt4 signals) and nCoda (???). For nCoda, we should first try to use
``signals`` itself as the single signalling mechanism, but I expect we'll have to complement it
by interacting with a JavaScript-specific signalling library. In both cases however, Lychee's
``signals`` module should act as the overall controller, so that other signalling mechanisms will
simply serve as connection points between Lychee's client applications and Lychee itself.

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
