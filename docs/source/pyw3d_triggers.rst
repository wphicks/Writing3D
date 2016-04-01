.. _pyw3d_docs_triggers:

Event Triggers
==============

To enhance the interactivity of a VR experience, it is useful to use event
triggers. These allow you to trigger :ref:`W3DActions <pyw3d_docs_actions>`
when particular events take place in virtual space. For instance, you might
make an object appear only when the user is standing in particular spot in 3D
space or make an object move around whenever the user tries to look directly at
it.

TODO: Sample

.. autoclass:: pyw3d.W3DTrigger
    :members:
    :show-inheritance:

.. autoclass:: pyw3d.HeadTrackTrigger
    :members:
    :show-inheritance:

.. autoclass:: pyw3d.HeadPositionTrigger
    :members:
    :show-inheritance:

.. autoclass:: pyw3d.LookAtPoint
    :members:
    :show-inheritance:

.. autoclass:: pyw3d.LookAtDirection
    :members:
    :show-inheritance:

.. autoclass:: pyw3d.LookAtObject
    :members:
    :show-inheritance:

.. autoclass:: pyw3d.MovementTrigger
    :members:
    :show-inheritance:

.. autoclass:: pyw3d.EventBox
    :members:
    :show-inheritance:

.. toctree::
   :maxdepth: 2
