.. _faq:

Frequently Asked Questions
==========================

1. Why doesn't Writing3D support Python2?
-----------------------------------------
Writing3D is based on Blender, which currently uses Python3 as its scripting
language.

2. Will Writing3D output projects to Unity?
-------------------------------------------
No, Writing3D is currently based on Blender, but it would not be *too* difficult
(given the modular structure of Writing3D) to swap out Blender with any other
3D rendering and game platform. If you'd like to see Writing3D support other
backends besides Blender, take a look at the :ref:`getting_involved` page or
:ref:`developer_guide`. We have not looked into the licensing issues involved
with supporting Unity, either, but we'd be happy to talk through them with you
if you're interested.

3. Why does w3d_writer use Tkinter?
-----------------------------------
Primarily to limit the number of dependencies and ensure maintainability.
Python ships with Tkinter by default and Mac and Windows, and is likely to do
so for the foreseeable future. As such, we can limit the number of potential
"points of failure" for future maintainability by using Tkinter as opposed to
the awesome new GUI package du jour. That being said, Tkinter has some serious
limitations, and we're looking to move to something else in the near future,
possibly Qt. No matter what we use, though, we'll want it to be something that
is likely to be in common usage for the foreseeable future.

4. Why does w3d_writer (the GUI) suck so much?
----------------------------------------------
Cause it's not done! Don't worry, we'll be getting it up and running as soon as
possible, and it will hopefully suck less once it's complete. Check out
:ref:`Development Status <development_status>` for more details.

5. Why is Writing3D based on Blender?
-------------------------------------
Blender is just about the best open source 3D rendering and game engine out
there. We think it's very important that artists and students have access to
open source tools for working in VR so that they have full control of their
creative work. Furthermore, while we have nothing against the proprietary
alternatives out there, we think it's important that awesome open source tools
like Blender not be crowded out of the VR scene by their proprietary
competitors.

6. Can you implement feature X in Writing3D for me?
---------------------------------------------------
Maybe! If it sounds like an idea that other people would be interested in, we'd
love to have a crack at it. `Submit an issue
<https://help.github.com/articles/creating-an-issue/>`_ marked as a "feature
request" on `Github <https://github.com/wphicks/Writing3D/issues>`_, and we'll
take a look. Alternatively, if you have some coding experience, consider
implementing it yourself and then contributing your awesome new feature to the
project by `submitting a pull request
<https://help.github.com/articles/using-pull-requests/>`_.

7. Does Writing3D work on Oculus/ Vive/ Playstation VR/ Gear/ etc.?
-------------------------------------------------------------------
Possibly. Through the efforts of the amazing `BlenderVR
<https://blendervr.limsi.fr/doku.php>`_ team, Blender projects can run on a
fairly wide range of hardware, and we are working to make Writing3D work on
even more platforms (including Google Cardboard in the near future). We are
also working to reduce the overhead of targeting available platforms to a
single function call (pyw3d) or button press (w3d_writer), but this is still a
work in progress.

If you are part of an academic institution hoping to run Writing3D on a Cave or
similar environment and would like assistance, please reach out to `the
maintainer <https://twitter.com/intent/tweet?screen_name=whimsicalilk>`_.

8. How can I help with Writing3D?
---------------------------------
Check out the :ref:`getting_involved` page!

9. How can I get your attention?
--------------------------------
The best way is to either submit a Github issue or `Tweet
<https://twitter.com/intent/tweet?screen_name=whimsicalilk>`_ at William Hicks,
the maintainer for the Writing3D project.

10. Why doesn't Writing3D use a more sophisticated XML module?
--------------------------------------------------------------
Again, the goal is to limit dependencies in order to ensure maintainability and
accessibility, but we're not religious about that. If it becomes clear that the
benefits of one of the many great xml libraries out there outweighs the
downsides, we'll happily make the switch. For now, the standard library xml
module seems to be serving our needs fairly well, though.

11. The Blender Game Engine is about to radically change. What will you do?
---------------------------------------------------------------------------
Change with it! We're aware of the changes coming down the line, and while we
may not update the moment the new BGE drops, we're prepared to make things work
soon.

.. toctree::
   :maxdepth: 2
