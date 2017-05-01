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

"""Classes used to initiate actions in Blender
"""
import logging
from pyw3d.errors import EBKAC
LOGGER = logging.getLogger("pyw3d")
try:
    import bpy
except ImportError:
    LOGGER.debug(
        "Module bpy not found. Loading pyw3d.timeline as standalone")


class Activator(object):
    """An object used to create BGE logic for triggering W3DActions

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
        self.actuators = []
        self.script_header = """
import bge
from w3d_settings import *
from group_defs import *
import mathutils
from time import monotonic
import random
import logging
def activate(cont):
    try:  # UGLY HACK
        activate.target_pos
    except:
        activate.target_pos = {}
        activate.target_orientation = {}
    scene = bge.logic.getCurrentScene()
    own = cont.owner
    status = own['status']
    if status != "Continue":
        W3D_LOG.debug("activate called on {} with status {}".format(
            own.name, own['status']))
    if status == 'Start':
        own['start_time'] = monotonic()
        if ('action_index' not in own
                or 'clicks' not in own
                or own['clicks'] == 0):
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
        stop_block = False  # A flag to handle timeline restarting self
        try:
            if own['offset_time'] != 0:
                own['start_time'] = (
                    monotonic() - own['offset_time'])
                own['offset_time'] = 0
        except KeyError:
            # Should this just switch status to start instead of throwing an
            # error?
            raise RuntimeError(
                'Must start activator before continue is used')
        time = monotonic() - own['start_time']
        index = own['offset_index'] + own['action_index']
        #W3D_LOG.debug("Action Index {} at time {} on {}".format(
        #    index, time, own.name)
        #)
"""
        self.script_footer = """
        # FOOTER BEGINS HERE
        own['action_index'] = index
        own['offset_index'] = 0
        if time >= {max_time}:
            if not stop_block:
                own['status'] = 'Stop'
            own['action_index'] = 0
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

        .. warn: This property should be checked when a W3DAction attempts to
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
        LOGGER.debug(
            "Creating status sensors for {}".format(self.name_string)
        )
        self.select_base_object()
        # Create property sensor to initiate actions
        bpy.ops.logic.sensor_add(
            type="PROPERTY",
            object=self.name,
            name="start_sensor"
        )
        self.base_object.game.sensors[-1].name = "start_sensor"
        start_sensor = self.base_object.game.sensors["start_sensor"]
        start_sensor.property = "status"
        start_sensor.value = "Start"

        # Create property sensor to activate actions
        bpy.ops.logic.sensor_add(
            type="PROPERTY",
            object=self.name,
            name="active_sensor"
        )
        self.base_object.game.sensors[-1].name = "active_sensor"
        active_sensor = self.base_object.game.sensors["active_sensor"]
        active_sensor.use_pulse_true_level = True
        active_sensor.property = "status"
        active_sensor.value = "Continue"

        # Create property sensor to pause actions
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
        LOGGER.debug(
            "Creating controller for {}".format(self.name_string)
        )
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

    def create_actuators(self):
        """Create any Blender actuators"""
        LOGGER.debug(
            "Creating actuator list for {}".format(self.name_string)
        )
        for action in self.get_actions():
            self.actuators.extend(action.actuators)

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

    def link_actuators(self):
        """Link actuators necessary to invoke actions"""
        LOGGER.debug(
            "Linking actuators for {}".format(self.name_string)
        )
        try:
            controller = self.controller
        except AttributeError:
            raise EBKAC(
                "Controller must be created before actuators can be linked")
        for action in self.get_actions():
            for actuator in action.actuators:
                actuator.link(controller)

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
        activating W3DActions

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
        self.create_actuators()
        self.create_enabled_property()

    def link_logic_bricks(self):
        """Link together any Blender "logic bricks" for this activator"""
        LOGGER.debug(
            "Linking all logic bricks for {}".format(self.name_string)
        )
        self.link_status_sensors()
        self.link_actuators()

    def write_python_logic(self):
        """Write any necessary Python controller scripts for this activator"""
        LOGGER.debug(
            "Writing controller script for {}".format(self.name_string)
        )
        script_text = [
            self.script_header,
            self.generate_action_logic(),
            self.script_footer
        ]
        self.script.write("\n".join(script_text))
        return self.script
