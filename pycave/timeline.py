"""Tools for working with timelines in Cave projects
"""
from features import CaveFeature


class CaveTimeline(CaveFeature):
    """Represent timeline for choreography of actions in the Cave

    :param str name: Name of timeline
    :param bool start_immediately: Start timeline when project starts?
    :param list actions: List of CaveActions in timeline
    """
    # TODO: argument_validators
    # TODO: default_arguments

    def toXML(self, all_timelines_root):
        """Store CaveTimeline as Timeline node within TimelineRoot node
        """
        CaveFeature.toXML(self, all_timelines_root)  # TODO: Replace this

    @classmethod
    def fromXML(timeline_root):
        """Create CaveTimeline from Timeline node of Cave XML

        :param :py:class:xml.etree.ElementTree.Element timeline_root
        """
        return CaveFeature.fromXML(timeline_root)  # TODO: Replace this

    def blend(self):
        """Create representation of CaveTimeline in Blender"""
        raise NotImplementedError  # TODO
