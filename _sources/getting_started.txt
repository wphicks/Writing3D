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
(install_everything.py) to install everything you need for Writing3D.

On Windows
^^^^^^^^^^
Windows automatically associates .py files with the Python launcher, so you
should be able to just double-click on install_everything.py to begin the
install process. Follow the prompts, and the installer will walk you through
the process.

On Mac
^^^^^^
After installing Python3, you should have an application called PythonLauncher
in /Applications/MacPython 3.5/. Drag and drop install_everything.py onto
PythonLauncher, and then follow the prompts. More details are available `here
<https://docs.python.org/3.5/using/mac.html#how-to-run-a-python-script>`_.

On Linux
^^^^^^^^
Depending on your desktop environment, you may be able to just double-click on
install_everything.py to run it. If not, open a terminal, cd to the directory
containing install_everything.py and then run:

.. code:: bash

    $ python3 install_everything.py

Manual installation
^^^^^^^^^^^^^^^^^^^
If you'd like to install everything manually (on a headless machine, for
instance), please do the following after installing Python3:

1. Install Blender by following the instructions provided on the `Blender
   download page <https://www.blender.org/download/>`_.
2. Open the file pyw3d/__init__.py and replace the values in the lines::

        BLENDER_EXEC = "blender"  # BLENDEREXECSUBTAG
        BLENDER_PLAY = "blenderplayer"  # BLENDERPLAYERSUBTAG


    with the paths to your blender and blenderplayer executables respectively.
    Note that this may not be necessary on all systems.
3. Run the following in terminal from the root Writing3D directory::

        $ python3 setup.py install --user

You should now have access to the :ref:`pyw3d module <pyw3d_docs>` from
Python3.

Using w3d_writer: The Writing3D GUI
-----------------------------------
Unfortunately, w3d_writer is not yet ready for primetime. Check back soon for
updates.

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
