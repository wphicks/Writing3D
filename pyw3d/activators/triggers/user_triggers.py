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

"""A Blender-based implementation of triggers based on the state of the user in
virtual space
"""
import warnings
from pycave.errors import EBKAC
from .triggers import BlenderTrigger
try:
    import bpy
except ImportError:
    warnings.warn(
        "Module bpy not found. Loading "
        "pycave.activators.triggers.object_triggers as standalone")

# TODO: There's some code reuse happening between this and object_triggers


class BlenderPositionTrigger(BlenderTrigger):
    """Activator based on position of user in virtual space"""

    def create_enabled_sensor(self):
        """Add a sensor to fire continuously while trigger is enabled"""
        base_object = self.select_base_object()
        bpy.ops.logic.sensor_add(
            type="PROPERTY",
            object=self.name,
            name="enabled_sensor"
        )
        base_object.game.sensors[-1].name = self.name
        enable_sensor = base_object.game.sensors[self.name]
        enable_sensor.use_pulse_true_level = True
        enable_sensor.frequency = 1
        enable_sensor.property = "enabled"
        enable_sensor.value = "True"
        self.enable_sensor = enable_sensor
        return enable_sensor

    def create_detection_controller(self):
        """Add a controller for detecting specified event"""

        bpy.ops.logic.controller_add(
            type='PYTHON',
            object=self.name,
            name="detect")
        controller = self.base_object.game.controllers["detect"]
        controller.mode = "MODULE"
        controller.module = "{}.detect_event".format(self.name)
        self.detect_controller = controller
        return controller

    def link_detection_bricks(self):
        """Link necessary logic bricks for event detection

        :raises EBKAC: if controller or sensor does not exist"""
        try:
            self.detect_controller.link(sensor=self.enable_sensor)
        except AttributeError:
            raise EBKAC(
                "Detection sensor and controller must be created before they "
                "can be linked")
        return self.detect_controller

    def generate_detection_logic(self):
        """Add a function to Python control script to detect user position"""
        detection_logic = [
            "\ndef detect_event(cont):",
            "    scene = bge.logic.getCurrentScene()",
            "    own = cont.owner",
            "    position = scene.objects['CAMERA'].position",
            "    inside = True",
            "    corners = {}".format(
                list(zip(self.box["corner1"], self.box["corner2"]))),
            "    for i in range({}):".format((3, 2)[self.box["ignore_y"]]),
            "        if (",
            "                position[i] < min(corners[i]) or",
            "                position[i] > max(corners[i])):",
            "            inside = False",
            "            break",
            "    if ({} and own['enabled'] and".format(
                ("not inside", "inside")[
                    self.box["direction"] == "Inside"]),
            "            own['status'] == 'Stop'):",
            "        own['status'] = 'Start'"
        ]
        detection_logic = "\n".join(detection_logic)
        return detection_logic

    def create_blender_objects(self):
        super(BlenderPositionTrigger, self).create_blender_objects()
        self.create_enabled_sensor()
        self.create_detection_controller()

    def link_logic_bricks(self):
        super(BlenderPositionTrigger, self).link_logic_bricks()
        self.link_detection_bricks()

    def __init__(
            self, name, actions, box, duration=0, enable_immediately=True,
            remain_enabled=True):
        super(BlenderPositionTrigger, self).__init__(
            name, actions, duration=duration,
            enable_immediately=enable_immediately,
            remain_enabled=remain_enabled)
        self.box = box
