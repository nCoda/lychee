.. _workflow:

Workflow and Action Management
==============================

Program Modules
---------------

The :mod:`lychee.workflow` module itself is empty. These submodules manage user sessions and run
workflows.

.. toctree::
    :maxdepth: 2

    workflow-registrar
    workflow-session
    workflow-steps


Signals and Slots
-----------------

.. danger::
    The signals are intended for use by external applications, however their use in *Lychee* will
    change significantly in the near future---all of the existing signals should be considered
    deprecated.

    At this time, we recommend against incorporating *Lychee* in external programs. Please follow
    task `T113 <https://goldman.ncodamusic.org/T113>`_ for information on our progress in
    redesigning this important aspect of *Lychee*, including our predicted milestone for completion.

*Lychee* uses the :mod:`signalslot` library (`link <https://signalslot.readthedocs.org/>`_).

In the future, the :ref:`workflow-session` infrastructure will provide the primary means of getting
data into *Lychee*. Signals will be used to send data back to a user interface.


Signal Definitions
------------------

.. automodule:: lychee.signals
    :members: ACTION_START


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
