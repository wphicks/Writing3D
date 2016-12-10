#!/usr/bin/env blender
# Copyright (C) 2016 William Hicks
#
# This file is part of Writing3D.
#
# Writing3D is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

"""An example showcasing a basic W3DObject with a link


To run this script, use the following command::

    $ python3 link_sample.py
"""

import sys
from pyw3d import project, objects, placement, actions, export_to_blender, psys

# First, create a W3DProject to hold everything else you'll create
my_project = project.W3DProject(
    allow_movement=True)

# Next, let's create a simple text object that will specify the source region
# for emitted particles
source_object = objects.W3DObject(
    name="source",  # Give it a name
    placement=placement.W3DPlacement(),
    content=objects.W3DText(  # Specify that this is a text object
        text="W"  # ...in the shape of a W.
    ),
    visible=False  # This object needn't be visible.
)
# Now add this object to the project
my_project["objects"].append(source_object)

# Next, we do the same for the particle object, which determines the appearance
# of emitted particles
part_object = objects.W3DObject(
    name="particle",
    placement=placement.W3DPlacement(),
    content=objects.W3DText(text="3D"),
)
my_project["objects"].append(part_object)

psys = psys.W3DPSys(
    name="system",
    source_name=source_object["name"],
    particle_name=part_object["name"]
)
my_project["particle_systems"].append(psys)

# Finally, we render the whole thing using Blender, export it, and display the
# result
export_to_blender(my_project, filename="psys_sample.blend", display=True)
