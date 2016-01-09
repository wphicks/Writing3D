"""Classes used to initiate actions in Blender
"""
import warnings
from .errors import EBKAC
from .names import generate_blender_timeline_name
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
                'Must start timeline before continue is used')
        time = monotonic() - own['start_time']
        index = own['offset_index'] + own['action_index']
"""
        self.script_footer = """
        # FOOTER BEGINS HERE
        own['action_index'] = index
        own['offset_index'] = 0
        if time >= {}:
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
            type='BOOLEAN',
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
        activating CaveActions"""
        action_logic = ["        # ACTION LOGIC BEGINS HERE"]
        action_index = 0
        if len(self["actions"]) == 0:
            max_time = 0
        else:
            max_time = self["actions"][-1][0]
        for time, action in self["actions"]:
            action_logic.extend(
                ["".join(("        ", line)) for line in
                    action.generate_blender_logic(
                        time_condition=time,
                        index_condition=action_index
                    )]
            )
            action_index += 1
            max_time = max(max_time, action.end_time)
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
