"""Blender-based implementation of triggers based on the user's field of view
"""
import math
import warnings
from pycave.names import generate_blender_object_name
from pycave.errors import EBKAC
from .triggers import BlenderTrigger
try:
    import bpy
except ImportError:
    warnings.warn(
        "Module bpy not found. Loading "
        "pycave.activators.triggers.look_triggers as standalone")


class BlenderLookAtTrigger(BlenderTrigger):
    """Activator based on where user is looking"""
    # TODO: Restructure methods to be consistent with other triggers

    def select_camera(self):
        """Select the main camera for modifications"""
        camera_object = bpy.data.objects["CAMERA"]
        bpy.context.scene.objects.active = camera_object
        return camera_object

    def create_enabled_copier(self):
        """Create system to copy enabled value to camera property

        Adds a sensor to detect when "enabled" property is changed on
        base_object, a trivial "and" controller, and an actuator to copy the
        "enabled" property to the camera property of the same name as this
        trigger.This allows camera to only go through costly detection actions
        when the trigger is enabled.
        """
        self.select_base_object()
        bpy.ops.logic.sensor_add(
            type="PROPERTY",
            object=self.name,
            name="enabled_sensor"
        )
        self.base_object.game.sensors[-1].name = "enabled_sensor"
        enabled_sensor = self.base_object.game.sensors["enabled_sensor"]
        enabled_sensor.property = "enabled"
        enabled_sensor.evaluation_type = "PROPCHANGED"

        self.select_base_object()
        bpy.ops.logic.controller_add(
            type='LOGIC_AND',
            object=self.name,
            name="enable")
        controller = self.base_object.game.controllers["enable"]

        camera_object = self.select_camera()
        bpy.ops.logic.actuator_add(
            type="PROPERTY",
            object="CAMERA",
            name=self.name
        )
        camera_object.game.actuators[-1].name = self.name
        property_copier = camera_object.game.actuators[self.name]
        property_copier.mode = "COPY"
        property_copier.property = self.name
        property_copier.object = self.base_object
        property_copier.object_property = "enabled"

        return (enabled_sensor, controller, property_copier)

    def setup_camera(self):
        """Create a property, property sensor, and Python controller on the
        main camera for keeping track of if this trigger is enabled

        This setup is used for efficiency. By having the camera know when this
        trigger is enabled, we can have it only perform (expensive) checks
        related to the trigger when it is in fact enabled.
        """
        camera_object = self.select_camera()
        # Property on camera to keep track of when trigger is enabled
        bpy.ops.object.game_property_new(
            type='BOOL',
            name=self.name
        )
        camera_object.game.properties[
            self.name].value = self.enable_immediately
        # Sensor to fire continuously while trigger is enabled
        bpy.ops.logic.sensor_add(
            type="PROPERTY",
            object="CAMERA",
            name=self.name
        )
        camera_object.game.sensors[-1].name = self.name
        camera_enable_sensor = camera_object.game.sensors[self.name]
        camera_enable_sensor.use_pulse_true_level = True
        camera_enable_sensor.frequency = 1
        camera_enable_sensor.property = self.name
        camera_enable_sensor.value = str(self.enable_immediately)
        self.camera_enable_sensor = camera_enable_sensor

        #Create controller to detect trigger events
        camera_object = self.select_camera()
        bpy.ops.logic.controller_add(
            type='PYTHON',
            object="CAMERA",
            name=self.name)
        camera_object.game.controllers[-1].name = self.name
        controller = camera_object.game.controllers[self.name]
        controller.mode = "MODULE"
        controller.module = "{}.detect_event".format(self.name)

        return camera_object

    def link_camera_bricks(self):
        """Link BGE logic bricks for camera"""
        camera_object = self.select_camera()
        camera_controller = camera_object.game.controllers[self.name]
        try:
            camera_controller.link(sensor=self.camera_enable_sensor)
        except AttributeError:
            raise EBKAC(
                "Enabled sensor must be created on camera before being linked")

        enabled_sensor = self.base_object.game.sensors["enabled_sensor"]
        enabled_controller = self.base_object.game.controllers["enable"]
        property_copier = camera_object.game.actuators[self.name]
        enabled_controller.link(
            sensor=enabled_sensor, actuator=property_copier)

        return (enabled_controller, camera_controller)

    def create_blender_objects(self):
        super(BlenderLookAtTrigger, self).create_blender_objects()
        self.setup_camera()
        self.create_enabled_copier()

    def link_logic_bricks(self):
        super(BlenderLookAtTrigger, self).link_logic_bricks()
        self.link_camera_bricks()


