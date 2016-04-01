.. _pyw3d_docs:

pyw3d: The Python VR Library
============================

.. automodule:: pyw3d

pyw3d Classes
-------------

The backbone of pyw3d is the W3DFeature class. It is a container class for
storing data related to an element of a Writing3D project. All W3DFeature
subclasses should implement the fromXML classmethod and toXML method, which
create a class instance from the archival XML record or record necessary class
data to an XML tree respectively. W3DFeature is itself a subclass of a Python
dictionary, and keys are restricted to those which appear in the
argument_validator class variable.

The argument_validator dictionary itself maps allowable keys to callable
validators for data stored within a W3DFeature instance. Attempting to store an
invalid value in a W3DFeature will raise an InvalidArgument exception.  Any
valid key can also be used as a keyword argument when initializing a W3DFeature
object.

W3DFeature subclasses can also specify a default_arguments dictionary which
provides default values for given keys if they have not been set.

.. autoclass:: W3DFeature
    :members:
    :undoc-members:
    :show-inheritance:

pyw3d Objects
-------------
The W3DObject class allows you to add objects to virtual space in a W3D
Project. Take a look at :ref:`pyw3d Objects <pyw3d_docs_objects>` for full
details.

pyw3d Groups
------------
The W3DGroup class allows you to more easily reference groups of W3DObjects:

.. autoclass:: pyw3d.W3DGroup
    :members:
    :show-inheritance:

pyw3d Sounds
------------
The W3DSound class has not yet been fully implemented. See :ref:`Development
Status <development_status>` for more details.

.. autoclass:: pyw3d.W3DSound
    :members:
    :show-inheritance:

pyw3d Actions
-------------
The W3DAction class allows you to specify interactive changes in virtual space
(like moving an object or playing a sound). Take a look at :ref:`pyw3d Actions
<pyw3d_docs_actions>` for full details.

pyw3d Timelines
---------------
The W3DTimeline class allows you to group :ref:`pyw3d Actions
<pyw3d_docs_actions>` into timelines of successive actions. These timelines can
either run automatically when your project starts or be triggered by some other
event. See :ref:`pyw3d Timelines <pyw3d_docs_timelines>` for details.

pyw3d Event Triggers
--------------------
The W3DTrigger class allows you to trigger :ref:`pyw3d Actions
<pyw3d_docs_actions>` when certain events occur within virtual space (such as a
user looking in a particular direction). See :ref:`pyw3d Triggers
<pyw3d_docs_triggers>` for details.

Errors
------
pyw3d defines a number of custom exceptions in the pyw3d.errors module, as
documented here:

.. automodule:: pyw3d.errors

.. autoclass:: pyw3d.errors.BadW3DXML
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pyw3d.errors.InvalidArgument
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pyw3d.errors.ConsistencyError
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pyw3d.errors.EBKAC
    :members:
    :undoc-members:
    :show-inheritance:

Complete Reference
------------------
For complete details on all classes, functions, and variables in the pyw3d
module, take a look at the :ref:`modindex`.

.. toctree::
   :maxdepth: 2
