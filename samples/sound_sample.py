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


from pyw3d import project, objects, placement, actions, export_to_blender,\
    sounds

# First, create a W3DProject to hold everything else you'll create
my_project = project.W3DProject(
    allow_movement=True, debug=True)

# Next, make the test sound available in Writing3D
my_sound = sounds.W3DSound(
    name="test",
    filename="Front_Center.wav"
)

# Next, let's create a simple text object
my_object = objects.W3DObject(
    name="hello",  # Give it a name
    placement=placement.W3DPlacement(  # Specify position and orientation
        position=(0, 1, 0),  # We'll leave rotation as default for now
    ),
    content=objects.W3DText(  # Specify that this is a text object
        text="Play Sound!"  # ...with text reading "Play Sound!"
    ),
    link=objects.W3DLink(  # Add a clickable link to the text object
        actions={
            -1: [  # On every click (negative number)...
                actions.SoundAction(  # Affect the sound...
                    sound_name="test",  # named "test"...
                    change="Start"  # by starting it.
                )
            ]
        }
    )
)

# Now add this object to the project
my_project["objects"].append(my_object)
my_project["sounds"].append(my_sound)

# Finally, we render the whole thing using Blender, export it, and display the
# result
export_to_blender(my_project, filename="sound_sample.blend", display=True)
