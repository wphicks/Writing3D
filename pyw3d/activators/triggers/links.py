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
LOGGER = logging.getLogger("pyw3d")
from .triggers import BlenderTrigger
from pyw3d.errors import EBKAC
from pyw3d.names import generate_link_name
try:
    import bpy
except ImportError:
    LOGGER.debug(
        "Module bpy not found. Loading pyw3d.timeline as standalone")


class BlenderClickTrigger(BlenderTrigger):
    """Activator based on mouseclick on objects in virtual space

    :param str object_name: The name of the clickable object
    """

    # TODO: Change color when enabled

    def select_target_object(self):
        """Select the clickable object for modification"""
        click_object = bpy.data.objects[self.object_name]
        bpy.context.scene.objects.active = click_object
        return click_object

    @property
    def name(self):
        return generate_link_name(self.name_string)

    def create_primed_property(self):
        """Add property to track if mousedown is followed by mouseup"""
        click_object = self.select_target_object()
        bpy.ops.object.game_property_new(
            type='BOOL',
            name='click_primed'
        )
        click_object.game.properties["click_primed"].value = False
        return click_object.game.properties["click_primed"]

    def create_click_property(self):
        """Add property to keep track of how many times link has been
        clicked"""
        self.select_base_object()
        bpy.ops.object.game_property_new(
            type='INT',
            name='clicks'
        )
        self.base_object.game.properties["clicks"].value = 0
        return self.base_object.game.properties["clicks"]

    def create_detection_controller(self):
        """Add controller for detecting mouseclick and mouseover

        This controller also changes the color of the selected object on
        mouse-down events."""
        click_object = self.select_target_object()
        bpy.ops.logic.controller_add(
            type='PYTHON',
            object=self.object_name,
            name=self.name)
        controller = click_object.game.controllers[self.name]
        controller.mode = "MODULE"
        controller.module = "{}.detect_event".format(self.name)
        self.detect_controller = controller
        return self.detect_controller

    def create_detection_sensors(self):
        """Add mouseclick and mouseover sensors to clickable object"""
        click_object = self.select_target_object()
        if "mouse_click" not in click_object.game.sensors:
            bpy.ops.logic.sensor_add(
                type="MOUSE",
                object=self.object_name,
                name="mouse_click"
            )
            click_object.game.sensors[-1].name = "mouse_click"
            self.click_sensor = click_object.game.sensors["mouse_click"]
            self.click_sensor.mouse_event = "LEFTCLICK"
        if "mouse_over" not in click_object.game.sensors:
            bpy.ops.logic.sensor_add(
                type="MOUSE",
                object=self.object_name,
                name="mouse_over"
            )
            click_object.game.sensors[-1].name = "mouse_over"
            self.over_sensor = click_object.game.sensors["mouse_over"]
            self.over_sensor.mouse_event = "MOUSEOVER"
            self.over_sensor.use_pulse_true_level = True
        return (self.click_sensor, self.over_sensor)

    def link_detection_bricks(self):
        """Link necessary logic bricks for click detections

        :raises EBKAC: if necessary controller and sensors do not
        exist
        """
        try:
            self.detect_controller.link(sensor=self.click_sensor)
            self.detect_controller.link(sensor=self.over_sensor)
        except AttributeError:
            raise EBKAC(
                "Detection sensors and controller must be created before they "
                "can be linked")
        return self.detect_controller

    def generate_detection_logic(self):
        """Add a function to Python control script to handle mouse click events
        """
        detection_logic = [
            "\ndef detect_event(cont):",
            "    scene = bge.logic.getCurrentScene()",
            "    own = cont.owner",
            "    mouse_click = cont.sensors['mouse_click']",
            "    mouse_over = own.sensors['mouse_over']",
            "    trigger = scene.objects['{}']".format(self.name),
            "    select_color = {}".format(str(
                [coord / 255. for coord in self.select_color])),
            "    enable_color = {}".format(str(
                [coord / 255. for coord in self.enable_color])),
            "    if (mouse_over.positive):",
            "        W3D_LOG.debug('Mouse over {}'.format(own.name))",
            "        W3D_LOG.debug('{} over visibility: {}'.format(own.name, own.visible))",
            "        W3D_LOG.debug('{} over enabled: {}'.format(own.name, trigger['enabled']))",
            "    if (mouse_click.positive and trigger['enabled']):",
            "        W3D_LOG.debug('Mouse click {}'.format(own.name))",
            "        W3D_LOG.debug('{} click visibility: {}'.format(own.name, own.visible))",
            "        W3D_LOG.debug('{} click enabled: {}'.format(own.name, trigger['enabled']))",
            "    if (",
            "            mouse_click.positive and mouse_over.positive",
            "            and own.visible):",
            "        W3D_LOG.debug('Click registered')",
            "        if 'old_color' not in own or own['old_color'] is None:",
            "            own['old_color'] = [coord for coord in own.color]",
            "        new_color = own.color",
            "        for i in range(len(select_color)):",
            "            new_color[i] = select_color[i]",
            "        own['click_primed'] = True",
            "    else:",
            "        if (",
            "                not mouse_click.positive and mouse_over.positive",
            "                and trigger['enabled'] and own['click_primed']):",
            "            if trigger['status'] == 'Stop':",
            "                trigger['status'] = 'Start'",
            "            trigger['clicks'] += 1",
            "            own.color = own['old_color']",
            "            own['old_color'] = None",
            "        own['click_primed'] = False"
        ]
        detection_logic = "\n".join(detection_logic)
        return detection_logic

    def create_blender_objects(self):
        super(BlenderClickTrigger, self).create_blender_objects()
        self.create_click_property()
        self.create_primed_property()
        self.create_detection_controller()
        self.create_detection_sensors()

    def link_logic_bricks(self):
        super(BlenderClickTrigger, self).link_logic_bricks()
        self.link_detection_bricks()

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

    def __init__(
            self, name, actions, object_name,
            enable_immediately=True, remain_enabled=True,
            select_color=(255, 0, 0), enable_color=(0, 128, 255),
            reset_clicks=-1):
        super(BlenderClickTrigger, self).__init__(
            name, actions, duration=0,
            enable_immediately=enable_immediately,
            remain_enabled=remain_enabled)
        self.object_name = object_name
        self.select_color = select_color
        self.reset_clicks = reset_clicks
        self.enable_color = enable_color
