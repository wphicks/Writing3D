"""Tools for working with Cave projects
"""
from features import CaveFeature


class CaveProject(CaveFeature):
    """Represent entire project for display in Cave

    :param list objects: List of CaveObjects to be displayed
    :param dict groups: Maps names of groups to lists of CaveObjects
    :param list timelines: List of CaveTimelines within project
    :param list sounds: List of CaveSounds within project
    :param list trigger_events: List of CaveEvents within project
    """
    # TODO: argument_validators
    # TODO: default_arguments

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
