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

"""A Blender-based implementation of event triggers"""
from pyw3d.names import generate_trigger_name
from pyw3d.activators import Activator


class BlenderTrigger(Activator):
    """Activator based on detection of events in virtual space"""

    @property
    def name(self):
        return generate_trigger_name(self.name_string)

    def generate_action_logic(self):
        action_logic = ["        # ACTION LOGIC BEGINS HERE"]
        # TODO: Duration remains to be implemented. Duration is
        # a measure of how long a trigger must remain triggered
        # before its actions begin
        action_index = 0
        for action in self.actions:
            action_logic.extend(
                action.generate_blender_logic(
                    time_condition=0,
                    index_condition=action_index,
                    offset=2)
            )
            action_index += 1
        self.script_footer = self.script_footer.format(
            action_count=action_index
        )
        self.script_footer = "\n".join(
            [
                self.script_footer,
                "            own['enabled'] = {}".format(self.remain_enabled)
            ]
        )
        return "\n".join(action_logic)

    def generate_detection_logic(self):
        """Create logic for detecting triggering event

        Dummy method intended to be overridden by subclasses"""
        return ""

    def write_python_logic(self):
        """Write any necessary Python controller scripts for this activator"""
        script_text = [
            self.script_header,
            self.generate_action_logic(),
            self.script_footer,
            self.generate_detection_logic()
        ]
        self.script.write("\n".join(script_text))
        return self.script

    def create_enabled_property(self):
        return super(BlenderTrigger, self).create_enabled_property(
            self.enable_immediately)

    def get_actions(self):
        """Return a list of W3DActions that are controlled by this activator

        This method is necessary because of a very bad design decision which
        assigned different meanings to self.actions for different activators.
        This *will* be corrected in an upcoming refactoring but must remain for
        now in an effort to prepare for the next semester of the Writing3D
        workshop as soon as possible."""
        return self.actions

    def __init__(
            self, name, actions, duration=0, enable_immediately=True,
            remain_enabled=True):
        super(BlenderTrigger, self).__init__(name, actions)
        self.duration = duration
        self.enable_immediately = enable_immediately
        self.remain_enabled = remain_enabled
