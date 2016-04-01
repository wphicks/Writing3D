.. _pyw3d_docs_objects:

Objects in Space
================
All objects in W3D projects are created using the W3DObject class. You should
think of W3DObjects as containers for whatever content you're trying to add to
virtual space. To be more specific, if you want to put an image in space, you
create a W3DObject to specify a name, a position, and a few other basic things,
and then specify that the W3DObject contains "my_awesome_selfie.jpg" or
whatever image you want. If you later decide that selfies are lame, and you'd
rather just put your name in giant block letters at the same point in space,
you can swap out "my_awesome_selfie.jpg" for a :class:`pyw3d.W3DText` object. See
:ref:`W3DContent <pyw3d_docs_object_content>` for more details on this.

You can also interact with W3DObjects by adding a :ref:`W3DLink
<pyw3d_docs_links>` to them.

.. autoclass:: pyw3d.W3DObject
    :members:
    :show-inheritance:

TODO: Sample

.. _pyw3d_docs_object_content:

Content of Objects
------------------
The W3DObject class is used to specify the name, position, and other attributes
common to any object you might add to a Writing3D project. The W3DContent class
(and its subclasses) tells you what "kind of thing" that object is: text,
image, model, lighting, etc.

.. autoclass:: pyw3d.W3DContent
    :members:
    :show-inheritance:

.. autoclass:: pyw3d.W3DText
    :members:
    :show-inheritance:

.. autoclass:: pyw3d.W3DImage
    :members:
    :show-inheritance:

.. autoclass:: pyw3d.W3DStereoImage
    :members:
    :show-inheritance:

.. warning:: Stereo images are not yet fully implemented

.. autoclass:: pyw3d.W3DModel
    :members:
    :show-inheritance:

.. autoclass:: pyw3d.W3DLight
    :members:
    :show-inheritance:

.. autoclass:: pyw3d.W3DPSys
    :members:
    :show-inheritance:

.. warning:: Particle systems are not yet fully implemented

.. _pyw3d_docs_links:

Object Links
------------
In order to interact with an object, you may add a clickable link to it. This
link is implemented using the W3DLink class and may trigger a series of
:ref:`W3DActions <pyw3d_docs_actions>`.

.. autoclass:: pyw3d.W3DLink

.. toctree::
   :maxdepth: 2
