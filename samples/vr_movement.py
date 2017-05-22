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
from pyw3d import project, objects, placement, export_to_blender, timeline, \
    actions, convert_to_blender_axes

# First, create a W3DProject to hold everything else you'll create
my_project = project.W3DProject(
    call_directory=os.path.dirname(__file__),
    allow_movement=True)

relative_actions = []
absolute_actions = []

ordered_names = ["floor", "left", "front", "right"]

placements_dic = {
    "floor": placement.W3DPlacement(
        position=convert_to_blender_axes((0, 0, 4)),
        relative_to="FloorWall"
    ),
    "left": placement.W3DPlacement(
        position=convert_to_blender_axes((0, 4, 0)),
        relative_to="LeftWall"
    ),
    "right": placement.W3DPlacement(
        position=convert_to_blender_axes((0, 4, 0)),
        relative_to="RightWall"
    ),
    "front": placement.W3DPlacement(
        position=convert_to_blender_axes((0, 4, 0)),
        relative_to="FrontWall"
    ),
}

for name, positioning in placements_dic.items():

    my_object = objects.W3DObject(
        name=name,
        color=(200, 0, 180),
        placement=positioning,
        scale=0.5,
        content=objects.W3DText(
            text=name.upper()
        ),
    )

    my_project["objects"].append(my_object)


absolute_actions = [
    (
        1, actions.MoveVRAction(
            placement=placement.W3DPlacement(
                position=(0, 0, 1.5),
                rotation=placement.W3DRotation(
                    rotation_mode="LookAt",
                    rotation_vector=(4, 0, 1.5),
                ),
            ),
            duration=5
        )
    ),
    (
        6, actions.TimelineAction(
            timeline_name="relative",
            change="Start"
        )
    )
]

relative_actions = [
    (
        1, actions.MoveVRAction(
            placement=placement.W3DPlacement(
                position=(0, 5, 0)
            ),
            move_relative=True,
            duration=5,
        )
    ),
    (
        6, actions.TimelineAction(
            timeline_name="absolute",
            change="Start"
        )
    )
]


absolute_timeline = timeline.W3DTimeline(
    name="absolute",
    start_immediately=True,
    actions=absolute_actions
)
my_project["timelines"].append(absolute_timeline)

relative_timeline = timeline.W3DTimeline(
    name="relative",
    start_immediately=False,
    actions=relative_actions
)
my_project["timelines"].append(relative_timeline)

my_project["debug"] = True
# Now, we export the project to archival XML (e.g. for use in legacy cwapp
# environment)
my_project.save_XML("vr_movement.xml")

# Finally, we render the whole thing using Blender, export it, and display the
# result
export_to_blender(
    my_project, filename="vr_movement.blend", display=True,
    fullscreen=False
)
