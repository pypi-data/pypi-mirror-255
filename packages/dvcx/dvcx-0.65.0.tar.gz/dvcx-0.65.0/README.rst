DQL
===

|PyPI| |Status| |Python Version| |License|

|Tests| |Codecov| |pre-commit| |Black|

.. |PyPI| image:: https://img.shields.io/pypi/v/dql.svg
   :target: https://pypi.org/project/dvcx/
   :alt: PyPI
.. |Status| image:: https://img.shields.io/pypi/status/dql.svg
   :target: https://pypi.org/project/dql/
   :alt: Status
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/dql
   :target: https://pypi.org/project/dql
   :alt: Python Version
.. |License| image:: https://img.shields.io/pypi/l/dql
   :target: https://opensource.org/licenses/Apache-2.0
   :alt: License
.. |Tests| image:: https://github.com/iterative/dql/workflows/Tests/badge.svg
   :target: https://github.com/iterative/dql/actions?workflow=Tests
   :alt: Tests
.. |Codecov| image:: https://codecov.io/gh/iterative/dql/branch/main/graph/badge.svg
   :target: https://app.codecov.io/gh/iterative/dql
   :alt: Codecov
.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit
.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Black


Features
--------

* TODO


Requirements
------------

* TODO


Installation
------------

You can install *DQL* via pip_ from PyPI_:

.. code:: console

   $ pip install dvcx


Usage
-----
DQL can be used as a CLI (from system terminal), or as a Python library.

TODO: CLI usage

To use it from Python code, import class ``dql.catalog.Catalog``, which provides methods for all the same commands above, like ``ls()``, ``get()``, ``find()``, ``du()`` and ``index()``.

.. code:: py

    from dql.catalog import Catalog
    catalog = Catalog()
    catalog.ls(["s3://ldb-public/remote/data-lakes/dogs-and-cats/"], update=True)


Contributing
------------

Contributions are very welcome.
To learn more, see the `Contributor Guide`_.


License
-------

Distributed under the terms of the `Apache 2.0 license`_,
*DQL* is free and open source software.


Issues
------

If you encounter any problems,
please `file an issue`_ along with a detailed description.


.. _Apache 2.0 license: https://opensource.org/licenses/Apache-2.0
.. _PyPI: https://pypi.org/
.. _file an issue: https://github.com/iterative/dql/issues
.. _pip: https://pip.pypa.io/
.. github-only
.. _Contributor Guide: CONTRIBUTING.rst
