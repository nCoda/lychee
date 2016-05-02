Lychee: The MEI Arbiter
=======================


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



TUI: Commandline Interface
==========================

We can use the ``argparse`` module from the standard library.
https://docs.python.org/3.4/library/argparse.html

For the sketch this will be quite simple, and we can decide how to expand it later on, as required.
Obviously, no essential functionality should be kept in the ``tui`` module because it won't be used
when Lychee is operating on behalf of a GUI application like Frescobaldi or nCoda.
