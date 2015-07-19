"""Tools for working with particular Cave events that can trigger actions

Here, triggers are any events within the Cave that can be used to start another
action. For example, when the viewer reaches a particular location, a timeline
can be started."""
import xml.etree.ElementTree as ET
from features import CaveFeature
from actions import CaveAction
from validators import AlwaysValid, IsNumeric, IsNumericIterable, \
    OptionListValidator
from errors import ConsistencyError, BadCaveXML
from xml_tools import bool2text


def TriggerXMLDecorator(fromXML):
    """Decorator for fromXML to gather data not specific to subclass"""
    def wrapped_fromXML(trigger_class, xml_root):
        new_trigger = trigger_class()
        try:
            new_trigger["name"] = xml_root.attrib["name"]
        except KeyError:
            raise BadCaveXML("EventTrigger must specify name attribute")
        xml_tags = {
            "enabled": "enabled", "remain_enabled": "remain-enabled",
            "duration": "duration"}
        for key, tag in xml_tags:
            if tag in xml_root.attrib:
                new_trigger[key] = xml_root.attrib[tag]
        action_root = xml_root.find("Actions")
        if action_root is not None:
            for child in action_root.getchildren():
                new_trigger["actions"].append(CaveAction.fromXML(child))
        return fromXML(xml_root).update(new_trigger)
    return wrapped_fromXML


