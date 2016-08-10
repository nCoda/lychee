.. _document:

MEI Document Representation
===========================

.. note::
    Most external developers will not need to use this module directly.
    We recommend using functionality in :ref:`workflow` whenever possible.

The :class:`Document` class represents a Lychee-MEI document. If version control integration is
enabled, this is managed by the :mod:`lychee.vcs` module.

Guidelines for Using Lychee-MEI Documents
-----------------------------------------

These guidelines help guarantee the integrity of the LMEI document, and avoid duplicating error-prone
code. These are absolute requirements for *Lychee* developers and very strong recommendations for
external *Lychee* users.

#. For every capability the :class:`~lychee.document.document.Document` class offers, no other
   module or class may offer this functionality. This avoids duplicating functionality and thereby
   introducing possible errors. Other modules and classes may "shadow" :class:`Document` methods.
#. No filesystem access can happen outside the :mod:`document` module. The version control system
   is an exception, though it must be used properly (for example, through the :mod:`mercurial-hug`
   module) and in the proper place (:mod:`lychee.vcs`). This helps manage a range of potential
   problems, like XML-related security issues, data races, and so on.
#. Document manipulation at a level higher than a Lychee-MEI ``<section>`` should be performed by
   the :class:`Document` class itself. In a situation of "worst case" corruption, where a Lychee-MEI
   file cannot be loaded from the filesystem, this allows recovering the rest of a document by
   discarding or ignoring the corrupted ``<section>``.
#. Capabilities offered by private functions and methods in the :mod:`document` module may be changed
   to a public function or method if required by another module. Before doing this, carefully
   consider the implications: once a function or method becomes part of the public API, it is very
   difficult to change. Would it be better to add the functionality to the :class:`Document` class?
   Should the function or method be renamed? Does the function or method make sense in the context
   of the other public functions and methods?

*Lychee* developers may be interested in the internal functions and methods, documented here:

.. toctree::
    :maxdepth: 1

    document-internal


Document Module Public Interface
--------------------------------

.. autoclass:: lychee.document.document.Document
    :members:
