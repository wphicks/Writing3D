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

"""An example showcasing sound in Writing3D


To run this script, use the following command::

    $ python3 sound_sample.py
"""


import os
from pyw3d import project, objects, placement, actions, export_to_blender,\
    sounds

# First, create a W3DProject to hold everything else you'll create
my_project = project.W3DProject(
    allow_movement=True, debug=True)

# Next, make the test sounds available in Writing3D
play_sound = sounds.W3DSound(
    name="basic",
    filename="sound/play.wav"
)
left_sound = sounds.W3DSound(
    name="left",
    filename="sound/left.wav",
    movement_mode="Positional"  # Positional for 3D audio
)
right_sound = sounds.W3DSound(
    name="right",
    filename="sound/right.wav",
    movement_mode="Positional"
)
long_sound = sounds.W3DSound(
    name="long",
    filename="sound/long.wav"
)

# Next, let's create link to play a basic sound
play_object = objects.W3DObject(
    name="play",
    placement=placement.W3DPlacement(
        position=(0, 10, 0),
    ),
    content=objects.W3DText(
        text="Play Sound!"
    ),
    link=objects.W3DLink(
        actions={
            -1: [  # On every click (negative number)...
                actions.SoundAction(  # Affect the sound...
                    sound_name="basic",  # named "basic"...
                    change="Start"  # by starting it.
                )
            ]
        }
    )
)

# An object to play a sound to the left
play_object = objects.W3DObject(
    name="left",
    placement=placement.W3DPlacement(
        position=(-10, 0, 0),
        rotation=placement.W3DRotation(
            rotation_mode = "LookAt",
            rotation_vector = (0, 0, 0)
        )
    ),
    content=objects.W3DText(
        text="Left"
    ),
    sound="left",  # Attach the sound named left to this object
    link=objects.W3DLink(
        actions={
            -1: [
                actions.ObjectAction(  # Affect the object...
                    object_name="left",  # named "left"...
                    sound_change="Play Sound"  # by starting its sound file.
                )
            ]
        }
    )
)

# Now add this object to the project
my_project["objects"].append(play_object)
my_project["sounds"].append(play_sound)
my_project["sounds"].append(left_sound)
my_project["sounds"].append(right_sound)
my_project["sounds"].append(long_sound)

# Finally, we render the whole thing using Blender, export it, and display the
# result
export_to_blender(my_project, filename="sound_sample.blend", display=True)
