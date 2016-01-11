"""Classes used to initiate actions in Blender
"""
import warnings
import math
from .errors import EBKAC
from .names import generate_blender_timeline_name, generate_trigger_name,\
    generate_blender_object_name
try:
    import bpy
except ImportError:
    warnings.warn(
        "Module bpy not found. Loading pycave.timeline as standalone")


class Activator(object):
    """An object used to create BGE logic for triggering CaveActions

    :param str name_string: A string which is used to generate the name of the
    object associated with this activator (e.g. the user-assigned name of a
    timeline)
    :param SortedList actions: A list of actions to be activated by this
    activator

    Associated with every Activator is a single Blender object called
    base_object, which has a "status" property. This status is used to control
    when execution of actions is triggered.
    """

    def __init__(self, name_string, actions):
        self.name_string = name_string
        self.actions = actions
        self.script_header = """
import bge
from group_defs import *
import mathutils
from time import monotonic
def activate(cont):
    scene = bge.logic.getCurrentScene()
    own = cont.owner
    status = own['status']
    if status == 'Start':
        own['start_time'] = monotonic()
        own['action_index'] = 0
        # action_index property is used to ensure that each action is activated
        # exactly once
        own['offset_time'] = 0
        own['offset_index'] = 0
        own['status'] = 'Continue'
    if status == 'Stop':
        try:
            own['offset_time'] = monotonic() - own['start_time']
            own['offset_index'] = own['action_index']
        except KeyError:
            pass
    if status == 'Continue':
        try:
            if own['offset_time'] != 0:
                own['start_time'] = (
                    monotonic() - own['offset_time'])
                own['offset_time'] = 0
        except KeyError:
            raise RuntimeError(
                'Must start activator before continue is used')
        time = monotonic() - own['start_time']
        index = own['offset_index'] + own['action_index']
"""
        self.script_footer = """
        # FOOTER BEGINS HERE
        own['action_index'] = index
        own['offset_index'] = 0
        if time >= {max_time}:
            own['status'] = 'Stop'
"""

    @property
    def name(self):
        """A method intended to be overridden with the proper function from
        names.py"""
        return self.name_string

    def select_base_object(self):
        """Select base_object in Blender for modifications"""
        bpy.context.scene.objects.active = self.base_object
        return self.base_object

    def create_status_property(self, initial_value="Stop"):
        """Creates a property called "status" which defines whether the
        activator is in a "Start", "Stop", or "Continue" state

        Note that Stop essentially pauses any partially completed actions for
        an activator, if possible. Continue means that the actions are ongoing,
        and Start is used to initially start the actions associated with this
        activator"""
        self.select_base_object()
        bpy.ops.object.game_property_new(
            type='STRING',
            name='status'
        )
        self.base_object.game.properties["status"].value = initial_value
        return self.base_object.game.properties["status"]

    def create_enabled_property(self, initial_value=True):
        """Creates a property called "enabled" which defines whether or not
        activator can currently be activated

        .. warn: This property should be checked when a CaveAction attempts to
        start an activator. It is NOT checked by the activator itself. This is
        to allow the activator to be immediately disabled after activation but
        still process the remainder of its actions"""
        self.select_base_object()
        bpy.ops.object.game_property_new(
            type='BOOL',
            name='enabled'
        )
        self.base_object.game.properties["enabled"].value = initial_value
        return self.base_object.game.properties["enabled"]

    def create_status_sensors(self):
        """Creates sensors to detect change in "status" of activator

        Generates three sensors: "start_sensor" which detects when the status
        is set to "Start", "active_sensor" which sends continuous pulses so
        long as the status is set to "Continue", and "stop_sensor" which
        detects when the status is set to "Stop"
        """
        self.select_base_object()
        #Create property sensor to initiate actions
        bpy.ops.logic.sensor_add(
            type="PROPERTY",
            object=self.name,
            name="start_sensor"
        )
        self.base_object.game.sensors[-1].name = "start_sensor"
        start_sensor = self.base_object.game.sensors["start_sensor"]
        start_sensor.property = "status"
        start_sensor.value = "Start"

        #Create property sensor to activate actions
        bpy.ops.logic.sensor_add(
            type="PROPERTY",
            object=self.name,
            name="active_sensor"
        )
        self.base_object.game.sensors[-1].name = "active_sensor"
        active_sensor = self.base_object.game.sensors["active_sensor"]
        active_sensor.use_pulse_true_level = True
        active_sensor.frequency = 1
        active_sensor.property = "status"
        active_sensor.value = "Continue"

        #Create property sensor to pause actions
        bpy.ops.logic.sensor_add(
            type="PROPERTY",
            object=self.name,
            name="stop_sensor"
        )
        self.base_object.game.sensors[-1].name = "stop_sensor"
        stop_sensor = self.base_object.game.sensors["stop_sensor"]
        stop_sensor.property = "status"
        stop_sensor.value = "Stop"

        self.start_sensor = start_sensor
        self.active_sensor = active_sensor
        self.stop_sensor = stop_sensor
        return [start_sensor, active_sensor, stop_sensor]

    def create_controller(self):
        """Create a Python controller used to effect actions triggered by this
        Activator"""
        self.select_base_object()
        bpy.ops.logic.controller_add(
            type='PYTHON',
            object=self.name,
            name="activate")
        controller = self.base_object.game.controllers["activate"]
        controller.mode = "MODULE"
        controller.module = "{}.activate".format(self.name)
        self.controller = controller
        return controller

    def link_status_sensors(self):
        """Link the start, active, and stop sensors to the controller

        :raises EBKAC: if controller or sensors do not exist"""
        try:
            controller = self.controller
        except AttributeError:
            raise EBKAC(
                "Controller must be created before sensors can be linked")
        try:
            controller.link(self.start_sensor)
            controller.link(self.active_sensor)
            controller.link(self.stop_sensor)
        except AttributeError:
            raise EBKAC(
                "Sensors must be created before they can be linked")
        return controller

    def _create_base_object(self):
        """Create the object which controls the current status of the
        activator"""
        bpy.ops.object.add(
            type="EMPTY",
            layers=[layer == 20 for layer in range(1, 21)]
        )
        return bpy.context.scene.objects.active

    @property
    def base_object(self):
        """Returns the object which controls the current status of the
        activator, creating it if necessary"""
        try:
            return bpy.data.objects[self.name]
        except KeyError:
            blender_object = self._create_base_object()
            blender_object.name = self.name
            return blender_object

    @property
    def script(self):
        """Returns the Python control script for base_object, creating it if
        necessary"""
        script_name = ".".join((self.name, "py"))
        try:
            return bpy.data.texts[script_name]
        except KeyError:
            bpy.data.texts.new(script_name)
            return bpy.data.texts[script_name]

    def generate_action_logic(self):
        """Returns a string to be written into Python control script for
        activating CaveActions

        .. note: This method is responsible for writing the max_time for
        execution of actions into the script_footer. Failure to do this will
        result in BGE complaining about attempting to compare a dictionary with
        an integer or having the name max_time not defined"""
        action_logic = ["        # ACTION LOGIC BEGINS HERE"]
        max_time = 0
        self.script_footer = self.script_footer.format(max_time=max_time)
        return "\n".join(action_logic)

    def create_blender_objects(self):
        """Generate all new objects, properties, sensors, and controllers
        associated with this activator in Blender

        .. note:: This is a separate step from connecting logic bricks in order
        to ensure that all necessary objects, sensors, controllers, and
        actuators are created before we attempt to link them. Nevertheless, it
        is crucial that both of these steps (and writing Python logic, if
        necessary) be called when creating an Activator.
        """
        self.create_status_property()
        self.create_status_sensors()
        self.create_controller()
        self.create_enabled_property()

    def link_logic_bricks(self):
        """Link together any Blender "logic bricks" for this activator"""
        self.link_status_sensors()

    def write_python_logic(self):
        """Write any necessary Python controller scripts for this activator"""
        script_text = [
            self.script_header,
            self.generate_action_logic(),
            self.script_footer
        ]
        self.script.write("\n".join(script_text))
        return self.script


