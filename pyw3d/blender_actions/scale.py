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

"""Tools for scaling Blender objects"""


class ScaleAction(object):
    """Generate Python logic for how scale should change when action first
    starts, as it continues, and when it ends

    :param float scale: The scale to transition to
    :param float duration: Time for action to complete in seconds
    :param int offset: A number of tabs (4 spaces) to add before Python logic
    strings"""

    @property
    def start_string(self):
        script_text = []
        script_text.extend([
            "new_scale = {}".format(self.scale),
            "blender_object['scaleV'] = [",
            "    (new_scale - blender_object.scaling[i])/{}".format(
                ("({}*bge.logic.getLogicTicRate())".format(self.duration), 1)[
                    self.duration == 0]),
            "    for i in range(len(blender_object.scaling))]"]
        )

        try:
            script_text[0] = "{}{}".format("    "*self.offset, script_text[0])
        except IndexError:
            return ""
        return "\n{}".format("    "*self.offset).join(script_text)

    @property
    def continue_string(self):
        script_text = [
            "blender_object.scaling = [",
            "    (blender_object.scaling[i] + blender_object['scaleV'][i])",
            "    for i in range(len(blender_object.scaling))]"
        ]
        try:
            script_text[0] = "{}{}".format("    "*self.offset, script_text[0])
        except IndexError:
            return ""
        return "\n{}".format("    "*self.offset).join(script_text)

    @property
    def end_string(self):
        script_text = [
            "blender_object.scaling = {}".format([self.scale]*3)]
        try:
            script_text[0] = "{}{}".format("    "*self.offset, script_text[0])
        except IndexError:
            return ""
        return "\n{}".format("    "*self.offset).join(script_text)

    def __init__(self, scale, duration, offset=0):
        self.scale = scale
        self.duration = duration
        self.offset = offset
