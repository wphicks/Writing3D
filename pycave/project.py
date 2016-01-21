"""Tools for working with Cave projects
"""
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import warnings
import math
from .features import CaveFeature
from .placement import CavePlacement, CaveRotation, convert_to_blender_axes
from .validators import AlwaysValid, IsNumeric, IsNumericIterable
from .xml_tools import bool2text, text2tuple, attrib2bool
from .objects import CaveObject
from .sounds import CaveSound
from .timeline import CaveTimeline
from .groups import CaveGroup
from .triggers import CaveTrigger
from .errors import BadCaveXML
from .blender_scripts import MOUSE_LOOK_SCRIPT, MOVE_TOGGLE_SCRIPT
try:
    import bpy
except ImportError:
    warnings.warn(
        "Module bpy not found. Loading pycave.objects as standalone")


def clear_blender_scene():
    for obj in bpy.context.scene.objects:
        obj.select = True
    bpy.ops.object.delete()


def setup_blender_layout():
    """Put Blender interface in a convenient layout"""
    bpy.context.window.screen = bpy.data.screens["Game Logic"]
    #for area in bpy.context.window.screen.areas:
    #    if area.type == 'VIEW_3D':
    #        for space in area.spaces:
    #            space.region_3d.view_perspective = 'CAMERA'
    #            space.viewport_shade = "TEXTURED"


def add_key_movement(
        blender_object, move_name, key, direction, speed):
    """Convenience function for adding keyboard-controlled motion to
    Blender object

    :param blender_object: object to add motion to
    :param str move_name: Name for controller
    :param str key: Key used to activate motion
    :param int direction: 0, 1, 2 for x, y, z
    :param float speed: Speed of motion"""
    bpy.context.scene.objects.active = blender_object
    bpy.ops.logic.sensor_add(
        type="KEYBOARD",
        object=blender_object.name,
        name=move_name
    )
    blender_object.game.sensors[-1].name = move_name
    sensor = blender_object.game.sensors[move_name]
    sensor.key = key
    bpy.ops.logic.controller_add(
        type='LOGIC_AND',
        object=blender_object.name,
        name=move_name
    )
    blender_object.game.controllers[-1].name = move_name
    controller = blender_object.game.controllers[move_name]
    bpy.ops.logic.actuator_add(
        type="MOTION",
        object=blender_object.name,
        name=move_name
    )
    blender_object.game.actuators[-1].name = move_name
    actuator = blender_object.game.actuators[move_name]
    actuator.mode = "OBJECT_NORMAL"
    actuator.offset_location[direction] = speed
    actuator.use_local_location = True
    controller.link(actuator=actuator)
    controller.link(sensor=sensor)


