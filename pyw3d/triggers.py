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

"""Tools for working with particular W3D events that can trigger actions

Here, triggers are any events within the W3D that can be used to start another
action. For example, when the viewer reaches a particular location, a timeline
can be started."""
import xml.etree.ElementTree as ET
from .features import W3DFeature
from .validators import IsNumeric, ListValidator, \
    OptionValidator, IsBoolean, ValidPyString, \
    FeatureValidator, ReferenceValidator
from .errors import ConsistencyError, BadW3DXML, InvalidArgument, \
    EBKAC
from .xml_tools import bool2text, text2tuple, text2bool
from .activators import BlenderTrigger, BlenderPositionTrigger, \
    BlenderPointTrigger, BlenderDirectionTrigger, BlenderLookObjectTrigger, \
    BlenderObjectPositionTrigger
from .actions import W3DAction


class W3DTrigger(W3DFeature):
    """Store data on a trigger event in the cave

    :ivar base_trigger: A trigger object wrapped by this trigger (see
    __setitem__ and __getitem__ implementation for details)
    """
    def __init__(self, *args, **kwargs):
        self.base_trigger = BareTrigger()
        super(W3DTrigger, self).__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        try:
            return super(W3DTrigger, self).__setitem__(key, value)
        except InvalidArgument as bad_key_error:
            try:
                self.base_trigger.__setitem__(key, value)
            except InvalidArgument:
                raise bad_key_error

    def __getitem__(self, key):
        try:
            return super(W3DTrigger, self).__getitem__(key)
        except KeyError as not_found_error:
            try:
                return self.base_trigger.__getitem__(key)
            except KeyError:
                raise not_found_error

    @staticmethod
    def fromXML(trigger_root):
        """Create W3DTrigger from EventTrigger node

        :param :py:class:xml.etree.ElementTree.Element trigger_root
        """
        tag_class_dict = {
            "HeadTrack": HeadTrackTrigger,
            "MoveTrack": MovementTrigger
        }
        for tag, trigger_class in tag_class_dict.items():
            if trigger_root.find(tag) is not None:
                return trigger_class.fromXML(trigger_root)
        return BareTrigger.fromXML(trigger_root)

    def blend(self):
        """Create representation of W3DTrigger in Blender"""
        self.activator = BlenderTrigger(
            self["name"],
            self["actions"],
            enable_immediately=self["enabled"],
            remain_enabled=self["remain_enabled"])
        self.activator.create_blender_objects()
        return self.activator.base_object

    def link_blender_logic(self):
        """Link BGE logic bricks for this W3DTrigger"""
        try:
            self.activator.link_logic_bricks()
        except AttributeError:
            raise EBKAC(
                "blend() must be called before link_blender_logic()")

    def write_blender_logic(self):
        try:
            self.activator.write_python_logic()
        except AttributeError:
            raise EBKAC(
                "blend() must be called before write_blender_logic()")


class BareTrigger(W3DFeature):
    """A trigger specifying only base information common to other triggers

    :param str name: Unique name for this trigger
    :param bool enabled: Is this trigger enabled?
    :param bool remain-enabled: Should this remain enabled after it is
    triggered?
    :param float duration: TODO: Clarify
    :param actions: List of W3DActions to be triggered
    """
    argument_validators = {
        "name": ValidPyString(),
        "enabled": IsBoolean(),
        "remain_enabled": IsBoolean(),
        "duration": IsNumeric(min_value=0),
        "actions": ListValidator(
            FeatureValidator(W3DAction),
            help_string="A list of W3DActions"
        )}

    default_arguments = {
        "enabled": True,
        "remain_enabled": True,
        "duration": 0,
        }

    def __init__(self, *args, **kwargs):
        super(BareTrigger, self).__init__(*args, **kwargs)
        if "actions" not in self:
            self["actions"] = []

    def toXML(self, all_triggers_root):
        """Store BareTrigger as EventTrigger node within EventRoot node

        :param :py:class:xml.etree.ElementTree.Element all_triggers_root
        """
        try:
            xml_attrib = {"name": self["name"]}
        except KeyError:
            raise ConsistencyError("W3DTrigger must specify name")
        if not self.is_default("enabled"):
            xml_attrib["enabled"] = bool2text(self["enabled"])
        if not self.is_default("remain_enabled"):
            xml_attrib["remain-enabled"] = bool2text(self["remain_enabled"])
        if not self.is_default("duration"):
            xml_attrib["duration"] = str(self["duration"])
        trigger_root = ET.SubElement(
            all_triggers_root, "EventTrigger", attrib=xml_attrib)
        action_root = ET.SubElement(trigger_root, "Actions")
        for action in self["actions"]:
            action.toXML(action_root)
        return trigger_root

    @classmethod
    def fromXML(trigger_class, trigger_root):
        new_trigger = trigger_class()
        try:
            new_trigger["name"] = trigger_root.attrib["name"]
        except KeyError:
            raise BadW3DXML("EventTrigger must specify name attribute")
        xml_tags = {
            "enabled": "enabled", "remain_enabled": "remain-enabled"}
        for key, tag in xml_tags.items():
            if tag in trigger_root.attrib:
                new_trigger[key] = bool(trigger_root.attrib[tag])
        if "duration" in trigger_root.attrib:
            new_trigger["duration"] = float(trigger_root.attrib["duration"])
        action_root = trigger_root.find("Actions")
        if action_root is not None:
            for child in action_root.getchildren():
                new_trigger["actions"].append(W3DAction.fromXML(child))
        return new_trigger


