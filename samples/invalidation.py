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

"""An example showcasing sounds triggered by timelines


To run this script, use the following command::

    $ python3 timeline_sound_sample.py
"""
import os
from pyw3d import project, objects, placement, actions, export_to_blender, \
    timeline, sounds

# First, create a W3DProject to hold everything else you'll create
my_project = project.W3DProject(
    call_directory=os.path.dirname(__file__),
    allow_movement=True
)

# Next, make three test sounds available in Writing3D
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
my_project["sounds"].append(play_sound)
my_project["sounds"].append(left_sound)
my_project["sounds"].append(right_sound)

# An object to play a sound to the left
left_object = objects.W3DObject(
    name="left_object",
    placement=placement.W3DPlacement(
        position=(-5, 0, 0),
    ),
    content=objects.W3DText(
        text="Left"
    ),
    sound="left",  # Attach the sound named left to this object
    visible=False
)
# An object to play a sound to the right
right_object = objects.W3DObject(
    name="right_object",
    placement=placement.W3DPlacement(
        position=(5, 0, 0),
    ),
    content=objects.W3DText(
        text="Right"
    ),
    sound="right",  # Attach the sound named right to this object
    visible=False
)
my_project["objects"].append(left_object)
my_project["objects"].append(right_object)


# A timeline to play the sounds
my_timeline = timeline.W3DTimeline(
    name="my_timeline",
    start_immediately=False,
    actions=[
        (0, actions.SoundAction(sound_name="DOESNOTEXIST", change="Start")),
        (3.1, actions.ObjectAction(
            object_name="DOESNOTEXIST", sound_change="Start")),
        (6.2, actions.ObjectAction(
            object_name="DOESNOTEXIST", sound_change="Start"))
    ]
)
my_project["timelines"].append(my_timeline)


# Next, let's create a clickable object to start the timeline
my_object = objects.W3DObject(
    name="button",  # Give it a name
    color=(255, 0, 0),  # Make it red
    placement=placement.W3DPlacement(  # Specify position and orientation
        position=(0, 1, 0),  # We'll leave rotation as default for now
    ),
    content=objects.W3DText(  # Specify that this is a text object
        text="Play"  # ...with text reading "Hello, World!"
    ),
    link=objects.W3DLink(  # Add a clickable link to the text object
        actions={
            0: [  # On first click (index 0)...
                actions.TimelineAction(  # start the timeline
                    timeline_name="my_timeline", change="Start"
                )
            ]
        }
    )
)

# Now add this object to the project
my_project["objects"].append(my_object)
my_project["debug"] = True

# Finally, we render the whole thing using Blender, export it, and display the
# result
export_to_blender(
    my_project, filename="timeline_sound_sample.blend", display=True)
