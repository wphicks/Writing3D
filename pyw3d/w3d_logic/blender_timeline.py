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

"""Implementation of W3D-style timeline control in Blender"""

from .blender_trigger import TimedTrigger
import logging
try:
    import bpy
except ImportError:
    logging.warn(
        "Module bpy not found. \
Loading pyw3d.cave_logic.blender_trigger as standalone")

class BlenderTimeline(TimedTrigger):
    """A control structure within Blender for implementing timelines

    :param W3DTimeline timeline: The timeline to generate"""

    def get_object(self):
        """Create an empty object for timeline"""
        bpy.ops.object.add(
            type="EMPTY",
            layers=[layer == 20 for layer in range(1, 21)],
        )
        timeline_object = bpy.context.object
        timeline_object.name = self.blender_object_name
        return timeline_object

    def __init__(self, timeline):
        self.cave_timeline = timeline
        super(BlenderTimeline, self).__init__(
            self.cave_timeline["name"],
            self.cave_timeline["actions"][-1][0]
        )
        #NOPE! Not going to work if the last action in the timeline is at
        #duration 0
