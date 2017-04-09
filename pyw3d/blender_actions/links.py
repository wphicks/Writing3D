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

"""Tools for dynamically changing clickable links in Blender"""
from pyw3d.names import generate_blender_object_name
from pyw3d.errors import EBKAC


class LinkAction(object):
    """Generate Python logic for how link should change when action first
    starts, as it continues, and when it ends

    :param str change: The change to be performed (one of "Enable", "Disable",
    "Activate", or "Activate if enabled")
    :param int offset: A number of tabs (4 spaces) to add before Python logic
    strings"""

    @property
    def start_string(self):
        script_text = [
            "trigger = scene.objects['{}']".format(self.link_name)
        ]
        if self.change == "Enable":
            script_text.append(
                "trigger['click_status'] = 'unselected'"
            )
        elif self.change == "Disable":
            script_text.append(
                "trigger['click_status'] = 'disabled'"
            )
        elif self.change == "Activate":
            script_text.append(
                "trigger['status'] = 'Start'"
            )
        elif self.change == "Activate if enabled":
            script_text.extend([
                "if trigger['click_status'] == 'unselected':",
                "    trigger['status'] = 'Start'"]
            )
        else:
            raise EBKAC(
                "Link action must be one of 'Enable', 'Disable', 'Activate', "
                "'Activate if enabled'")

        try:
            script_text[0] = "{}{}".format(
                "    " * self.offset, script_text[0]
            )
        except IndexError:
            return ""
        return "\n{}".format("    " * self.offset).join(script_text)

    @property
    def continue_string(self):
        return "{}pass".format("    " * self.offset)

    @property
    def end_string(self):
        return "{}pass".format("    " * self.offset)

    def __init__(self, object_name, change, offset=0):
        self.link_name = generate_blender_object_name(object_name)
        self.change = change
        self.offset = offset
