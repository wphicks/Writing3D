"""Tools for working with timelines in Cave projects
"""
from features import CaveFeature
from validators import AlwaysValid
from errors import ConsistencyError, BadCaveXML
from xmltools import bool2text, text2bool
import xml.etree.ElementTree as ET


class SortedList(list):
    """A list that is guaranteed to remain sorted
    
    :param compare: Comparison function for sorting"""
    def __init__(self, init_list=None, compare=None):
        self.compare = compare
        super(SortedList, self).__init__(init_list)
        self.sort(cmp=self.compare)

    def add(self, new_item):
        for index, item in enumerate(self):
            if self.compare(


class CaveTimeline(CaveFeature):
    """Represent timeline for choreography of actions in the Cave

    :param str name: Name of timeline
    :param bool start_immediately: Start timeline when project starts?
    :param list actions: A list of two-element tuples specifying (start time
    for action, CaveAction)
    """
    argument_validators = {
        "name": AlwaysValid(
            help_string="A string specifying a unique name for this sound"),
        "start_immediately": AlwaysValid(help_string="Either true or false"),
        "actions": AlwaysValid(
            help_string="A dictionary mapping CaveActions to floats")
        }
    default_arguments = {
        "start_immediately": True,
        "actions": SortedList()
        }

    def toXML(self, all_timelines_root):
        """Store CaveTimeline as Timeline node within TimelineRoot node
        """
        try:
            timeline_attribs = {"name": self["name"]}
        except KeyError:
            raise ConsistencyError("CaveTimeline must specify a name")
        if "start_immediately" in self:
            timeline_attribs["start-immediately"] = bool2text(
                self["start_immediately"])
        timeline_root = ET.SubElement(
            all_timelines_root, "Timeline", attrib=timeline_attribs)
        for time, action in self["actions"]:
            action_root = ET.SubElement(
                timeline_root, "TimedActions",
                attrib={"seconds-time": str(time)}
                )
            action.toXML(action_root)
        return timeline_root

    @classmethod
    def fromXML(timeline_root):
        """Create CaveTimeline from Timeline node of Cave XML

        :param :py:class:xml.etree.ElementTree.Element timeline_root
        """
        new_timeline = CaveTimeline()
        try:
            new_timeline["name"] = timeline_root.attrib["name"]
        except KeyError:
            raise BadCaveXML(
                "Timeline node must specify name attribute")
        if "start-immediately" in timeline_root.attrib:
            new_timeline["start_immediately"] = text2bool(timeline_root.attrib[
                "start-immediately"])
        for timed_action in timeline_root.findall("TimedActions"):
            try:
                action_time = float(timed_action.attrib["seconds-time"])
            except KeyError, ValueError:
                raise BadCaveXML(
                    "TimedActions node must specify numeric seconds-time "
                    "attribute")
            for child in timed_action.getchildren():
                new_timeline["actions"].add(
                    (action_time, CaveAction.fromXML(child))

        return new_timeline

    def blend(self):
        """Create representation of CaveTimeline in Blender"""
        raise NotImplementedError  # TODO
