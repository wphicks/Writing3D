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

"""Blender implementation of clickable object links in virtual space
"""
import logging
from .triggers import BlenderTrigger
from pyw3d.blender_scripts import DISABLE_LINK_SCRIPT, UNSELECT_LINK_SCRIPT,\
    SELECT_LINK_SCRIPT, ACTIVATE_LINK_SCRIPT
LOGGER = logging.getLogger("pyw3d")
try:
    import bpy
except ImportError:
    LOGGER.debug(
        "Module bpy not found. Loading pyw3d.timeline as standalone")


class BlenderClickTrigger(BlenderTrigger):
    """Activator based on mouseclick on objects in virtual space

    :param str object_name: The name of the clickable object
    """

    def create_click_status_property(self):
        """Add property to track if link is disabled, unselected, selected, or
        activated"""
        click_object = self.select_base_object()
        bpy.ops.object.game_property_new(
            type='STRING',
            name='click_status'
        )
        click_object.game.properties["click_status"].value = "False"
        return click_object.game.properties["click_status"]

    def create_click_status_sensors(self):
        """Add property sensors for click status"""
        self.select_base_object()
        bpy.ops.logic.sensor_add(
            type="PROPERTY",
            object=self.name,
            name="disabled_sensor"
        )
        self.base_object.game.sensors[-1].name = "disabled_sensor"
        click_sensor = self.base_object.game.sensors["disabled_sensor"]
        click_sensor.property = "click_status"
        click_sensor.value = "disabled"
        self.disabled_sensor = click_sensor

        self.select_base_object()
        bpy.ops.logic.sensor_add(
            type="PROPERTY",
            object=self.name,
            name="unselected_sensor"
        )
        self.base_object.game.sensors[-1].name = "unselected_sensor"
        click_sensor = self.base_object.game.sensors["unselected_sensor"]
        click_sensor.property = "click_status"
        click_sensor.value = "unselected"
        self.unselected_sensor = click_sensor

        bpy.ops.logic.sensor_add(
            type="PROPERTY",
            object=self.name,
            name="selected_sensor"
        )
        self.base_object.game.sensors[-1].name = "selected_sensor"
        click_sensor = self.base_object.game.sensors["selected_sensor"]
        click_sensor.property = "click_status"
        click_sensor.value = "selected"
        self.selected_sensor = click_sensor

        bpy.ops.logic.sensor_add(
            type="PROPERTY",
            object=self.name,
            name="activated_sensor"
        )
        self.base_object.game.sensors[-1].name = "activated_sensor"
        click_sensor = self.base_object.game.sensors["activated_sensor"]
        click_sensor.property = "click_status"
        click_sensor.value = "activated"
        self.activated_sensor = click_sensor

        return (self.disabled_sensor, self.unselected_sensor,
                self.selected_sensor, self.activated_sensor)

    def create_click_status_controllers(self):
        """Add controllers to handle when click status changes
        """
        click_object = self.select_base_object()
        bpy.ops.logic.controller_add(
            type='PYTHON',
            object=self.object_name,
            name="disabled_controller")
        controller = click_object.game.controllers["disabled_controller"]
        controller.mode = "MODULE"
        controller.module = "{}.disable_link".format(self.name)
        controller.link(sensor=self.disabled_sensor)
        self.disabled_controller = controller

        bpy.ops.logic.controller_add(
            type='PYTHON',
            object=self.object_name,
            name="unselected_controller")
        controller = click_object.game.controllers["unselected_controller"]
        controller.mode = "MODULE"
        controller.module = "{}.unselect_link".format(self.name)
        controller.link(sensor=self.unselected_sensor)
        self.unselected_controller = controller

        bpy.ops.logic.controller_add(
            type='PYTHON',
            object=self.object_name,
            name="selected_controller")
        controller = click_object.game.controllers["selected_controller"]
        controller.mode = "MODULE"
        controller.module = "{}.select_link".format(self.name)
        controller.link(sensor=self.selected_sensor)
        self.selected_controller = controller

        bpy.ops.logic.controller_add(
            type='PYTHON',
            object=self.object_name,
            name="activated_controller")
        controller = click_object.game.controllers["activated_controller"]
        controller.mode = "MODULE"
        controller.module = "{}.activate_link".format(self.name)
        controller.link(sensor=self.activated_sensor)
        self.activated_controller = controller

        return (
            self.disabled_controller, self.unselected_controller,
            self.selected_controller, self.activated_controller
        )

    def create_click_count_property(self):
        """Add property to keep track of how many times link has been
        clicked"""
        self.select_base_object()
        bpy.ops.object.game_property_new(
            type='INT',
            name='clicks'
        )
        self.base_object.game.properties["clicks"].value = 0
        return self.base_object.game.properties["clicks"]

    def create_clickable_property(self):
        """Add property to track if object is clickable

        Note: In order to make an object unclickable, this property should be
        *deleted*, not merely set to False"""
        click_object = self.select_base_object()
        if (
                (not click_object.hide_render) and
                self.base_object.game.properties['enabled']):
            bpy.ops.object.game_property_new(
                type='BOOL',
                name='clickable'
            )
            click_object.game.properties["clickable"].value = True
            return click_object.game.properties["clickable"]
        return None

    def create_blender_objects(self):
        super(BlenderClickTrigger, self).create_blender_objects()
        self.create_click_status_property()
        self.create_click_status_sensors()
        self.create_click_status_controllers()
        self.create_click_count_property()
        self.create_clickable_property()

    def generate_action_logic(self):
        action_logic = ["        # ACTION LOGIC BEGINS HERE"]
        max_time = 0
        action_index = 0
        for clicks, all_actions in self.actions.items():
            for action in all_actions:
                action_logic.extend(
                    action.generate_blender_logic(
                        click_condition=clicks,
                        index_condition=action_index,
                        offset=2)
                )
                action_index += 1
                max_time = max(max_time, action.end_time)
        if self.reset_clicks > 0:
            action_logic.extend([
                "        if own['clicks'] == {}".format(self.reset_clicks),
                "            own['clicks'] = 0"]
            )
        self.script_footer = self.script_footer.format(max_time=max_time)
        return "\n".join(action_logic)

    def generate_detection_logic(self):
        detection_logic = "\n".join([
            DISABLE_LINK_SCRIPT.format(
                disabled_color=self.disable_color
            ),
            UNSELECT_LINK_SCRIPT.format(
                enabled_color=self.enable_color
            ),
            SELECT_LINK_SCRIPT.format(
                selected_color=self.select_color
            ),
            ACTIVATE_LINK_SCRIPT.format(
                remain_enabled=self.remain_enabled
            )
        ])
        return detection_logic

    def get_actions(self):
        """Return a list of W3DActions that are controlled by this activator

        This method is necessary because of a very bad design decision which
        assigned different meanings to self.actions for different activators.
        This *will* be corrected in an upcoming refactoring but must remain for
        now in an effort to prepare for the next semester of the Writing3D
        workshop as soon as possible."""
        all_actions = []
        for clicks, actions in self.actions.items():
            all_actions.extend(actions)
        return all_actions

    @property
    def base_object(self):
        """Returns clickable object"""
        return bpy.data.objects[self.object_name]

    @property
    def name(self):
        return self.object_name

    def __init__(
            self, name, actions, object_name,
            enable_immediately=True, remain_enabled=True,
            select_color=(255, 0, 0), enable_color=(0, 128, 255),
            reset_clicks=-1):
        self.select_color = select_color
        self.reset_clicks = reset_clicks
        self.enable_color = enable_color
        self.object_name = object_name
        self.disable_color = tuple(self.base_object.color)
        self.select_color = tuple(select_color)
        super(BlenderClickTrigger, self).__init__(
            name, actions, duration=0,
            enable_immediately=enable_immediately,
            remain_enabled=remain_enabled)
        if enable_immediately:
            for i in range(len(self.enable_color)):
                self.base_object.color[i] = self.enable_color[i]
