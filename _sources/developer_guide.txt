.. _developer_guide:

Developer's Guide
=================

To Begin
--------
1. Begin by `forking <https://help.github.com/articles/fork-a-repo/>`_ the
   `Writing3D repo <https://github.com/wphicks/Writing3D>`_ on Github.

2. Download and install `Blender <https://www.blender.org/download/>`_ on your
   system.

    .. warning::
        Writing3D has only been tested with Blender 2.76. You are welcome to try a
        later version and let us know the results, but only 2.76 is supported at
        the moment.

3. `Clone <https://help.github.com/articles/cloning-a-repository/>`_ your fork
   of the repo to your computer, and `checkout
   <https://git-scm.com/docs/git-checkout>`_ the ``develop`` branch.

5. Create a feature branch to commit your changes to by running the following
   within your local repo:
    .. code-block:: bash
        
        $ git branch my_cool_feature_name

4. Create a `configuration file <https://en.wikipedia.org/wiki/JSON#Example>`_
   in your `home directory
   <https://docs.python.org/3/library/os.path.html#os.path.expanduser>`_ called
   .w3d.json with the following fields:

   * ``Blender executable``: The (absolute) path to your Blender executable.

   * ``Blender player executable``: The (absolute) path to your Blender player
     executable.


You should now be able to `add <https://git-scm.com/docs/git-add>`_ and `commit
<https://git-scm.com/docs/git-commit>`_ changes to your local repo and `push
<https://help.github.com/articles/pushing-to-a-remote/>`_ those changes to your
fork. When you're ready to share those changes with the rest of the Writing3D
community, open a `pull request
<https://help.github.com/articles/about-pull-requests/>`_ against the develop
branch of the Writing3D repo.

Samples
-------
The Writing3D repo includes sample projects written both in archival xml format
and as Python scripts. To test that your install is working properly, try
running at least some of these samples.

Python Samples
^^^^^^^^^^^^^^
To make it easier to run the Python samples, a script called ``w3dpy.sh`` or
``w3dpy.bat`` is included in the scripts directory for your platform. Execute
this script with the Python sample file as argument. Example (for Linux):

.. code-block:: bash
    
    $ cd Writing3D
    $ ./scripts/Linux/w3dpy.sh samples/link_sample.py

XML Samples
^^^^^^^^^^^
To run xml samples, we use ``cwapp.sh`` or ``cwapp.bat`` from the script
directory for your platform. These scripts take two arguments: either
``desktop`` or ``desktopfull`` to run in windowed or fullscreen mode
respectively and the name of the xml file to run. Example (for Linux):

.. code-block:: bash
    
    $ cd Writing3D
    $ ./scripts/Linux/cwapp.sh desktop samples/xml_samples/random_sample.xml


Documentation and Getting Help
------------------------------
pyw3d Documentation
^^^^^^^^^^^^^^^^^^^
Complete documentation of all classes, methods, functions, etc. of the pyw3d
module is available here:

.. toctree::
   :maxdepth: 2

        pyw3d Documentation <pyw3d.rst>

Getting Help
~~~~~~~~~~~~
If you have questions on where to find information about something related to
Writing3D, please feel free to submit a ticket to the `issue tracker
<https://github.com/wphicks/Writing3D/issues>`_ with the first word
"Documentation". That way we can make it easier for the next person to find
what they need. You should also feel free to contact the maintainer directly
via Twitter (`@whimsicalilk
<https://twitter.com/intent/tweet?screen_name=whimsicalilk>`_).

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

.. toctree::
   :maxdepth: 2