class CaveTrigger(CaveFeature):
    """Store data on a trigger event in the cave

    :param str name: Unique name for this trigger
    :param bool enabled: Is this trigger enabled?
    :param bool remain-enabled: Should this remain enabled after it is
    triggered?
    :param float duration: TODO: Clarify
    :param actions: List of names of CaveActions to be triggered"""

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
        "actions": []
        }

    def toXML(self, all_triggers_root):
        """Store CaveTrigger as EventTrigger node within EventRoot node

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

    # Would it be better for to decorate with TriggerXMLDecorator here rather
    # than in subclasses? Only disadvantage is that we're updating with a
    # generic CaveTrigger in the decorator, but I'm not sure that's really an
    # issue. Actually, by decorating the subclasses, we ensure that a fully
    # valid CaveTrigger is always returned, even if the subclass fromXMLs are
    # called directly, not through CaveTrigger.
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
        raise BadCaveXML(
            "EventTrigger node must contain HeadTrack or MoveTrack child")

    def blend(self):
        """Create representation of CaveTrigger in Blender"""
        raise NotImplementedError  # TODO


class HeadTrackTrigger(CaveTrigger):
    """For triggers based on head-tracking of Cave user

    :param EventBox box: Used to trigger events when user's head moves into or
    out of specified box. If None, trigger can occur anywhere in Cave
    """
    def __init__(self):
        super(HeadTrackTrigger, self).init()
        # Note: It would really be preferable for argument_validators to always
        # be a class attribute, but short of having __setitem__ always check
        # super's argument_validators as well, I'm not sure that there's an
        # easy way to make this happen. Think about it more.
        self.argument_validators = {
            key: value for (key, value) in
            super(HeadTrackTrigger).argument_validators.items()}
        self.argument_validators.update({
            "box": AlwaysValid(
                help_string="Movement into or out of a box to trigger action?")
            }
        )
        self.default_arguments = {
            key: value for (key, value) in
            super(HeadTrackTrigger).default_arguments.items()}
        self.default_arguments.update({
            "box": None
            }
        )

    def toXML(self, all_triggers_root):
        """Store HeadTrackTrigger as EventTrigger node within EventRoot node

        :param :py:class:xml.etree.ElementTree.Element all_triggers_root
        """
        trigger_root = ET.SubElement(all_triggers_root, "EventTrigger")
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
    @TriggerXMLDecorator
    def fromXML(trigger_root):
        """Create HeadTrackTrigger from EventTrigger node

        :param :py:class:xml.etree.ElementTree.Element trigger_root
        """
        new_trigger = HeadTrackTrigger()
        head_node = trigger_root.find("HeadTrack")
        position_node = head_node.find("Position")
        box_node = position_node.find("Box")
        if box_node is not None:
            new_trigger["box"] = EventBox.fromXML(box_node)
        direction_node = head_node.find("Direction")
        if direction_node.find("None") is not None:
            return new_trigger
        elif direction_node.find("PointTarget") is not None:
            return LookAtPoint.fromXML(trigger_root).update(new_trigger)
        #TODO: Start here, think about when decorators are being applied


class LookAtPoint(HeadTrackTrigger):
    """For event triggers based on user looking at a point

    :param tuple point: The point to look at
    :param float angle: TODO: clarify"""

    def __init__(self):
        super(LookAtPoint, self).init()
        self.argument_validators.update({
            "point": IsNumericIterable(required_length=3),
            "angle": IsNumeric()
            }
        )
        self.default_arguments.update({
            "angle": 30
            }
        )

    def toXML(self, all_triggers_root):
        """Store LookAtPoint as EventTrigger node within EventRoot node

        :param :py:class:xml.etree.ElementTree.Element all_triggers_root
        """
        trigger_root = super(LookAtPoint, self).toXML(all_triggers_root)
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
    def fromXML(target_root):
        """Create LookAtPoint from PointTarget node

        :param :py:class:xml.etree.ElementTree.Element target_root
        """
        return CaveFeature.fromXML(target_root)  # TODO: Replace this


class LookAtDirection(HeadTrackTrigger):
    """For event triggers based on user looking in a direction

    :param tuple direction: Direction in which to look
    :param float angle: TODO: clarify"""

    def __init__(self):
        super(LookAtDirection, self).init()
        self.argument_validators.update({
            "direction": IsNumericIterable(required_length=3),
            "angle": IsNumeric()
            }
        )
        self.default_arguments.update({
            "angle": 30
            }
        )

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
    def fromXML(target_root):
        """Create LookAtDirection from DirectionTarget node

        :param :py:class:xml.etree.ElementTree.Element target_root
        """
        return CaveFeature.fromXML(target_root)  # TODO: Replace this


class LookAtObject(HeadTrackTrigger):
    """For event triggers based on user looking at an object

    :param str object: Name of the object to look at
    :param float angle: TODO: clarify"""

    def __init__(self):
        super(LookAtObject, self).init()
        self.argument_validators.update({
            "object": AlwaysValid("The name of the object to look at"),
            }
        )

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
    def fromXML(target_root):
        """Create LookAtObject from ObjectTarget node

        :param :py:class:xml.etree.ElementTree.Element target_root
        """
        return CaveFeature.fromXML(target_root)  # TODO: Replace this


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
    def __init__(self):
        super(MovementTrigger, self).init()
        self.argument_validators = {
            key: value for (key, value) in
            super(MovementTrigger).argument_validators.items()}
        self.argument_validators.update({
            "type": OptionListValidator(
                "Single Object", "Group(Any)", "Group(All)"),
            "name": AlwaysValid(
                help_string="Must be the name of an object or group"),
            "box": AlwaysValid(
                help_string="Box used to check position of objects")
            }
        )

    def toXML(self, all_triggers_root):
        """Store MovementTrigger as EventTrigger node within EventRoot node

        :param :py:class:xml.etree.ElementTree.Element trigger_root
        """
        trigger_root = super(MovementTrigger, self).toXML(all_triggers_root)
        track_node = ET.SubElement(trigger_root, "MoveTrack")
        node = ET.SubElement(track_node, "Source")
        try:
            xml_attrib = {"name", self["name"]}
        except KeyError:
            raise ConsistencyError("MovementTrigger must specify name")

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
    @TriggerXMLDecorator
    def fromXML(move_track_root):
        """Create MovementTrigger from MoveTrack node

        :param :py:class:xml.etree.ElementTree.Element movement_root
        """
        return CaveFeature.fromXML(move_track_root)  # TODO: Replace this


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
    def fromXML(box_root):
        """Create LookAtObject from ObjectTarget node

        :param :py:class:xml.etree.ElementTree.Element box_root
        """
        return CaveFeature.fromXML(box_root)  # TODO: Replace this