class HeadTrackTrigger(W3DTrigger):
    """For triggers based on head-tracking of W3D user
    """
    @classmethod
    def fromXML(trigger_class, trigger_root):
        """Create HeadTrackTrigger from EventTrigger node

        :param :py:class:xml.etree.ElementTree.Element trigger_root
        """
        head_node = trigger_root.find("HeadTrack")
        direction_node = head_node.find("Direction")
        if direction_node.find("None") is not None:
            return HeadPositionTrigger.fromXML(trigger_root)
        elif direction_node.find("PointTarget") is not None:
            return LookAtPoint.fromXML(trigger_root)
        elif direction_node.find("DirectionTarget") is not None:
            return LookAtDirection.fromXML(trigger_root)
        elif direction_node.find("ObjectTarget") is not None:
            return LookAtObject.fromXML(trigger_root)
        else:
            raise BadW3DXML(
                "HeadTrack node must contain None, PointTarget,"
                " DirectionTarget, or ObjectTarget child node")


class EventBox(W3DFeature):
    """For triggers based on movement into or out of box

    :param str direction: One of "Inside" or "Outside" depending on whether
    trigger occurs for movement into or out of box
    :param bool ignore_y: Should y-direction be ignored in checking box? In
    other words, vertical position in W3D doesn't matter when this is set to
    true.
    :param tuple corner1: First corner specifiying box location
    :param tuple corner2: Second corner specifying box location
    """

    argument_validators = {
        "direction": OptionValidator("Inside", "Outside"),
        "ignore_y": IsBoolean(),
        "corner1": ListValidator(
            IsNumeric(),
            required_length=3,
            help_string="Coordinates of box corner"
        ),
        "corner2": ListValidator(
            IsNumeric(),
            required_length=3,
            help_string="Coordinates of box corner"
        )}

    default_arguments = {
        "ignore_y": True
        }

    def toXML(self, parent_root):
        """Store EventBox as Box node within one of several possible node types

        :param :py:class:xml.etree.ElementTree.Element parent_root
        """
        try:
            xml_attrib = {
                "corner1": "({}, {}, {})".format(*self["corner1"]),
                "corner2": "({}, {}, {})".format(*self["corner2"]),
                }
        except KeyError:
            raise ConsistencyError("EventBox must specify corner1 and corner2")
        if not self.is_default("ignore_y"):
            xml_attrib["ignore-y"] = bool2text(self["ignore_y"])
        box_node = ET.SubElement(parent_root, "Box", attrib=xml_attrib)
        node = ET.SubElement(box_node, "Movement")
        try:
            ET.SubElement(node, self["direction"])
        except KeyError:
            raise ConsistencyError("EventBox must specify direction")
        return box_node

    @classmethod
    def fromXML(box_class, box_root):
        """Create EventBox from Box node

        :param :py:class:xml.etree.ElementTree.Element box_root
        """
        new_box = box_class()
        for corner in ("corner1", "corner2"):
            try:
                new_box[corner] = text2tuple(
                    box_root.attrib[corner], evaluator=float)
            except KeyError:
                raise BadW3DXML(
                    'Box node must specify attribute {}'.format(corner))
        if "ignore-y" in box_root.attrib:
            new_box["ignore_y"] = text2bool(box_root.attrib["ignore-y"])

        movement_node = box_root.find("Movement")
        if movement_node is None:
            raise BadW3DXML('Box node must contain Movement child')
        direction_node = movement_node.find("Inside")
        if direction_node is None:
            direction_node = movement_node.find("Outside")
            if direction_node is None:
                raise BadW3DXML(
                    'Movement node must contain Inside or Outside child')
            new_box['direction'] = "Outside"
        else:
            new_box['direction'] = "Inside"

        return new_box