class BlenderPointTrigger(BlenderLookAtTrigger):
    """Trigger based on user looking at a point in virtual space"""

    def __init__(
            self, name, actions, point, duration=0, enable_immediately=True,
            remain_enabled=True):
        super(BlenderPointTrigger, self).__init__(
            name, actions, duration=duration,
            enable_immediately=enable_immediately,
            remain_enabled=remain_enabled)
        self.point = point

    def generate_detection_logic(self):
        """Add a function to Python control script to detect user position"""
        detection_logic = [
            "\ndef detect_event(cont):",
            "    scene = bge.logic.getCurrentScene()",
            "    own = cont.owner",
            "    trigger = scene.objects['{}']".format(
                self.name),
            "    # Following is total hack since pointInsideFrustum seems to",
            "    # give false positive on first frame in certain",
            "    # circumstances",
            "    if 'initialized' not in trigger:",
            "        trigger['initialized'] = True",
            "        return",
            "    if (own.pointInsideFrustum({})".format(
                tuple(self.point)),
            "            and trigger['enabled'] and",
            "            trigger['status'] == 'Stop'):",
            "        trigger['status'] = 'Start'"
        ]
        detection_logic = "\n".join(detection_logic)
        return detection_logic


class BlenderDirectionTrigger(BlenderLookAtTrigger):
    """Trigger based on user looking in a direction in virtual space"""

    def __init__(
            self, name, actions, direction, duration=0,
            enable_immediately=True, remain_enabled=True, angle=30):
        super(BlenderDirectionTrigger, self).__init__(
            name, actions, duration=duration,
            enable_immediately=enable_immediately,
            remain_enabled=remain_enabled)
        self.direction = direction
        self.angle = angle

    def generate_detection_logic(self):
        """Add a function to Python control script to detect user position"""
        detection_logic = [
            "\ndef detect_event(cont):",
            "    scene = bge.logic.getCurrentScene()",
            "    own = cont.owner",
            "    cam_dir = (own.getCameraToWorld().to_quaternion() *",
            "        mathutils.Vector((0, 0, -1)))",
            "    target_dir = mathutils.Vector({})".format(
                tuple(self.direction)),
            "    angle = abs(cam_dir.angle(target_dir, 3.14))",
            "    trigger = scene.objects['{}']".format(
                self.name),
            "    if (angle < {}".format(math.radians(self.angle)),
            "            and trigger['enabled'] and",
            "            trigger['status'] == 'Stop'):",
            "        trigger['status'] = 'Start'"
        ]
        detection_logic = "\n".join(detection_logic)
        return detection_logic


class BlenderLookObjectTrigger(BlenderLookAtTrigger):
    """Trigger based on user looking at an object in virtual space

    :param str look_at_object: Name of the CaveObject to be looked at"""

    def __init__(
            self, name, actions, look_at_object, duration=0,
            enable_immediately=True, remain_enabled=True, angle=30):
        super(BlenderDirectionTrigger, self).__init__(
            name, actions, duration=duration,
            enable_immediately=enable_immediately,
            remain_enabled=remain_enabled)
        self.look_at_object = generate_blender_object_name(look_at_object)
        self.angle = angle

    def generate_detection_logic(self):
        """Add a function to Python control script to detect user position"""
        detection_logic = [
            "\ndef detect_event(cont):",
            "    scene = bge.logic.getCurrentScene()",
            "    own = cont.owner",
            "    position = scene.objects[{}].position".format(
                self.look_at_object),
            "    trigger = scene.objects['{}']".format(
                self.name),
            "    # Following is total hack since pointInsideFrustum seems to",
            "    # give false positive on first frame in certain",
            "    # circumstances",
            "    if 'initialized' not in trigger:",
            "        trigger['initialized'] = True",
            "        return",
            "    if (own.pointInsideFrustum(position)",
            "            and trigger['enabled']",
            "            and trigger['status'] == 'Stop'):",
            "        trigger['status'] = 'Start'"
        ]
        detection_logic = "\n".join(detection_logic)
        return detection_logic
