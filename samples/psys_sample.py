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

from pyw3d import project, objects, placement, export_to_blender,\
    psys, groups

# First, create a W3DProject to hold everything else you'll create
my_project = project.W3DProject(
    allow_movement=True)

# Next, let's create two simple text objects that will be emitted by our system
particles = []
for index, char in enumerate(["W", "3", "D"]):
    particles.append(
        objects.W3DObject(
            name="part{}".format(index),  # Give it a name
            placement=placement.W3DPlacement(),
            content=objects.W3DText(  # Specify that this is a text object
                text=char
            ),
            visible=True  # This object needn't be visible.
        )
    )
# Now add these objects to the project
my_project["objects"].extend(particles)

# and make them a group.
my_project["groups"].append(
    groups.W3DGroup(
        name="particles",
        objects=[obj["name"] for obj in particles]
    )
)

# Next, we describe the actions that will describe the system
my_project["particle_actions"].append(
    psys.W3DPAction(
        name="my_actions",
        source_domain=psys.W3DPDomain(
            type="Line",
            p1=(-1, -1, 0),
            p2=(1, -1, 0)
        ),
        velocity_domain=psys.W3DPDomain(
            type="Point",
            point=(0, 0, -1)
        )
    )
)

# Next, we create the particle system itself

my_project["objects"].append(
    objects.W3DObject(
        name="system",
        placement=placement.W3DPlacement(),
        content=objects.W3DPSys(
            particle_group="particles",
            max_particles=100,
            max_age=3,
            speed=1,
            particle_actions="my_actions"
        ),
        visible=True
    )
)

my_project["debug"] = True


# Finally, we render the whole thing using Blender, export it, and display the
# result
export_to_blender(my_project, filename="psys_sample.blend", display=True)