class HeadPositionTrigger(HeadTrackTrigger):
    """For triggers based on position of user in W3D

    :param EventBox box: Used to trigger events when user's head moves into or
    out of specified box. If None, trigger can occur anywhere in W3D
    """

    argument_validators = {
        "box": FeatureValidator(
            EventBox,
            help_string="Movement into or out of a box to trigger action?")
    }

    default_arguments = {
        "box": None
    }

    def toXML(self, all_triggers_root):
        """Store HeadPositionTrigger as EventTrigger node within EventRoot node

        :param :py:class:xml.etree.ElementTree.Element all_triggers_root
        """
        trigger_root = self.base_trigger.toXML(all_triggers_root)
        head_node = ET.SubElement(trigger_root, "HeadTrack")
        position_node = ET.SubElement(head_node, "Position")
        if self["box"] is None:
            ET.SubElement(position_node, "Anywhere")
        else:
            self["box"].toXML(position_node)
        direction_node = ET.SubElement(head_node, "Direction")
        ET.SubElement(direction_node, "None")
        return trigger_root

    @classmethod
    def fromXML(trigger_class, trigger_root):
        """Create HeadPositionTrigger from EventTrigger node

        :param :py:class:xml.etree.ElementTree.Element trigger_root
        """
        new_trigger = trigger_class()
        new_trigger.base_trigger = BareTrigger.fromXML(trigger_root)
        head_node = trigger_root.find("HeadTrack")
        position_node = head_node.find("Position")
        box_node = position_node.find("Box")
        if box_node is not None:
            new_trigger["box"] = EventBox.fromXML(box_node)
        return new_trigger

    def blend(self):
        """Create representation of W3DTrigger in Blender"""
        self.activator = BlenderPositionTrigger(
            self["name"],
            self["actions"],
            self["box"],
            enable_immediately=self["enabled"],
            remain_enabled=self["remain_enabled"])
        self.activator.create_blender_objects()
        return self.activator.base_object


class LookAtPoint(HeadTrackTrigger):
    """For event triggers based on user looking at a point

    :param tuple point: The point to look at
    :param float angle: TODO: clarify (WARNING: currently does nothing)"""
    # TODO: Do we need to allow localization in box?

    argument_validators = {
        "point": ListValidator(
            IsNumeric(), required_length=3,
            help_string="Coordinates of point to look at"),
        "angle": IsNumeric()
    }
    default_arguments = {
        "angle": 30
    }

    def toXML(self, all_triggers_root):
        """Store LookAtPoint as EventTrigger node within EventRoot node

        :param :py:class:xml.etree.ElementTree.Element all_triggers_root
        """
        trigger_root = self.base_trigger.toXML(all_triggers_root)
        node = ET.SubElement(trigger_root, "HeadTrack")
        position_node = ET.SubElement(node, "Position")
        ET.SubElement(position_node, "Anywhere")
        node = ET.SubElement(node, "Direction")
        try:
            xml_attrib = {"point": "({}, {}, {})".format(*self["point"])}
        except KeyError:
            raise ConsistencyError("LookAtPoint must specify point")
        if not self.is_default("angle"):
            xml_attrib["angle"] = str(self["angle"])
        ET.SubElement(node, "PointTarget", attrib=xml_attrib)
        return trigger_root

    @classmethod
    def fromXML(trigger_class, trigger_root):
        """Create LookAtPoint from EventTrigger node

        :param :py:class:xml.etree.ElementTree.Element target_root
        """
        new_trigger = trigger_class()
        new_trigger.base_trigger = HeadPositionTrigger.fromXML(trigger_root)
        node = trigger_root.find("HeadTrack")
        node = node.find("Direction")
        node = node.find("PointTarget")
        new_trigger["point"] = text2tuple(
            node.attrib["point"], evaluator=float)
        new_trigger["angle"] = float(node.attrib["angle"])
        return new_trigger

    def blend(self):
        """Create representation of W3DTrigger in Blender"""
        self.activator = BlenderPointTrigger(
            self["name"],
            self["actions"],
            self["point"],
            enable_immediately=self["enabled"],
            remain_enabled=self["remain_enabled"])
        self.activator.create_blender_objects()
        return self.activator.base_object


