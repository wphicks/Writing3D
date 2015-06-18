"""Tools for working with Cave projects
"""
from features import CaveFeature
from placement import CavePlacement
from validators import CheckContainedType
from objects import CaveObject


class CaveProject(CaveFeature):
    """Represent entire project for display in Cave

    :param list objects: List of CaveObjects to be displayed
    :param dict groups: Maps names of groups to lists of CaveObjects
    :param list timelines: List of CaveTimelines within project
    :param list sounds: List of CaveSounds within project
    :param list trigger_events: List of CaveEvents within project
    :param CavePlacement camera_position: Initial placement of camera
    :param float far_clip: Far clip for camera (how far away from camera
    objects remain visible)
    :param tuple background: Color of background as an RGB tuple of 3 ints
    :param bool allow_movement: Allow user to navigate within project?
    :param bool allow_rotation: Allow user to rotate withing project?
    """
    # TODO: argument_validators
    argument_validators = {
        "objects": CheckContainedType(CaveObject),
        "groups": {},
        "timelines": [],
        "sounds": [],
        "trigger_events": [],
        "camera_position": CavePlacement(),
        "far_clip": 100.0,
        "background": (0, 0, 0),
        "allow_movement": False,
        "allow_rotation": False
        }
    default_arguments = {
        "objects": [],
        "groups": {},
        "timelines": [],
        "sounds": [],
        "trigger_events": [],
        "camera_position": CavePlacement(),
        "far_clip": 100.0,
        "background": (0, 0, 0),
        "allow_movement": False,
        "allow_rotation": False
        }

    def toXML(self):
        """Store CaveProject as Cave XML tree
        """
        CaveFeature.toXML(self, None)  # TODO: Replace this

    @classmethod
    def fromXML(project_root):
        """Create CaveProject from Story node of Cave XML

        :param :py:class:xml.etree.ElementTree.Element project_root
        """
        return CaveFeature.fromXML(project_root)  # TODO: Replace this

    def blend(self):
        """Create representation of CaveProject in Blender"""
        raise NotImplementedError  # TODO