class CaveProject(CaveFeature):
    """Represent entire project for display in Cave

    :param list objects: List of CaveObjects to be displayed
    :param list groups: Maps names of groups to lists of CaveObjects
    :param list timelines: List of CaveTimelines within project
    :param list sounds: List of CaveSounds within project
    :param list trigger_events: List of CaveEvents within project
    :param CavePlacement camera_placement: Initial placement of camera
    :param CavePlacement desktop_camera_placement: Initial placement of camera
    if project is run outside an actual Cave environment
    :param float far_clip: Far clip for camera (how far away from camera
    objects remain visible)
    :param tuple background: Color of background as an RGB tuple of 3 ints
    :param bool allow_movement: Allow user to navigate within project?
    :param bool allow_rotation: Allow user to rotate withing project?
    :param dict wall_placements: Dictionary mapping names of walls to
    CavePlacements specifying their position and orientation
    """

    argument_validators = {
        "objects": AlwaysValid(
            help_string="A list of CaveObjects in the project"),
        "groups": AlwaysValid(
            help_string="A list of CaveGroups in the project"),
        "timelines": AlwaysValid(
            help_string="A list of CaveTimelines in the project"),
        "sounds": AlwaysValid(
            help_string="A list of CaveSounds in the project"),
        "trigger_events": AlwaysValid(
            help_string="A list of CaveTriggers in the project"),
        "camera_placement": AlwaysValid(
            help_string="A CavePlacement object"),
        "desktop_camera_placement": AlwaysValid(
            help_string="A CavePlacement object"),
        "far_clip": IsNumeric(),
        "background": IsNumericIterable(required_length=3),
        "allow_movement": AlwaysValid("Either true or false"),
        "allow_rotation": AlwaysValid("Either true or false"),
        "wall_placements": AlwaysValid(
            "Dictionary mapping wall names to placements")
        }

    default_arguments = {
        "far_clip": 100,
        "background": (0, 0, 0),
        "allow_movement": False,
        "allow_rotation": False
        }

    def __init__(self, *args, **kwargs):
        super(CaveProject, self).__init__(*args, **kwargs)
        if "objects" not in self:
            self["objects"] = []
        if "groups" not in self:
            self["groups"] = []
        if "timelines" not in self:
            self["timelines"] = []
        if "sounds" not in self:
            self["sounds"] = []
        if "trigger_events" not in self:
            self["trigger_events"] = []
        if "camera_placement" not in self:
            self["camera_placement"] = CavePlacement(
                position=convert_to_blender_axes((0, 0, 6)))
        if "desktop_camera_placement" not in self:
            self["desktop_camera_placement"] = CavePlacement(
                position=convert_to_blender_axes((0, 0, 0)))
        # Note: Center position shift will not be used right now. This has
        # never been used to my knowledge and probably shouldn't be. Changing
        # initial camera position should be preferred.
        if "wall_placements" not in self:
            self["wall_placements"] = {
                "Center": CavePlacement(
                    position=convert_to_blender_axes((0, 0, 0)),
                    rotation=CaveRotation(
                        rotation_mode="Axis",
                        rotation_vector=convert_to_blender_axes((0, 1, 0)),
                        rotation_angle=0
                    )
                ),
                "FrontWall": CavePlacement(
                    position=convert_to_blender_axes((0, 0, -4)),
                    rotation=CaveRotation(
                        rotation_mode="LookAt",
                        rotation_vector=convert_to_blender_axes((0, 0, 0)),
                        up_vector=convert_to_blender_axes((0, 1, 0))
                    )
                ),
                "LeftWall": CavePlacement(
                    position=convert_to_blender_axes((-4, 0, 0)),
                    rotation=CaveRotation(
                        rotation_mode="LookAt",
                        rotation_vector=convert_to_blender_axes((0, 0, 0)),
                        up_vector=convert_to_blender_axes((0, 1, 0))
                    )
                ),
                "RightWall": CavePlacement(
                    position=convert_to_blender_axes((4, 0, 0)),
                    rotation=CaveRotation(
                        rotation_mode="LookAt",
                        rotation_vector=convert_to_blender_axes((0, 0, 0)),
                        up_vector=convert_to_blender_axes((0, 1, 0))
                    )
                ),
                "FloorWall": CavePlacement(
                    position=convert_to_blender_axes((0, -4, 0)),
                    rotation=CaveRotation(
                        rotation_mode="LookAt",
                        rotation_vector=convert_to_blender_axes((0, 0, 0)),
                        up_vector=convert_to_blender_axes((0, 1, 0))
                    )
                )
            }

    def toXML(self):
        """Store CaveProject as Cave XML tree
        """
        project_root = ET.Element("Story")
        object_root = ET.SubElement(project_root, "ObjectRoot")
        for object_ in self["objects"]:
            object_.toXML(object_root)
        group_root = ET.SubElement(project_root, "GroupRoot")
        for group in self["groups"]:
            group.toXML(group_root)
        timeline_root = ET.SubElement(project_root, "TimelineRoot")
        for timeline in self["timelines"]:
            timeline.toXML(timeline_root)
        sound_root = ET.SubElement(project_root, "SoundRoot")
        for sound in self["sounds"]:
            sound.toXML(sound_root)
        event_root = ET.SubElement(project_root, "EventRoot")
        for trigger in self["trigger_events"]:
            trigger.toXML(event_root)
        global_node = ET.SubElement(project_root, "Global")
        # CameraPos corresponds to position when run in Cave mode
        # CaveCameraPos corresponds to position when run in Desktop mode
        # Editorial aside: I can't even...
        camera_node = ET.SubElement(
            global_node, "CameraPos", attrib={
                "far-clip": str(self["far_clip"])})
        self["camera_placement"].toXML(camera_node)
        camera_node = ET.SubElement(
            global_node, "CaveCameraPos", attrib={
                "far-clip": str(self["far_clip"])})
        self["desktop_camera_placement"].toXML(camera_node)
        ET.SubElement(global_node, "Background", attrib={
            "color": "{}, {}, {}".format(*self["background"])})
        ET.SubElement(global_node, "WandNavigation", attrib={
            "allow-rotation": bool2text(self["allow_rotation"]),
            "allow-movement": bool2text(self["allow_movement"])
            }
        )
        wall_root = ET.SubElement(project_root, "PlacementRoot")
        for wall, placement in self["wall_placements"].items():
            place_root = placement.toXML(wall_root)
            place_root.attrib["name"] = wall

        return project_root

    @classmethod
    def fromXML(project_class, project_root):
        """Create CaveProject from Story node of Cave XML

        :param :py:class:xml.etree.ElementTree.Element project_root
        """
        new_project = project_class()
        object_root = project_root.find("ObjectRoot")
        if object_root is None:
            raise BadCaveXML("Story root has no ObjectRoot node")
        for child in object_root.findall("Object"):
            new_project["objects"].append(CaveObject.fromXML(child))
        group_root = project_root.find("GroupRoot")
        if group_root is None:
            raise BadCaveXML("Story root has no GroupRoot node")
        for child in group_root.findall("Group"):
            new_project["groups"].append(CaveGroup.fromXML(child))
        timeline_root = project_root.find("TimelineRoot")
        if object_root is None:
            raise BadCaveXML("Story root has no ObjectRoot node")
        for child in timeline_root.findall("Timeline"):
            new_project["timelines"].append(CaveTimeline.fromXML(child))
        sound_root = project_root.find("SoundRoot")
        if object_root is None:
            raise BadCaveXML("Story root has no ObjectRoot node")
        for child in sound_root.findall("Sound"):
            new_project["sounds"].append(CaveSound.fromXML(child))
        trigger_root = project_root.find("EventRoot")
        if object_root is None:
            raise BadCaveXML("Story root has no ObjectRoot node")
        for child in trigger_root.findall("EventTrigger"):
            new_project["trigger_events"].append(CaveTrigger.fromXML(child))

        global_root = project_root.find("Global")
        if global_root is None:
            raise BadCaveXML("Story root has no Global node")

        camera_node = global_root.find("CaveCameraPos")
        if camera_node is None:
            raise BadCaveXML("Global node has no CaveCameraPos child")
        if "far-clip" in camera_node.attrib:
            new_project["far_clip"] = camera_node.attrib["far-clip"]
        place_node = camera_node.find("Placement")
        if camera_node is None:
            raise BadCaveXML("CameraPos node has no Placement child")
        new_project["desktop_camera_placement"] = CavePlacement.fromXML(
            place_node)

        camera_node = global_root.find("CameraPos")
        if camera_node is None:
            raise BadCaveXML("Global node has no CameraPos child")
        if "far-clip" in camera_node.attrib:
            new_project["far_clip"] = camera_node.attrib["far-clip"]
        place_node = camera_node.find("Placement")
        if camera_node is None:
            raise BadCaveXML("CameraPos node has no Placement child")
        new_project["camera_placement"] = CavePlacement.fromXML(place_node)

        bg_node = global_root.find("Background")
        if bg_node is None:
            raise BadCaveXML("Global node has no Background child")
        if "color" in bg_node.attrib:
            new_project["background"] = text2tuple(
                bg_node.attrib["color"],
                evaluator=int
            )

        wand_node = global_root.find("WandNavigation")
        if wand_node is None:
            raise BadCaveXML("Global node has no WandNavigation child")
        new_project["allow_rotation"] = attrib2bool(
            wand_node, "allow-rotation", default=False)
        new_project["allow_movement"] = attrib2bool(
            wand_node, "allow-movement", default=False)

        wall_root = project_root.find("PlacementRoot")
        for placement in wall_root.findall("Placement"):
            try:
                wall_name = placement.attrib["name"]
            except KeyError:
                raise BadCaveXML(
                    "Placements within PlacementRoot must specify name")
            new_project["wall_placements"][
                wall_name] = CavePlacement.fromXML(placement)
        return new_project

    @classmethod
    def fromXML_file(project_class, filename):
        """Create CaveProject from XML file of given filename

        :param str filename: Filename of XML file for project
        """
        return project_class.fromXML(ET.parse(filename).getroot())

    def toprettyxml(self):
        tree = self.toXML()
        xml_string = ET.tostring(tree, encoding="unicode")
        xml_string = minidom.parseString(xml_string).toprettyxml()
        # WARNING: Need to make sure that this doesn't miss up paragraphs of
        # text
        xml_string = "\n".join(
            [line for line in xml_string.split("\n") if line.strip()])
        return xml_string

    def save_XML(self, filename):
        with open(filename, "w") as file_:
            file_.write(self.toprettyxml())

    def sort_groups(self):
        """Sort groups such that no group contains a later group"""
        new_groups = []
        while len(self["groups"]):
            group = self["groups"].pop()
            cur_len = len(new_groups)
            for i in range(cur_len):
                if group["name"] in new_groups[i]["groups"]:
                    new_groups.insert(i, group)
                    break
            if cur_len == len(new_groups):
                new_groups.append(group)
        self["groups"] = new_groups

    def setup_camera(self):
        bpy.ops.object.camera_add(rotation=(math.pi/2, 0, 0))
        bpy.data.cameras[-1].clip_end = self["far_clip"]
        self.main_camera = bpy.context.object
        self.main_camera.name = "CAMERA"
        self.main_camera.layers = [layer == 1 for layer in range(1, 21)]
        self["desktop_camera_placement"].place(self.main_camera)

    def setup_controls(self):
        bpy.context.scene.objects.active = self.main_camera
        # TODO: if self["allow_rotation"]:
        bpy.ops.logic.sensor_add(
            type="MOUSE",
            object=self.main_camera.name,
            name="Look"
        )
        self.main_camera.game.sensors[-1].name = "Look"
        sensor = self.main_camera.game.sensors["Look"]
        sensor.mouse_event = "MOVEMENT"
        bpy.ops.logic.controller_add(
            type='PYTHON',
            object=self.main_camera.name,
            name="Look")
        self.main_camera.game.controllers[-1].name = "Look"
        controller = self.main_camera.game.controllers["Look"]
        controller.mode = "MODULE"
        controller.module = "mouse.look"
        controller.link(sensor=sensor)
        bpy.ops.logic.actuator_add(
            type="MOTION",
            object=self.main_camera.name,
            name="Look_x"
        )
        self.main_camera.game.actuators[-1].name = "Look_x"
        actuator = self.main_camera.game.actuators["Look_x"]
        actuator.mode = "OBJECT_NORMAL"
        actuator.use_local_rotation = True
        controller.link(actuator=actuator)

        bpy.ops.logic.actuator_add(
            type="MOTION",
            object=self.main_camera.name,
            name="Look_y"
        )
        self.main_camera.game.actuators[-1].name = "Look_y"
        actuator = self.main_camera.game.actuators["Look_y"]
        actuator.mode = "OBJECT_NORMAL"
        actuator.use_local_rotation = False
        controller.link(actuator=actuator)

        bpy.data.texts.new("mouse.py")
        script = bpy.data.texts["mouse.py"]
        script.write(MOUSE_LOOK_SCRIPT)

        self.add_move_toggle()

        #TODO: Mouselook script and actuators
        if self["allow_movement"]:
            add_key_movement(self.main_camera, "Forward", "W", 2, -0.15)
            add_key_movement(self.main_camera, "Backward", "S", 2, 0.15)
            add_key_movement(self.main_camera, "Left", "A", 0, -0.15)
            add_key_movement(self.main_camera, "Right", "D", 0, 0.15)

    def add_move_toggle(self):
        bpy.context.scene.objects.active = self.main_camera
        bpy.ops.logic.controller_add(
            type='PYTHON',
            object=self.main_camera.name,
            name="move_toggle")
        self.main_camera.game.controllers[-1].name = "move_toggle"
        controller = self.main_camera.game.controllers["move_toggle"]
        controller.mode = "MODULE"
        controller.module = "move.move_toggle"

        bpy.ops.object.game_property_new(
            type="BOOL",
            name="toggle_movement"
        )
        self.main_camera.game.properties["toggle_movement"].value = False
        bpy.ops.logic.sensor_add(
            type="KEYBOARD",
            object=self.main_camera.name,
            name="toggle_movement"
        )
        self.main_camera.game.sensors[-1].name = "toggle_movement"
        sensor = self.main_camera.game.sensors["toggle_movement"]
        sensor.key = "TAB"

        bpy.data.texts.new("move.py")
        script = bpy.data.texts["move.py"]
        script.write(MOVE_TOGGLE_SCRIPT)

        controller.link(sensor=sensor)

    def blend(self):
        """Create representation of CaveProject in Blender"""
        clear_blender_scene()
        bpy.data.scenes["Scene"].game_settings.physics_gravity = 0
        bpy.data.scenes["Scene"].game_settings.material_mode = "GLSL"
        bpy.data.scenes["Scene"].layers = [
            layer in (1, 3, 20) for layer in range(1, 21)]
        self.setup_camera()
        self.setup_controls()
        self.sort_groups()
        bpy.data.texts.new("group_defs.py")
        bpy.data.worlds["World"].horizon_color = self["background"]
        #bpy.data.worlds["World"].ambient_color = self["background"]

        # Create Objects
        for group in self["groups"]:
            group.blend_objects()
        for group in self["groups"]:
            group.blend_groups()
        for object_ in self["objects"]:
            object_.blend()
        # TODO: Call methods to add links
        for sound in self["sounds"]:
            sound.blend()

        # Create Activators
        for timeline in self["timelines"]:
            timeline.blend()
        for trigger in self["trigger_events"]:
            trigger.blend()
        # Link game engine logic bricks for Activators
        for timeline in self["timelines"]:
            timeline.link_blender_logic()
        for object_ in self["objects"]:
            if object_["link"] is not None:
                object_["link"].link_blender_logic()
        for trigger in self["trigger_events"]:
            trigger.link_blender_logic()
        # Write any necessary game engine logic for Activators
        for timeline in self["timelines"]:
            timeline.write_blender_logic()
        for object_ in self["objects"]:
            if object_["link"] is not None:
                object_["link"].write_blender_logic()
        for trigger in self["trigger_events"]:
            trigger.write_blender_logic()
        setup_blender_layout()
