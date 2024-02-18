copier_example
===========================

|code_ci| |docs_ci| |coverage| |pypi_version| |license|

This is where you should write a short paragraph that describes what your module does,
how it does it, and why people should use it.

============== ==============================================================
PyPI           ``pip install copier-example``
Source code    https://github.com/coretl/copier-example
Documentation  https://coretl.github.io/copier-example
Releases       https://github.com/coretl/copier-example/releases
============== ==============================================================

This is a test repo.


This is where you should put some images or code snippets that illustrate
some relevant examples. If it is a library then you might put some
introductory code here:

.. code-block:: python

    from copier_example import __version__

    print(f"Hello copier_example {__version__}")

Or if it is a commandline tool then you might put some example commands here::

    $ python -m copier_example --version

TODO
====

- [x] Use pyright instead of mypy
- [x] Use
- [x] Use GH pages publishing
- [x] Split up CI
- [x] Slim down devcontainer
- [x] Use dev constraints everywhere
- [x] Investigate ruff checks and fixes
- [x] Add pre-commit for dev constraints
- [ ] Get docs from releases and add them too
- [ ] MD-ify docs
- [ ] Run repo review
- [ ] Fix broken docs links
- [ ] Group dependabot alerts
- [ ] Delete favicon
- [ ] Add copier to pyproject

.. |code_ci| image:: https://github.com/coretl/copier-example/actions/workflows/code.yml/badge.svg?branch=main
    :target: https://github.com/coretl/copier-example/actions/workflows/code.yml
    :alt: Code CI

.. |docs_ci| image:: https://github.com/coretl/copier-example/actions/workflows/docs.yml/badge.svg?branch=main
    :target: https://github.com/coretl/copier-example/actions/workflows/docs.yml
    :alt: Docs CI

.. |coverage| image:: https://codecov.io/gh/coretl/copier-example/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/coretl/copier-example
    :alt: Test Coverage

.. |pypi_version| image:: https://img.shields.io/pypi/v/copier-example.svg
    :target: https://pypi.org/project/copier-example
    :alt: Latest PyPI version

.. |license| image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
    :target: https://opensource.org/licenses/Apache-2.0
    :alt: Apache License


..
    Anything below this line is used when viewing README.rst and will be replaced
    when included in index.rst

See https://coretl.github.io/copier-example for more detailed documentation.
