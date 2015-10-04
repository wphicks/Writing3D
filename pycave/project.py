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
try:
    import bpy
except ImportError:
    warnings.warn(
        "Module bpy not found. Loading pycave.objects as standalone")


def clear_blender_scene():
    for obj in bpy.context.scene.objects:
        obj.select = True
    bpy.ops.object.delete()


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
            help_string="A dictionary mapping names to lists of CaveObjects"),
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
        if object_root is None:
            raise BadCaveXML("Story root has no GroupRoot node")
        for child in group_root.findall("Group"):
            new_project["objects"].append(CaveGroup.fromXML(child))
        timeline_root = project_root.find("TimelineRoot")
        if object_root is None:
            raise BadCaveXML("Story root has no ObjectRoot node")
        for child in timeline_root.findall("Timeline"):
            new_project["objects"].append(CaveTimeline.fromXML(child))
        sound_root = project_root.find("SoundRoot")
        if object_root is None:
            raise BadCaveXML("Story root has no ObjectRoot node")
        for child in sound_root.findall("Sound"):
            new_project["objects"].append(CaveSound.fromXML(child))
        trigger_root = project_root.find("EventRoot")
        if object_root is None:
            raise BadCaveXML("Story root has no ObjectRoot node")
        for child in trigger_root.findall("EventTrigger"):
            new_project["objects"].append(CaveTrigger.fromXML(child))

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
        #tree = ET.ElementTree(self.toXML())
        #tree.write(filename, encoding='utf-8', xml_declaration=True)
        with open(filename, "w") as file_:
            file_.write(self.toprettyxml())

    def blend(self):
        """Create representation of CaveProject in Blender"""
        clear_blender_scene()
        bpy.data.scenes["Scene"].game_settings.physics_gravity = 0
        bpy.data.scenes["Scene"].layers = [
            layer in (1, 3, 20) for layer in range(1, 21)]
        bpy.ops.object.camera_add(rotation=(math.pi/2, 0, 0))
        self.main_camera = bpy.context.object
        self.main_camera.layers = [layer == 1 for layer in range(1, 21)]
        self["desktop_camera_placement"].place(self.main_camera)
        for object_ in self["objects"]:
            object_.blend()
        for timeline in self["timelines"]:
            timeline.blend()
            timeline.write_blender_logic()
