.. _readme:

Writing3D
=========
Writing3D is a set of tools designed to lower the barrier-of-entry (and speed
up development time) for producing VR games, literature, and artwork. Click
`here <https://wphicks.github.io/Writing3D/>`_ to view the complete
documentation website.

Quickstart Guide
----------------
The easiest way to get started with Writing3D is to download a zipfile install
from one of the following locations:

* `Linux <https://drive.google.com/open?id=0B-L9I5ef3FLWV3lDdU1McDRRRkU>`_
* `Windows <https://drive.google.com/open?id=0B-L9I5ef3FLWd1luR1N0MHlVMjQ>`_
* `Mac <https://drive.google.com/open?id=0B-L9I5ef3FLWRGttR1U2WmFBaE0>`_

Note that this includes the old (non-FOSS, Java-based) cwapp editor and a copy
of the appropriate version of Blender. You can then launch CWEditor.jar to
begin creating Writing3D projects.

.. Warning::
    The first time you open CWEditor.jar, you may need to open the Run menu,
    select "Configure Paths" and then simply click "OK" to get CWEditor to
    recognize the Writing3D backend.


Overview
--------
Based on `cwapp <http://cavewriting.sourceforge.net/>`_ and inspired by
projects like `Processing <https://processing.org/>`_ and `Twine
<http://twinery.org/>`_, which help make a range of technologies more
accessible to creative coders, Writing3D aims to provide a highly accessible
point-of-entry for creative work in virtual reality. It is designed with three
major goals in mind:

1. Accessibility
^^^^^^^^^^^^^^^^
The layered design of Writing3D helps make it both useful and accessible for
VR content creators of all technical abilities. Those with limited (or no)
coding experience can still access all of Writing3D's functionality through its
Python-based graphic user interface (GUI), w3d_writer. For those who have more
coding experience or those who have become comfortable with the GUI and want to
create even more sophisticated work, Writing3D provides an easy-to-use Python
module, pyw3d. Finally, since Writing3D interfaces with `Blender
<https://www.blender.org>`_ to render VR projects, users who are experienced
with 3D modeling can directly import their models into the Writing3D framework
to quickly add interactivity and animation.

2. Extensibility
^^^^^^^^^^^^^^^^
Writing3D is open source software
(`GPLv3 <https://www.gnu.org/licenses/gpl-3.0.en.html>`_), which means you are
free to look at and modify its source code. It is also specifically structured
to make it as easy as possible for users to add their own functionality. This
means that Writing3D can continue to improve and gain cool new features as the
community of users grows.

3. Maintainability
^^^^^^^^^^^^^^^^^^
Writing3D not only uses best practices to ensure that it can be maintained far
into the future but also contains features to ensure that projects developed
with this framework will continue to be accessible for the foreseeable future.
Among other things, Writing3D provides a method to save an "archival" copy of
any VR project using a human-readable XML format. This will help ensure that
creative developers have access to a valuable "canon" of VR work even as
VR technologies evolve.

Our commitment to maintaining VR work means that projects from Brown
University's `Cave Writing
<http://www.wired.com/2003/02/writings-on-the-wall-in-3-d-cave/>`_ program
going as far back as 1999 can still run through Writing3D and may soon be
available on new hardware platforms like Google Cardboard and the Oculus Rift.

More Information
----------------
For more information, check out our `FAQ
<https://wphicks.github.io/Writing3D/faq.html>`_ page or dive in with the
`Getting Started
<https://wphicks.github.io/Writing3D/getting_started.html#getting-started>`_
guide.

.. _development_status:

Current Development Status
--------------------------
Writing3D is currently in a pre-alpha stage. It can read and write to its
archival xml format and render most project features. It has not been
extensively tested across platforms and OSes, and some features remain to be
implemented, including:

1. Particle systems
2. Stereo images (images which only appear in one eye of stereo visualizations)
3. Support for OpenAL-based 3D audio
4. Simplified Python interface for adding Writing3D features

The GUI is also currently in an unusable skeletal state. That being said, pyw3d
currently provides almost all features that will eventually make up the core of
Writing3D, and you can begin using it immediately to create basic interactive
VR experiences.

If you are interested in Writing3D and would like to see its core feature set
completed sooner, please see the
`Getting Involved <https://wphicks.github.io/Writing3D/getting_involved.html>`_ page.

Contact
-------
The best ways to contact those involved with the Writing3D project are by
tweeting `@whimsicalilk
<https://twitter.com/intent/tweet?screen_name=whimsicalilk>`_ or by logging an
issue on `Github <https://github.com/wphicks/Writing3D/issues>`_.
