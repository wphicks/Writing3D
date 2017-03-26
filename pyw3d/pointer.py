#!/usr/bin/env python
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

"""Handle pointer interface (mouse, wand, etc.) for project"""

import logging
from .blender_scripts import MOUSE_LOOK_SCRIPT
LOGGER = logging.getLogger("pyw3d")
try:
    import bpy
except ImportError:
    LOGGER.info(
        "Module bpy not found. Loading pyw3d.pointer as standalone")


def setup_mouselook(project):
    bpy.context.scene.objects.active = project.main_camera
    bpy.ops.logic.sensor_add(
        type="MOUSE",
        object=project.main_camera.name,
        name="Look"
    )
    project.main_camera.game.sensors[-1].name = "Look"
    sensor = project.main_camera.game.sensors["Look"]
    sensor.mouse_event = "MOVEMENT"
    bpy.ops.logic.controller_add(
        type='PYTHON',
        object=project.main_camera.name,
        name="Look")
    project.main_camera.game.controllers[-1].name = "Look"
    controller = project.main_camera.game.controllers["Look"]
    controller.mode = "MODULE"
    controller.module = "mouse.look"
    controller.link(sensor=sensor)
    bpy.ops.logic.actuator_add(
        type="MOTION",
        object=project.main_camera.name,
        name="Look_x"
    )
    project.main_camera.game.actuators[-1].name = "Look_x"
    actuator = project.main_camera.game.actuators["Look_x"]
    actuator.mode = "OBJECT_NORMAL"
    actuator.use_local_rotation = True
    controller.link(actuator=actuator)

    bpy.ops.logic.actuator_add(
        type="MOTION",
        object=project.main_camera.name,
        name="Look_y"
    )
    project.main_camera.game.actuators[-1].name = "Look_y"
    actuator = project.main_camera.game.actuators["Look_y"]
    actuator.mode = "OBJECT_NORMAL"
    actuator.use_local_rotation = False
    controller.link(actuator=actuator)

    bpy.data.texts.new("mouse.py")
    script = bpy.data.texts["mouse.py"]
    script.write(MOUSE_LOOK_SCRIPT)

    return sensor


def setup_click(project):
    bpy.ops.logic.sensor_add(
        type="MOUSE",
        object=project.main_camera,
        name="mouse_click"
    )
    project.main_camera.game.sensors[-1].name = "Click"
    sensor = project.main_camera.game.sensors["Click"]
    sensor.mouse_event = "LEFTCLICK"
