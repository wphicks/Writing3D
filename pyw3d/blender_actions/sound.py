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

"""Tools for starting and stopping audio playback in Blender"""


class SoundChange(object):
    """Generate Python logic for playing or stopping sound
    
    :param str sound_name: The name of the sound to start or stop
    :param str change: One of "Play Sound" or "Stop Sound"
    :param str object_name: Name of object to which sound is attached, if any
    :param int offset: A number of tabs (4 spaces) to add before Python logic
    """

    @property
    def start_string(self):
        script_text = [
            "sound_object = scene.objects['{}']".format(self.object_name),
            "sound_actuator = sound_object.actuators['{}']".format(
                self.sound_name
            )
        ]
        if self.change == "Play Sound":
            script_text.append(
                "cont.activate(sound_actuator)"
            )
        elif self.change == "Stop Sound":
            script_text.append(
                "cont.deactivate(sound_actuator)"
            )
        return "\n{}".format("    "*self.offset).join(script_text)

    @property
    def continue_string(self):
        return "{}pass".format("    "*self.offset)

    @property
    def end_string(self):
        return "{}pass".format("    "*self.offset)

    def __init__(self, sound_name, change, offset, object_name=None):
        self.sound_name = generate_blender_sound_name(sound_name)
        if object_name is None:
            self.object_name = "AUDIO"
        else:
            self.object_name = generate_blender_object_name(object_name)
        self.change = change
