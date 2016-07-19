.. _getting_started:

Getting Started
===============

Installing Python3
------------------

Regardless of how you intend to use or install Writing3D, you *must* install
Python3 first. Basic instructions are available here, and you can visit the
`official Python documentation <https://www.python.org/about/gettingstarted/>`_
if you have any trouble.

For Windows
^^^^^^^^^^^
If you are on a 64-bit Windows computer, download and run the MSI installer
from `here <https://www.python.org/ftp/python/3.4.4/python-3.4.4.amd64.msi>`_.
If you are on a 32-bit Windows computer, download and run the MSI installer
from `here <https://www.python.org/ftp/python/3.4.4/python-3.4.4.msi>`_.

For Mac OS X
^^^^^^^^^^^^
Download and run the installer for Mac `here
<https://www.python.org/ftp/python/3.4.4/python-3.4.4-macosx10.6.pkg>`_.

For Debian-based Linux systems (including Ubuntu and Mint)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Run the following from terminal:

.. code:: bash

    $ sudo apt-get install python3 python3-tk

For other Linux systems
^^^^^^^^^^^^^^^^^^^^^^^

Either check your distribution's documentation for how to install Python3
via your package manager or run the following from terminal:

.. code:: bash

    $ wget https://www.python.org/ftp/python/3.4.3/Python-3.4.3.tar.xz
    $ tar xf Python-3.*
    $ cd Python-3.*
    $ ./configure
    $ make; make altinstall

TODO: Add tkinter installation instructions

Downloading Writing3D
---------------------
As a zip file
^^^^^^^^^^^^^
You can download the latest version of Writing3D as a zip file `here
<https://github.com/wphicks/Writing3D/archive/master.zip>`_. Then, `extract
<http://www.wikihow.com/Extract-Files>`_ the zip archive to any convenient
directory on your system.

Using Git
^^^^^^^^^
If you know how to use git, you can also just clone the Writing3D repository,
which will allow you to stay up to date with new versions and features more
easily:

.. code:: bash

    $ git clone https://github.com/wphicks/Writing3D.git

Installing Writing3D
--------------------

Using the GUI installation script
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Once you've installed Python3, you can use the included GUI install script
(install_w3d.py) to install everything you need for Writing3D.

On Windows
^^^^^^^^^^
Windows automatically associates .py files with the Python launcher, so you
should be able to just double-click on install_w3d.py to begin the
install process. Follow the prompts, and the installer will walk you through
the process.

On Mac
^^^^^^
After installing Python3, you should have an application called PythonLauncher
in /Applications/MacPython 3.5/. Drag and drop install_w3d.py onto
PythonLauncher, and then follow the prompts. More details are available `here
<https://docs.python.org/3.5/using/mac.html#how-to-run-a-python-script>`_.

TODO: This seems to occasionally point to the wrong Python version. Advice from
a Mac user would be appreciated.

On Linux
^^^^^^^^
Depending on your desktop environment, you may be able to just double-click on
install_w3d.py to run it. If not, open a terminal, cd to the directory
containing install_w3d.py and then run:

.. code:: bash

    $ python3 install_w3d.py

Manual installation
^^^^^^^^^^^^^^^^^^^
To install manually from terminal, just execute the following:

        $ python3 setup.py install --user

This will install Blender, and you should now have access to the :ref:`pyw3d
module <pyw3d_docs>` from Python3.

.. warning::

    Due to a bug in the Homebrew configuration of Python, Homebrew users should
    instead run

        $ python3 setup.py install --user --prefix=

    This will prevent the system-level distutils.cfg file from conflicting with
    the --user flag.

Using w3d_writer: The Writing3D GUI
-----------------------------------
Unfortunately, w3d_writer is not yet ready for primetime. Check back soon for
updates.

In the meantime, you might be interested in CWEditor, the legacy Java-based
frontend that was once used in the Brown University CaveWriting program to
create VR projects. It outputs to the same XML archival format as Writing3D, so
it should interoperate smoothly with the Writing3D backend. You may download
this legacy software from `here for Mac and Linux
<https://drive.google.com/file/d/0By7izea0dXGyYUgwZVNReUhfOXM/edit?usp=sharing>`_
and `here for Windows
<https://drive.google.com/file/d/0By7izea0dXGyekFCVFUzZVdCa28/edit?usp=sharing>`_.

Once you have downloaded the indicated zip file, extract CWEditor.jar **and
only CWEditor.jar** to some convenient location on your system. Do *not*
extract the other files, or if you do, just copy CWEditor.jar to another
directory. Next double-click on CWEditor.jar (on most systems) to run it with
the Jave JRE.

Within the editor, go to the "Run" menu and select "Configure paths." In the
resulting dialog, navigate to cwapp.py in the Writing3D samples folder. The
editor should now be able to use Writing3D to preview VR projects. See
documentation within cwapp.py for additional help and caveats.

Module Documentation
^^^^^^^^^^^^^^^^^^^^
TODO: Create and link w3dui documentation

Using pyw3d: The Python Library
-------------------------------
Now that you have Writing3D installed, the best way to get started is to check
out some of the examples in the samples directory. These are all carefully
documented with instructions on how to make them run. We suggest that you start
with link_sample.py, shown here:

.. literalinclude:: ../../samples/link_sample.py
    :language: python
    :linenos:

TODO: Example with export to Oculus and Brown University Cave

Module Documentation
^^^^^^^^^^^^^^^^^^^^
Complete documentation of all classes, methods, functions, etc. of the pyw3d
module is available :ref:`here <pyw3d_docs>`.

.. toctree::
   :maxdepth: 2

        pyw3d Documentation <pyw3d.rst>
