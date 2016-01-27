"""Tools for working with timelines in Cave projects
"""
import xml.etree.ElementTree as ET
from collections import MutableSequence
from .features import CaveFeature
from .actions import CaveAction
from .validators import AlwaysValid, IsBoolean, ValidPyString
from .errors import ConsistencyError, BadCaveXML
from .xml_tools import bool2text, text2bool
from .activators import BlenderTimeline
from .errors import EBKAC


class SortedList(MutableSequence):
    """A list that is guaranteed to remain sorted

    :param init_list: Initial list of elements (not necessarily sorted)
    :param sort_key: Key function for sorting"""
    def __init__(self, init_list=[], sort_key=None):
        self.sort_key = sort_key
        self._data = init_list
        self.sort()

    def __setitem__(self, index, value):
        self._data.__setitem__(index, value)
        self.sort()

    def __delitem__(self, index):
        del self._data[index]

    def __len__(self):
        return len(self._data)

    def __getitem__(self, index):
        return self._data[index]

    def insert(self, index, new_item):
        self._data.insert(index, new_item)

    def add(self, new_item):
        """Add new_item to list, maintaining proper ordering"""
        for index, item in enumerate(self):
            if self.sort_key is None:
                if new_item < item:
                    self._data.insert(index, new_item)
                    return
            else:
                if self.sort_key(new_item) < self.sort_key(item):
                    self._data.insert(index, new_item)
                    return
        self._data.insert(len(self), new_item)

    def sort(self):
        self._data.sort(key=self.sort_key)

    def append(self, value):
        self.add(value)

    def extend(self, value_list):
        for value in value_list:
            self.add(value)

    def reverse(self):
        raise NotImplementedError("Cannot reverse a SortedList")


class CaveTimeline(CaveFeature):
    """Represent timeline for choreography of actions in the Cave

    :param str name: Name of timeline
    :param bool start_immediately: Start timeline when project starts?
    :param list actions: A list of two-element tuples specifying (start time
    for action, CaveAction)
    """
    argument_validators = {
        "name": ValidPyString(),
        "start_immediately": IsBoolean(),
        "actions": AlwaysValid(
            help_string="A list of (float, CaveAction) tuples")
        }
    default_arguments = {
        "start_immediately": True
        }

    def __init__(self, *args, **kwargs):
        super(CaveTimeline, self).__init__(*args, **kwargs)
        if "actions" not in self:
            self["actions"] = SortedList()
        else:
            self["actions"] = SortedList(self["actions"])

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
    def fromXML(timeline_class, timeline_root):
        """Create CaveTimeline from Timeline node of Cave XML

        :param :py:class:xml.etree.ElementTree.Element timeline_root
        """
        new_timeline = timeline_class()
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
            except (KeyError, ValueError):
                raise BadCaveXML(
                    "TimedActions node must specify numeric seconds-time "
                    "attribute")
            for child in timed_action.getchildren():
                new_timeline["actions"].add(
                    (action_time, CaveAction.fromXML(child)))

        return new_timeline

    def blend(self):
        """Create Blender object to implement CaveTimeline"""
        self.activator = BlenderTimeline(
            self["name"], self["actions"],
            start_immediately=self["start_immediately"])
        self.activator.create_blender_objects()
        return self.activator.base_object

    def link_blender_logic(self):
        """Link BGE logic bricks for this CaveTimeline"""
        try:
            self.activator.link_logic_bricks()
        except AttributeError:
            raise EBKAC(
                "blend() must be called before link_blender_logic()")

    def write_blender_logic(self):
        """Write any necessary game engine logic for this CaveTimeline"""
        try:
            self.activator.write_python_logic()
        except AttributeError:
            raise EBKAC(
                "blend() must be called before write_blender_logic()")
