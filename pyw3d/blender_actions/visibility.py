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

"""Tools for changing the visibility of a Blender object"""


class VisibilityAction(object):
    """Generate Python logic for how visibility should change when action first
    starts, as it continues, and when it ends

    :param bool visibility: The visibility to transition to
    :param float duration: Time for action to complete in seconds
    :param int offset: A number of tabs (4 spaces) to add before Python logic
    strings"""

    @property
    def start_string(self):
        script_text = []
        # TODO: Fade out timing appears to be mucked
        script_text.extend([
            "blender_object.color[3] = int(blender_object.visible)",
            "blender_object.setVisible(True)",
            "delta_alpha = {} - blender_object.color[3]".format(
                int(self.visible)),
            "W3D_LOG.debug(",
            "    'object {} visibility set to {}'.format(",
            "        blender_object.name, delta_alpha > 0",
            "    )",
            ")",
            "blender_object['visible_tag'] = 'delta_alpha > 0'",
            "blender_object['visV'] = delta_alpha/{}".format(
                ("({}*bge.logic.getLogicTicRate())".format(self.duration), 1)[
                    self.duration == 0])]
        )

        try:
            script_text[0] = "{}{}".format("    "*self.offset, script_text[0])
        except IndexError:
            return ""
        return "\n{}".format("    "*self.offset).join(script_text)

    @property
    def continue_string(self):
        script_text = [
            "new_color = blender_object.color",
            "new_color[3] += blender_object['visV']",
            "blender_object.color = new_color"
        ]
        try:
            script_text[0] = "{}{}".format("    "*self.offset, script_text[0])
        except IndexError:
            return ""
        return "\n{}".format("    "*self.offset).join(script_text)

    @property
    def end_string(self):
        script_text = [
            "new_color = blender_object.color",
            "new_color[3] = {}".format(int(self.visible)),
            "blender_object.color = new_color",
            "blender_object.setVisible({})".format(self.visible),
            "if 'clicks' in blender_object:",
            "    if blender_object.visible:",
            "        blender_object['clickable'] = True",
            "    else:",
            "        try:",
            "            del blender_object['clickable']",
            "        except KeyError:",
            "            pass # Already unclickable",
        ]
        try:
            script_text[0] = "{}{}".format("    "*self.offset, script_text[0])
        except IndexError:
            return ""
        return "\n{}".format("    "*self.offset).join(script_text)

    def __init__(self, visibility, duration, offset=0):
        self.visible = visibility
        self.duration = duration
        self.offset = offset
