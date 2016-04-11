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

"""A copy of the sphere example showcasing single-sided text


To run this script, use the following command::

    $ python3 single_sided_sample.py
"""

import sys
#PATHSUBTAG
from random import randint
from math import pi, sin, cos
from pyw3d import project, objects, placement, export_to_blender

# First, create a W3DProject to hold everything else you'll create
my_project = project.W3DProject(
    allow_movement=True)

theta_div = 10
phi_div = 10
radius = 10
for i in range(1, theta_div):
    for j in range(phi_div):
        theta = pi/theta_div*i
        phi = 2*pi/phi_div*j

        my_object = objects.W3DObject(
            name="elem{}x{}".format(i, j),
            color=(randint(0, 255), randint(0, 255), randint(0, 255)),
            double_sided=False,
            placement=placement.W3DPlacement(
                position=(
                    radius*sin(theta)*cos(phi),
                    radius*sin(theta)*sin(phi),
                    radius*cos(theta)
                ),
                rotation=placement.W3DRotation(
                    rotation_mode="LookAt",
                    rotation_vector=(0, 0, 0)
                )
            ),
            content=objects.W3DText(
                text="W3D"
            ),
        )

        my_project["objects"].append(my_object)

#Now, we export the project to archival XML (e.g. for use in legacy cwapp
#environment)
my_project.save_XML("single_sided_sample.xml")

#Finally, we render the whole thing using Blender, export it, and display the
#result
export_to_blender(
    my_project, filename="single_sided_sample.blend", display=True,
    fullscreen=True)
