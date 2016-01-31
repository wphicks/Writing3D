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

"""A collection of scripts to be imported wholesale into Blender
projects"""

MOUSE_LOOK_SCRIPT = """
import bge
import random
import mathutils
def look(cont):
    sensor = cont.sensors["Look"]
    actuator_x = cont.actuators["Look_x"]
    actuator_y = cont.actuators["Look_y"]
    center = (
        bge.render.getWindowWidth()//2,
        bge.render.getWindowHeight()//2)
    if not "look_initialized" in cont.owner:
        cont.owner["look_initialized"] = True
        bge.render.showMouse(not cont.owner["toggle_movement"])
        bge.render.setMousePosition(*center)
    elif cont.owner["toggle_movement"]:
        mouse_pos = sensor.position
        offset = [mouse_pos[i] - center[i] for i in range(2)]

        actuator_y.dRot = [0, 0, -offset[0]*0.001]
        actuator_y.useLocalDRot = False

        actuator_x.dRot = [offset[1]*-0.001, 0, 0]
        actuator_x.useLocalDRot = True

        cont.activate(actuator_x)
        cont.activate(actuator_y)
        bge.render.setMousePosition(*center)"""

MOVE_TOGGLE_SCRIPT = """
import bge
import mathutils
def move_toggle(cont):
    toggle_sensor = cont.sensors["toggle_movement"]
    if toggle_sensor.positive:
        cont.owner["toggle_movement"] = not cont.owner["toggle_movement"]
        bge.render.showMouse(not cont.owner["toggle_movement"])
"""
