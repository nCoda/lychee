Lychee
======

*Lychee* is an MEI document manager.

License
-------

*Lychee* is copyrighted according to the terms of the GNU GPLv3+. A copy of the license is held in
the file called "LICENSE."

Install for Development (CPython 3)
-----------------------------------

Clone this git repository:

    $ git clone https://jameson.adjectivenoun.ca:lychee/lychee.git

Create and activate a new virtualenv:

    $ pyvenv */your/path/here*
    $ source */your/path/here/bin/activate*

Install the development requirements:

    $ pip install -r cra_pip_freeze-py3.txt

Install *Lychee* itself. This ensure the *Lychee* module is importable in the interpreter.

    $ pip install -e .

The test suite uses the ``pytest`` package. To run the test suite, ensure your venv is activated,
then issue the following command from the "abbott" root directory:

    $ py.test

Install for Development (CPython 2)
-----------------------------------

Same as for CPython 3, but use the ``virtualenv`` command to create a virtualenv. You may need to
install that package separately.

Install for Deployment
----------------------

Don't.
