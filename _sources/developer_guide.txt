.. _developer_guide:

Developer's Guide
=================

.. warning::
    This is *very much* still a work in progress, but please don't let that
    keep you from contributing. The maintainer is happy to sort out any style
    issues or workflow problems that are not addressed by this guide.

Style Guide
-----------
Writing3D code should be `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_
compliant. This ensures both maintainability and extensibility (through
readability), two of the major goals of this project. It should also contain
docstrings for `Sphinx <http://www.sphinx-doc.org/en/stable/index.html>`_-style
`autodocing <https://pythonhosted.org/an_example_pypi_project/sphinx.html>`_.
If you are absolutely unable to follow PEP 8 or document your code, you can
submit a pull request anyway, but it may be some time before the maintainer can
revise your code and integrate it into the main codebase.

Features which introduce new Writing3D functionality should in general inherit
from the W3DFeature class and *must* implement fromXML and toXML methods for
creating an archival XML format.

TODO: Describe W3DFeature structure in detail

Git Workflow
------------
Writing3D uses a `fork & pull model
<https://stackoverflow.com/questions/11582995/what-is-the-fork-pull-model-in-github>`_
for contributions. In general, you should make changes off of the develop
branch, and they will eventually be pulled into master in the main repo.

TODO: Give more detail on workflow

.. toctree::
   :maxdepth: 2
