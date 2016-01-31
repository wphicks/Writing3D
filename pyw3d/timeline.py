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

"""Tools for working with timelines in W3D projects
"""
import xml.etree.ElementTree as ET
from collections import MutableSequence
from .features import W3DFeature
from .actions import W3DAction
from .validators import AlwaysValid, IsBoolean, ValidPyString
from .errors import ConsistencyError, BadW3DXML
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


class W3DTimeline(W3DFeature):
    """Represent timeline for choreography of actions in the W3D

    :param str name: Name of timeline
    :param bool start_immediately: Start timeline when project starts?
    :param list actions: A list of two-element tuples specifying (start time
    for action, W3DAction)
    """
    argument_validators = {
        "name": ValidPyString(),
        "start_immediately": IsBoolean(),
        "actions": AlwaysValid(
            help_string="A list of (float, W3DAction) tuples")
        }
    default_arguments = {
        "start_immediately": True
        }

    def __init__(self, *args, **kwargs):
        super(W3DTimeline, self).__init__(*args, **kwargs)
        if "actions" not in self:
            self["actions"] = SortedList()
        else:
            self["actions"] = SortedList(self["actions"])

    def toXML(self, all_timelines_root):
        """Store W3DTimeline as Timeline node within TimelineRoot node
        """
        try:
            timeline_attribs = {"name": self["name"]}
        except KeyError:
            raise ConsistencyError("W3DTimeline must specify a name")
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
        """Create W3DTimeline from Timeline node of W3D XML

        :param :py:class:xml.etree.ElementTree.Element timeline_root
        """
        new_timeline = timeline_class()
        try:
            new_timeline["name"] = timeline_root.attrib["name"]
        except KeyError:
            raise BadW3DXML(
                "Timeline node must specify name attribute")
        if "start-immediately" in timeline_root.attrib:
            new_timeline["start_immediately"] = text2bool(timeline_root.attrib[
                "start-immediately"])
        for timed_action in timeline_root.findall("TimedActions"):
            try:
                action_time = float(timed_action.attrib["seconds-time"])
            except (KeyError, ValueError):
                raise BadW3DXML(
                    "TimedActions node must specify numeric seconds-time "
                    "attribute")
            for child in timed_action.getchildren():
                new_timeline["actions"].add(
                    (action_time, W3DAction.fromXML(child)))

        return new_timeline

    def blend(self):
        """Create Blender object to implement W3DTimeline"""
        self.activator = BlenderTimeline(
            self["name"], self["actions"],
            start_immediately=self["start_immediately"])
        self.activator.create_blender_objects()
        return self.activator.base_object

    def link_blender_logic(self):
        """Link BGE logic bricks for this W3DTimeline"""
        try:
            self.activator.link_logic_bricks()
        except AttributeError:
            raise EBKAC(
                "blend() must be called before link_blender_logic()")

    def write_blender_logic(self):
        """Write any necessary game engine logic for this W3DTimeline"""
        try:
            self.activator.write_python_logic()
        except AttributeError:
            raise EBKAC(
                "blend() must be called before write_blender_logic()")
