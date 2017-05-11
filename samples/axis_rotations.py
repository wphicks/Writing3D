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

"""An example showcasing scripted creation of objects


To run this script, use the following command:
blender --background --python link_sample.py

where blender is your blender executable.
"""

import os
from math import pi, sin, cos, degrees
from pyw3d import project, objects, placement, export_to_blender, timeline, \
    actions

# First, create a W3DProject to hold everything else you'll create
my_project = project.W3DProject(
    call_directory=os.path.dirname(__file__),
    allow_movement=True)

theta_div = 8
radius = 10
relative_actions = []
absolute_actions = []
all_angles = [2 * pi / theta_div * i for i in range(theta_div)]
for i in range(0, theta_div):

    theta = all_angles[i]

    object_name = "elem_x_{}".format(i)

    my_object = objects.W3DObject(
        name=object_name,
        color=(int(i / theta_div * 255), 100, 0),
        placement=placement.W3DPlacement(
            position=(
                0,
                radius * sin(theta),
                radius * cos(theta)
            ),
            rotation=placement.W3DRotation(
                rotation_mode="Axis",
                rotation_vector=(1, 0, 0),
                rotation_angle=degrees(-theta + pi / 2)
            )
        ),
        content=objects.W3DText(
            text="{}".format(int(180 / pi * theta))
        ),
    )

    absolute_actions.extend(
        [
            (
                1 + 2 * j, actions.ObjectAction(
                    object_name=object_name,
                    placement=placement.W3DPlacement(
                        position=(
                            0,
                            radius * sin(
                                all_angles[(i + j + 1) % theta_div]),
                            radius * cos(
                                all_angles[(i + j + 1) % theta_div]),
                        ),
                        rotation=placement.W3DRotation(
                            rotation_mode="Axis",
                            rotation_vector=(1, 0, 0),
                            rotation_angle=degrees(
                                -all_angles[
                                    (i + j + 1) % theta_div] + pi / 2
                            )
                        ),
                    ),
                    duration=1
                )
            ) for j in range(theta_div)
        ]
    )

    relative_actions.extend(
        [
            (
                2 * i, actions.ObjectAction(
                    object_name=object_name,
                    move_relative=True,
                    placement=placement.W3DPlacement(
                        rotation=placement.W3DRotation(
                            rotation_mode="Axis",
                            rotation_vector=(1, 0, 0),
                            rotation_angle=int(360 / theta_div)
                        ),
                    ),
                    duration=1
                )
            ) for i in range(theta_div)
        ]
    )

    my_project["objects"].append(my_object)

absolute_actions.append(
    (
        2 * (theta_div + 1), actions.TimelineAction(
            timeline_name="relative",
            change="Start"
        )
    )
)

absolute_timeline = timeline.W3DTimeline(
    name="absolute",
    start_immediately=True,
    actions=absolute_actions
)
my_project["timelines"].append(absolute_timeline)

relative_actions.append(
    (
        2 * theta_div, actions.TimelineAction(
            timeline_name="absolute",
            change="Start"
        )
    )
)

relative_timeline = timeline.W3DTimeline(
    name="relative",
    start_immediately=False,
    actions=relative_actions
)
my_project["timelines"].append(relative_timeline)
# Now, we export the project to archival XML (e.g. for use in legacy cwapp
# environment)
my_project.save_XML("axis_rotations.xml")

# Finally, we render the whole thing using Blender, export it, and display the
# result
export_to_blender(
    my_project, filename="axis_rotations.blend", display=True, fullscreen=True)
