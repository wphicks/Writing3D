"""Tools for working with particular Cave events that can trigger actions

Here, triggers are any events within the Cave that can be used to start another
action. For example, when the viewer reaches a particular location, a timeline
can be started."""
import xml.etree.ElementTree as ET
from .features import CaveFeature
from .actions import CaveAction
from .validators import AlwaysValid, IsNumeric, IsNumericIterable, \
    OptionListValidator
from .errors import ConsistencyError, BadCaveXML, InvalidArgument, \
    EBKAC
from .xml_tools import bool2text, text2tuple, text2bool
from .activators import BlenderTrigger, BlenderPositionTrigger, \
    BlenderPointTrigger, BlenderDirectionTrigger, BlenderLookObjectTrigger, \
    BlenderObjectPositionTrigger


class CaveTrigger(CaveFeature):
    """Store data on a trigger event in the cave

    :ivar base_trigger: A trigger object wrapped by this trigger (see
    __setitem__ and __getitem__ implementation for details)
    """
    def __init__(self, *args, **kwargs):
        self.base_trigger = BareTrigger()
        super(CaveTrigger, self).__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        try:
            return super(CaveTrigger, self).__setitem__(key, value)
        except InvalidArgument as bad_key_error:
            try:
                self.base_trigger.__setitem__(key, value)
            except InvalidArgument:
                raise bad_key_error

    def __getitem__(self, key):
        try:
            return super(CaveTrigger, self).__getitem__(key)
        except KeyError as not_found_error:
            try:
                return self.base_trigger.__getitem__(key)
            except KeyError:
                raise not_found_error

    @staticmethod
    def fromXML(trigger_root):
        """Create CaveTrigger from EventTrigger node

        :param :py:class:xml.etree.ElementTree.Element trigger_root
        """
        tag_class_dict = {
            "HeadTrack": HeadTrackTrigger,
            "MoveTrack": MovementTrigger
        }
        for tag, trigger_class in tag_class_dict:
            if trigger_root.find(tag) is not None:
                return trigger_class.fromXML(trigger_root)
        return BareTrigger.fromXML(trigger_root)

    def blend(self):
        """Create representation of CaveTrigger in Blender"""
        self.activator = BlenderTrigger(
            self["name"],
            self["actions"],
            enable_immediately=self["enabled"],
            remain_enabled=self["remain_enabled"])
        self.activator.create_blender_objects()
        return self.activator.base_object

    def link_blender_logic(self):
        """Link BGE logic bricks for this CaveTrigger"""
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


class BareTrigger(CaveFeature):
    """A trigger specifying only base information common to other triggers

    :param str name: Unique name for this trigger
    :param bool enabled: Is this trigger enabled?
    :param bool remain-enabled: Should this remain enabled after it is
    triggered?
    :param float duration: TODO: Clarify
    :param actions: List of CaveActions to be triggered
    """
    argument_validators = {
        "name": AlwaysValid(
            help_string="This string should specify a unique name for this"
            " trigger"),
        "enabled": AlwaysValid(
            help_string="Either true or false"),
        "remain_enabled": AlwaysValid(
            help_string="Either true or false"),
        "duration": IsNumeric(min_value=0),
        "actions": AlwaysValid(help_string="A list of names of CaveActions")
        }

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
            raise ConsistencyError("CaveTrigger must specify name")
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
            raise BadCaveXML("EventTrigger must specify name attribute")
        xml_tags = {
            "enabled": "enabled", "remain_enabled": "remain-enabled",
            "duration": "duration"}
        for key, tag in xml_tags:
            if tag in trigger_root.attrib:
                new_trigger[key] = trigger_root.attrib[tag]
        action_root = trigger_root.find("Actions")
        if action_root is not None:
            for child in action_root.getchildren():
                new_trigger["actions"].append(CaveAction.fromXML(child))
        return new_trigger