class BlenderTimeline(Activator):

    @property
    def name(self):
        return generate_blender_timeline_name(self.name_string)

    def create_status_property(self):
        return super(BlenderTimeline, self).create_status_property(
            initial_value=("Stop", "Start")[self.start_immediately])

    def generate_action_logic(self):
        action_logic = [super(BlenderTimeline, self).generate_action_logic()]
        action_index = 0
        if len(self.actions) == 0:
            max_time = 0
        else:
            max_time = self.actions[-1][0]
        for time, action in self.actions:
            action_logic.extend(
                ["".join(("        ", line)) for line in
                    action.generate_blender_logic(
                        time_condition=time,
                        index_condition=action_index
                    )]
            )
            action_index += 1
            max_time = max(max_time, action.end_time)
        self.script_footer = self.script_footer.format(max_time=max_time)
        return "\n".join(action_logic)

    def __init__(self, name, actions, start_immediately=False):
        super(BlenderTimeline, self).__init__(name, actions)
        self.start_immediately = start_immediately


class BlenderTrigger(Activator):
    """Activator based on detection of events in virtual space"""

    @property
    def name(self):
        return generate_trigger_name(self.name_string)

    def generate_action_logic(self):
        action_logic = [super(BlenderTrigger, self).generate_action_logic()]
        max_time = self.duration
        #TODO: The above is incorrect. Duration is actually a measure of how
        #long a trigger must remain triggered before its actions begin
        action_index = 0
        for action in self.actions:
            action_logic.extend(
                ["".join(("        ", line)) for line in
                    action.generate_blender_logic(
                        time_condition=0,
                        index_condition=action_index
                    )]
            )
            action_index += 1
            max_time = max(max_time, action.end_time)
        self.script_footer = self.script_footer.format(max_time=max_time)
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

    def __init__(
            self, name, actions, duration=0, enable_immediately=True,
            remain_enabled=True):
        super(BlenderTrigger, self).__init__(name, actions)
        self.duration = duration
        self.enable_immediately = enable_immediately
        self.remain_enabled = remain_enabled


