========
Meet Bob
========

.. image:: https://github.com/renemoll/bob/actions/workflows/unit-testing.yaml/badge.svg
   :target: https://github.com/renemoll/bob/actions/workflows/unit-testing.yaml
   :alt: Unit tests
.. image:: https://coveralls.io/repos/github/renemoll/bob/badge.svg?branch=main
   :target: https://coveralls.io/github/renemoll/bob?branch=main
   :alt: Test coverage
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Coding style
.. image:: https://img.shields.io/github/license/renemoll/bob
   :target: https://github.com/renemoll/bob/blob/main/LICENSE
   :alt: GitHub

Bob is my collection of build tools. The goal is to provide a simple interface
to build and test projects without having to remember or lookup various commands.

For now, this project limits itself to C/C++ projects.

How to use
==========

.. code-block:: bash

  bob build

Other commands available are:
* `bootstrap`: gather dependencies and toolchain(s)
* `configure`: configure a build system.
* `install`: install the package.

Requirements
============

 * Python 3.8+
 * git

Development
===========

1. Setup a virtual environment and activate it:

.. code-block:: bash

   python3 -m venv .env_dev
   . .env_dev/bin/activate

2. Install locally:

.. code-block:: bash

   pip install --editable .[dev]

3. Test:

.. code-block:: bash

   pytest


Run the complete test-suite
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Setup a virtual environment and activate it:

.. code-block:: bash

   python -m venv .env_tox
   . .env_tox/bin/activate

2. Install locally:

.. code-block:: bash

   pip install --editable .[tox]

3. Test:

.. code-block:: bash

   tox

Configured tools
~~~~~~~~~~~~~~~~

1. ``black`` for code formatting.
2. ``ruff`` for linting.
3. ``pylint`` for linting.
4. ``mypy`` for static type checking.