class HeadTrackTrigger(CaveTrigger):
    """For triggers based on head-tracking of Cave user
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
            raise BadCaveXML(
                "HeadTrack node must contain None, PointTarget,"
                " DirectionTarget, or ObjectTarget child node")


class HeadPositionTrigger(HeadTrackTrigger):
    """For triggers based on position of user in Cave

    :param EventBox box: Used to trigger events when user's head moves into or
    out of specified box. If None, trigger can occur anywhere in Cave
    """

    argument_validators = {
        "box": AlwaysValid(
            help_string="Movement into or out of a box to trigger action?")
    }

    default_arguments = {
        "box": None
    }

    def toXML(self, all_triggers_root):
        """Store HeadPositionTrigger as EventTrigger node within EventRoot node

        :param :py:class:xml.etree.ElementTree.Element all_triggers_root
        """
        trigger_root = self.bare_trigger.toXML(all_triggers_root)
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
        """Create representation of CaveTrigger in Blender"""
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

    argument_validators = {
        "point": IsNumericIterable(required_length=3),
        "angle": IsNumeric()
    }
    default_arguments = {
        "angle": 30
    }

    def toXML(self, all_triggers_root):
        """Store LookAtPoint as EventTrigger node within EventRoot node

        :param :py:class:xml.etree.ElementTree.Element all_triggers_root
        """
        trigger_root = self.bare_trigger.toXML(all_triggers_root)
        node = trigger_root.find("HeadTrack")
        node = node.find("Direction")
        node.remove(node.find("None"))
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
        """Create representation of CaveTrigger in Blender"""
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
        "direction": IsNumericIterable(required_length=3),
        "angle": IsNumeric()
    }
    default_arguments = {
        "angle": 30
    }

    def toXML(self, all_triggers_root):
        """Store LookAtDirection as EventTrigger node within EventRoot node

        :param :py:class:xml.etree.ElementTree.Element all_triggers_root
        """
        trigger_root = super(LookAtDirection, self).toXML(all_triggers_root)
        node = trigger_root.find("HeadTrack")
        node = node.find("Direction")
        node.remove(node.find("None"))
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
        """Create representation of CaveTrigger in Blender"""
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
        "object": AlwaysValid("The name of the object to look at"),
    }

    def toXML(self, all_triggers_root):
        """Store LookAtObject as EventTrigger node within EventRoot node

        :param :py:class:xml.etree.ElementTree.Element all_triggers_root
        """
        trigger_root = super(LookAtObject, self).toXML(all_triggers_root)
        node = trigger_root.find("HeadTrack")
        node = node.find("Direction")
        node.remove(node.find("None"))
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
        """Create representation of CaveTrigger in Blender"""
        self.activator = BlenderLookObjectTrigger(
            self["name"],
            self["actions"],
            self["object"],
            enable_immediately=self["enabled"],
            remain_enabled=self["remain_enabled"])
        self.activator.create_blender_objects()
        return self.activator.base_object


class MovementTrigger(CaveTrigger):
    """For triggers based on movement of Cave objects

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
        "type": OptionListValidator(
            "Single Object", "Group(Any)", "Group(All)"),
        "object_name": AlwaysValid(
            help_string="Must be the name of an object or group"),
        "box": AlwaysValid(
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
                    raise BadCaveXML(
                        'GroupObj node must specify "objects" attribute')
        try:
            new_trigger["object_name"] = node.attrib["name"]
        except KeyError:
            raise BadCaveXML(
                'GroupObj or ObjectRef node must specify "name" attribute')
        node = track_node.find("Box")
        if node is None:
            raise BadCaveXML("Source node must have Box child")
        new_trigger["box"] = EventBox.fromXML(node)
        return new_trigger

    def blend(self):
        """Create representation of CaveTrigger in Blender"""
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


class EventBox(CaveFeature):
    """For triggers based on movement into or out of box

    :param str direction: One of "Inside" or "Outside" depending on whether
    trigger occurs for movement into or out of box
    :param bool ignore_y: Should y-direction be ignored in checking box? In
    other words, vertical position in Cave doesn't matter when this is set to
    true.
    :param tuple corner1: First corner specifiying box location
    :param tuple corner2: Second corner specifying box location
    """

    argument_validators = {
        "direction": OptionListValidator("Inside", "Outside"),
        "ignore_y": AlwaysValid(
            help_string="Either true or false"),
        "corner1": IsNumericIterable(required_length=3),
        "corner2": IsNumericIterable(required_length=3)}

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
                raise BadCaveXML(
                    'Box node must specify attribute {}'.format(corner))

        if "ignore-y" in box_root.attrib:
            new_box["ignore_y"] = text2bool(box_root.attrib["ignore-y"])
        return new_box