class BlenderPositionTrigger(BlenderTrigger):
    """Activator based on position of user in virtual space"""

    def generate_detection_logic(self):
        """Add a function to Python control script to detect user position"""
        detection_logic = [
            "\ndef detect_event(cont):",
            "    scene = bge.logic.getCurrentScene()",
            "    own = cont.owner",
            "    position = own.position",
            "    inside = True",
            "    corners = {}".format(
                zip(self.box["corner1"], self.box["corner2"])),
            "    for i in range({}):".format((3, 2)[self.box["ignore_y"]]),
            "        if (",
            "                position[i] < min(corners[i]) or",
            "                position[i] > max(corners[i])):",
            "            inside = False",
            "            break",
            "    if {}:".format(
                ("not inside", "inside")[
                    self.box["direction"] == "Inside"]),
            "        trigger = scene.objects['{}']".format(
                self.name),
            "        trigger['status'] = 'Start'"
        ]
        detection_logic = "\n".join(detection_logic)
        return detection_logic

    def __init__(
            self, name, actions, box, duration=0, enable_immediately=True,
            remain_enabled=True):
        super(BlenderPositionTrigger, self).__init__(
            name, actions, enable_imediately=enable_immediately,
            remain_enabled=remain_enabled)
        self.box = box


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
        super(BlenderPositionTrigger, self).__init__(
            name, actions, enable_imediately=enable_immediately,
            remain_enabled=remain_enabled)
        self.box = box
        self.objects_string = objects_string
        self.detect_any = detect_any


class BlenderLookAtTrigger(BlenderTrigger):
    """Activator based on where user is looking"""

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
        enabled_sensor.evaluation_type = "CHANGED"

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
        property_copier.object = self.name
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
            type='BOOLEAN',
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
        camera_enable_sensor.value = self.enable_immediately

        #Create controller to detect trigger events
        camera_object = self.select_camera()
        bpy.ops.logic.controller_add(
            type='PYTHON',
            object="CAMERA",
            name=self.name)
        controller = camera_object.game.controllers[self.name]
        controller.mode = "MODULE"
        controller.module = "{}.detect_event".format(self.name)

        return camera_object

    def link_camera_bricks(self):
        """Link BGE logic bricks for camera"""
        camera_object = self.select_camera()
        camera_controller = camera_object.game.controllers[self.name]
        camera_controller.link(sensor=self.name)

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
            "    if own.pointInsideFrustrum({}):".format(
                tuple(self["point"])),
            "        trigger = scene.objects['{}']".format(
                self.name),
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
            "    cam_dir = (own.matrix_world.to_quaternion() *",
            "        mathutils.Vector((0, 1, 0)))",
            "    target_dir = mathutils.Vector({})".format(
                tuple(self.direction)),
            "    angle = abs(cam_dir.angle(target_dir, 1.571))",
            "    if angle < {}:".format(
                math.radians(self.angle)),
            "        trigger = scene.objects['{}']".format(
                self.name),
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
            "    if own.pointInsideFrustrum(position):",
            "        trigger = scene.objects['{}']".format(
                self.name),
            "        trigger['status'] = 'Start'"
        ]
        detection_logic = "\n".join(detection_logic)
        return detection_logic
