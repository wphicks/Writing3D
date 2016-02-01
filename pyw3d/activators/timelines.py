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

"""A Blender-based timeline implementation
"""
from pyw3d.names import generate_blender_timeline_name
from .activators import Activator


class BlenderTimeline(Activator):
    """Activates actions at specified times"""

    @property
    def name(self):
        return generate_blender_timeline_name(self.name_string)

    def create_status_property(self):
        return super(BlenderTimeline, self).create_status_property(
            initial_value=("Stop", "Start")[self.start_immediately])

    def generate_action_logic(self):
        action_logic = ["        # ACTION LOGIC BEGINS HERE"]
        action_index = 0
        if len(self.actions) == 0:
            max_time = 0
        else:
            max_time = self.actions[-1][0]
        for time, action in self.actions:
            action_logic.extend(
                action.generate_blender_logic(
                    time_condition=time,
                    index_condition=action_index,
                    offset=2)
            )
            action_index += 1
            max_time = max(max_time, action.end_time)
        self.script_footer = self.script_footer.format(max_time=max_time)
        return "\n".join(action_logic)

    def __init__(self, name, actions, start_immediately=False):
        super(BlenderTimeline, self).__init__(name, actions)
        self.start_immediately = start_immediately
