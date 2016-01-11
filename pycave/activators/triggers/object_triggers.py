"""A Blender-based implementation of triggers based on the state of objects in
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


class BlenderObjectPositionTrigger(BlenderTrigger):
    """Activator based on position of objects in virtual space
    """
    def create_enabled_sensor(self):
        """Add a sensor to fire continuously while trigger is enabled"""

        bpy.ops.logic.sensor_add(
            type="PROPERTY",
            object=self.name,
            name="enabled_sensor"
        )
        self.base_object.game.sensors[-1].name = "enabled_sensor"
        enable_sensor = self.base_object.game.sensors["enabled_sensor"]
        enable_sensor.use_pulse_true_level = True
        enable_sensor.frequency = 1
        enable_sensor.property = self.name
        enable_sensor.value = self.enable_immediately
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
        """Add a function to Python control script to detect user position

        :param str objects_string: A string containing either a
        Python-formatted list of names of Blender objects or a single valid
        group name (e.g. "['object_myobj1', 'object_myobj2']" or "group_mygrp"
        :param bool detect_any: True if trigger should activate when any
        specified object passes the box's boundaries as specified, False if
        trigger should activate when ALL specified objects have done so"""
        detection_logic = [
            "\ndef detect_event(cont):",
            "    scene = bge.logic.getCurrentScene()",
            "    own = cont.owner",
            "    corners = {}".format(
                zip(self["box"]["corner1"], self["box"]["corner2"])),
            "    all_objects = {}".format(self.objects_string),
            "    all_objects = ["
            "scene.objects[object_name] for object_name in all_objects]",
            "    in_region = {}".format(not self.detect_any),
            "    for object_ in all_objects:",
            "        position = object_.position",
            "        in_region = (in_region {}".format(
                ("or", "and")[not self.detect_any]),
            "            {}(position[i] < min(corners[i]) or".format(
                ("", "not ")[self.box["direction"] == "Inside"]),
            "               position[i] > max(corners[i])))",
            "    if in_region:",
            "        own['status'] = 'Start'"
        ]
        detection_logic = "\n".join(detection_logic)
        return detection_logic

    def create_blender_objects(self):
        super(BlenderObjectPositionTrigger, self).create_blender_objects()
        self.create_enabled_sensor()
        self.create_detection_controller()

    def link_logic_bricks(self):
        super(BlenderObjectPositionTrigger, self).link_logic_bricks()
        self.link_detection_bricks()

    def __init__(
            self, name, actions, box, objects_string, duration=0,
            enable_immediately=True, remain_enabled=True, detect_any=True):
        super(BlenderObjectPositionTrigger, self).__init__(
            name, actions, enable_imediately=enable_immediately,
            remain_enabled=remain_enabled)
        self.box = box
        self.objects_string = objects_string
        self.detect_any = detect_any
