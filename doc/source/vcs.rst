.. _vcs:

VCS: Version Control System Management
======================================

One of the core nCoda features is integration with a VCS (version control system) through the
:mod:`~lychee.vcs` module. This is potentially a significant advantage for third-party users of
*Lychee* too, many of whom have sought effective VCS integration with LilyPond for years. The
signals in the :mod:`lychee.signals.vcs` module provide an abstraction over the specific version
control system used, which is implemented in this module.

Our first-class VCS is `Mercurial`_, which we chose because it is written in Python and has a
friendly-to-us license. While we admit the Git VCS is significantly more popular than Mercurial,
the possibilities allowed by a VCS written in Python, primarily in terms of extensibility, are too
helpful to ignore.

.. _mercurial: https://www.mercurial-scm.org/

.. warning::
    (August 2016) The *Lychee* version control features are not a primary development priority,
    so we will not invest significant development effort here for several months.

    (September 2016) VCS integration is disabled by default. You can enable VCS support when you
    create an :class:`~lychee.workflow.session.InteractiveSession` instance.

    Version control is a secondary development priority, so we do expect to develop this module
    significantly during 2017. For more information, please refer to
    `this discussion <https://spivak.ncodamusic.org/t/choosing-ncoda-use-cases-july-2016/145>`_
    on *nCoda* Discourse.


How Lychee Uses the VCS (Actual)
--------------------------------

This section describes the current state of version control support in *Lychee* as of August 2016.

Mercurial is always used, and in fact it's required for *Lychee* to start. Every action creates
a new changeset. You can't use *Lychee* to do anything with changesets or the revlog.

There are several related tasks on Phabricator: `T92 <https://goldman.ncodamusic.org/T92>`_,
`T110 <https://goldman.ncodamusic.org/T110>`_, `T111 <https://goldman.ncodamusic.org/T111>`_,
and `T112 <https://goldman.ncodamusic.org/T112>`_.


How Lychee Uses the VCS (Planned)
---------------------------------

.. note::
    This section describes the current implementation plan for version control support in *Lychee*.
    This model poses some challenges, so we may change it significantly before implementation.

*Lychee* allows end users to interact with the VCS only indirectly in most situations. For nCoda,
users will primarily access Mercurial through our *Julius* user interface. We will therefore take
the opportunity to relieve our users of the burden of learning advanced (or non-salient) version
control topics as much as possible. In particular, we want to allow users to learn version control
concepts without worrying about command names, arguments, and the differences between a Git branch
and Mercurial branch.

In addition, nCoda users will not usually manage the *files* in their projects, but rather focus on
musical sections, modifications, and actions. We can take advantage of this situation to offer a
buffer between the revision history and our users: while the *Lychee*
:class:`~lychee.document.document.Document` class manages files in the way most efficient for
computers, and the :mod:`~lychee.vcs` module manages the repository in the way most efficient for
computers, the data we show to users need not necessarily correspond directly to the information
they might see by running ``hg summary``.

In particular, we can take advantage of this "buffer" between the VCS and our users to implement
commit rewriting for session changesets, described immediately below, which might otherwise render
the repository nearly useless.


Session Changesets
^^^^^^^^^^^^^^^^^^

A *session changeset* is a changeset (revision, commit) that we intend to be temporary---it should
not outlive a user's current session. A session changeset represents a single action in the user's
undo/redo stack. Every "change" a user makes will be entered as a changeset and, if it can be
converted successfully, it will be used to update all the views a user has open. When a user
chooses to "save" their work, all the existing session changesets will be "folded" into a single,
permanent changeset.

We can do this using bookmarks and Mercurial's "histedit" extension, shipped by default. We require
three bookmarks through the editing session, which may refer to one, two, or three discrete
changesets. One, called "latest," marks the most recent changeset of either type (session or
permanent). Another, "permanent," marks the most recent permanent changeset from the start of the
user's session (that is, it will not move during an editing session). The final, "session_permanent,"
marks the most recent changeset a user has "saved."

If we only track two bookmarks ("latest" and "permanent") then we effectively discard the undo/redo
stack every time a user "saves." Tracking three bookmarks allows us to undo actions that happened
before the most recent "save."

When a user ends their session, we can use "histedit" to "fold" the changesets between the
"permanent" and "session_permanent" changesets into a single changeset. (In Git, we would use
"interactive rebase" to "squash" the commits between the two "branches" into a single commit).
The updated repository will be uploaded to the nCoda server and/or exported locally to the user's
computer.

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
this before too long. If it comes to it, we can simply delete the backups generated by "histedit."

We will also need to make a replacement "hgeditor" script to allow us to handle the "histedit"
changeset revision file preparation without asking the user to open a text editor.


Branching and Bookmarking
^^^^^^^^^^^^^^^^^^^^^^^^^

In Mercurial, "bookmarks" are mostly equivalent to Git's "branches," while Mercurial's "branches"
represent a permanent diversion in development. Unlike with bookmarks (and Git branches) a changeset
permanently records information about the branch to which it was committed.

I suggest we create a new branch for every user who wants to work on the same document. Merging
between branches is permitted, but the permanent record will help us keep track of who works on
what. It may lead to a situation where popular scores take a lot of time and space to clone for
new users, but there should be a way around this with some of Facebook's Mercurial extensions.


Collaboration and Merging
^^^^^^^^^^^^^^^^^^^^^^^^^

We can use the same mechanisms for viewing changes and differences between "branches," whether
created by a single user with bookmarks or by many users with branches. In the beginning, we can
offer simple merge conflict resolution with ours/theirs-style resolution. Later, we can find a way
to let users resolve merges by themselves.


Mercurial Submodule
-------------------

.. automodule:: lychee.vcs.hg
    :members:
