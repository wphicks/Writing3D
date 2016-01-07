"""A collection of scripts to be imported wholesale into Blender
projects"""

MOUSE_LOOK_SCRIPT = """
import bge
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
    else:
        mouse_pos = sensor.position
        offset = [mouse_pos[i] - center[i] for i in range(2)]

        actuator_y.dRot = [0, 0, -offset[0]*0.001]
        actuator_y.useLocalDRot = False

        actuator_x.dRot = [offset[1]*-0.001, 0, 0]
        actuator_x.useLocalDRot = True

        cont.activate(actuator_x)
        cont.activate(actuator_y)
    bge.render.setMousePosition(*center)"""