class LookAtDirection(HeadTrackTrigger):
    """For event triggers based on user looking in a direction

    :param tuple direction: Direction in which to look
    :param float angle: Look direction must be within this angle of target"""

    argument_validators = {
        "direction": ListValidator(
            IsNumeric(),
            help_string="Vector specifying look direction"
        ),
        "angle": IsNumeric()
    }
    default_arguments = {
        "angle": 30
    }

    def toXML(self, all_triggers_root):
        """Store LookAtDirection as EventTrigger node within EventRoot node

        :param :py:class:xml.etree.ElementTree.Element all_triggers_root
        """
        trigger_root = self.base_trigger.toXML(all_triggers_root)
        node = ET.SubElement(trigger_root, "HeadTrack")
        position_node = ET.SubElement(node, "Position")
        ET.SubElement(position_node, "Anywhere")
        node = ET.SubElement(node, "Direction")
        try:
            xml_attrib = {
                "direction": "({}, {}, {})".format(*self["direction"])
            }
        except KeyError:
            raise ConsistencyError("LookAtDirection must specify direction")
        if not self.is_default("angle"):
            xml_attrib["angle"] = str(self["angle"])
        ET.SubElement(node, "DirectionTarget", attrib=xml_attrib)
        return trigger_root

    @classmethod
    def fromXML(trigger_class, trigger_root):
        """Create LookAtDirection from EventTrigger node

        :param :py:class:xml.etree.ElementTree.Element target_root
        """
        new_trigger = trigger_class()
        new_trigger.base_trigger = HeadPositionTrigger.fromXML(trigger_root)
        node = trigger_root.find("HeadTrack")
        node = node.find("Direction")
        node = node.find("DirectionTarget")
        new_trigger["direction"] = text2tuple(
            node.attrib["direction"], evaluator=float)
        new_trigger["angle"] = float(node.attrib["angle"])
        return new_trigger

    def blend(self):
        """Create representation of W3DTrigger in Blender"""
        self.activator = BlenderDirectionTrigger(
            self["name"],
            self["actions"],
            self["direction"],
            enable_immediately=self["enabled"],
            remain_enabled=self["remain_enabled"])
        self.activator.create_blender_objects()
        return self.activator.base_object


class LookAtObject(HeadTrackTrigger):
    """For event triggers based on user looking at an object

    :param str object: Name of the object to look at
    :param float angle: TODO: clarify (WARNING: currently does nothing)"""

    argument_validators = {
        "object": ReferenceValidator(
            ValidPyString(),
            ["objects"],
            help_string="Must be an existing object"
        ),
        "angle": IsNumeric()
    }

    def toXML(self, all_triggers_root):
        """Store LookAtObject as EventTrigger node within EventRoot node

        :param :py:class:xml.etree.ElementTree.Element all_triggers_root
        """
        trigger_root = self.base_trigger.toXML(all_triggers_root)
        node = ET.SubElement(trigger_root, "HeadTrack")
        position_node = ET.SubElement(node, "Position")
        ET.SubElement(position_node, "Anywhere")
        node = ET.SubElement(node, "Direction")
        try:
            xml_attrib = {
                "name": self["object"]
            }
        except KeyError:
            raise ConsistencyError("LookAtObject must specify object")
        ET.SubElement(node, "ObjectTarget", attrib=xml_attrib)
        return trigger_root

    @classmethod
    def fromXML(trigger_class, trigger_root):
        """Create LookAtObject from EventTrigger node

        :param :py:class:xml.etree.ElementTree.Element target_root
        """
        new_trigger = trigger_class()
        new_trigger.base_trigger = HeadPositionTrigger.fromXML(trigger_root)
        node = trigger_root.find("HeadTrack")
        node = node.find("Direction")
        node = node.find("ObjectTarget")
        new_trigger["object"] = node.attrib["name"].strip()
        return new_trigger

    def blend(self):
        """Create representation of W3DTrigger in Blender"""
        self.activator = BlenderLookObjectTrigger(
            self["name"],
            self["actions"],
            self["object"],
            enable_immediately=self["enabled"],
            remain_enabled=self["remain_enabled"])
        self.activator.create_blender_objects()
        return self.activator.base_object


class MovementTrigger(W3DTrigger):
    """For triggers based on movement of W3D objects

    :param str type: One of "Single Object", "Group(Any)", or "Group(All)",
    depending on if action should be triggered based on movements of a single
    object, any object in group, or all objects in group. That is, should
    trigger occur when any object in the group moves into specified region or
    once all objects have moved into the region?
    :param str name: The name of the object or group to track
    :param EventBox box: Used to trigger events when objects move into or out
    of specified box
    """
    argument_validators = {
        "type": OptionValidator(
            "Single Object", "Group(Any)", "Group(All)"),
        "object_name": ValidPyString(),
        "box": FeatureValidator(
            EventBox,
            help_string="Box used to check position of objects")
    }

    def toXML(self, all_triggers_root):
        """Store MovementTrigger as EventTrigger node within EventRoot node

        :param :py:class:xml.etree.ElementTree.Element trigger_root
        """
        trigger_root = self.base_trigger.toXML(all_triggers_root)
        track_node = ET.SubElement(trigger_root, "MoveTrack")
        node = ET.SubElement(track_node, "Source")
        try:
            xml_attrib = {"name", self["object_name"]}
        except KeyError:
            raise ConsistencyError("MovementTrigger must specify object_name")

        if self["type"] == "Single Object":
            ET.SubElement(node, "ObjectRef", attrib=xml_attrib)
        else:
            # Extract Any/All
            xml_attrib["objects"] = self["type"][
                self["type"].find("(") + 1: self["type"].find(")")]
            #Add Objects to the end
            xml_attrib["objects"] += " Objects"
            ET.SubElement(node, "GroupObj", attrib=xml_attrib)

        try:
            self["box"].toXML(track_node)
        except KeyError:
            raise ConsistencyError("MovementTrigger must specify box")

        return trigger_root

    @classmethod
    def fromXML(trigger_class, trigger_root):
        """Create MovementTrigger from EventTrigger node

        :param :py:class:xml.etree.ElementTree.Element movement_root
        """
        new_trigger = trigger_class()
        new_trigger.base_trigger = BareTrigger.fromXML(trigger_root)
        track_node = trigger_root.find("MoveTrack")
        source_node = track_node.find("Source")
        node = source_node.find("ObjectRef")
        if node is not None:
            new_trigger["type"] = "Single Object"
        else:
            node = source_node.find("GroupObj")
            if node is not None:
                try:
                    new_trigger["type"] = "Group ({})".format(
                        node.attrib["objects"])
                except KeyError:
                    raise BadW3DXML(
                        'GroupObj node must specify "objects" attribute')
        try:
            new_trigger["object_name"] = node.attrib["name"]
        except KeyError:
            raise BadW3DXML(
                'GroupObj or ObjectRef node must specify "name" attribute')
        node = track_node.find("Box")
        if node is None:
            raise BadW3DXML("Source node must have Box child")
        new_trigger["box"] = EventBox.fromXML(node)
        return new_trigger

    def blend(self):
        """Create representation of W3DTrigger in Blender"""
        if self["type"] == "Single Object":
            objects_string = "['{}']".format(self["object_name"])
        else:
            objects_string = self["object_name"]
        if "All" in self["type"]:
            detect_any = False
        self.activator = BlenderObjectPositionTrigger(
            self["name"],
            self["actions"],
            self["box"],
            objects_string,
            enable_immediately=self["enabled"],
            remain_enabled=self["remain_enabled"],
            detect_any=detect_any)
        self.activator.create_blender_objects()
        return self.activator.base_object
