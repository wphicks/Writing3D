"""Tools for working with particular Cave events that can trigger actions

Here, triggers are any events within the Cave that can be used to start another
action. For example, when the viewer reaches a particular location, a timeline
can be started."""
from features import CaveFeature
from validators import AlwaysValid, IsNumeric, IsNumericIterable, \
    OptionListValidator


# Kinda got bunny classes here, but seems necessary given legacy format...
# Should probably revisit this overall design at some point
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
        "remain-enabled": AlwaysValid(
            help_string="Either true or false"),
        "duration": IsNumeric(min_value=0),
        "actions": AlwaysValid(help_string="A list of names of CaveActions")
        }

    default_arguments = {
        "enabled": True,
        "remain-enabled": True,
        "duration": 0,
        "actions": []
        }

    def toXML(self, all_triggers_root):
        """Store CaveTrigger as EventTrigger node within EventRoot node

        :param :py:class:xml.etree.ElementTree.Element all_triggers_root
        """
        CaveFeature.toXML(self, all_triggers_root)  # TODO: Replace this

    @classmethod
    def fromXML(trigger_root):
        """Create CaveTrigger from EventTrigger node

        :param :py:class:xml.etree.ElementTree.Element trigger_root
        """
        return CaveFeature.fromXML(trigger_root)  # TODO: Replace this

    def blend(self):
        """Create representation of CaveTrigger in Blender"""
        raise NotImplementedError  # TODO


class LookAtPoint(CaveFeature):
    """For event triggers based on user looking at a point

    :param tuple point: The point to look at
    :param float angle: TODO: clarify"""

    argument_validators = {
        "point": IsNumericIterable(required_length=3),
        "angle": IsNumeric()
        }

    default_arguments = {
        "angle": 30
        }

    def toXML(self, direction_root):
        """Store LookAtPoint as PointTarget node within Direction node

        :param :py:class:xml.etree.ElementTree.Element direction_root
        """
        CaveFeature.toXML(self, direction_root)  # TODO: Replace this

    @classmethod
    def fromXML(target_root):
        """Create LookAtPoint from PointTarget node

        :param :py:class:xml.etree.ElementTree.Element target_root
        """
        return CaveFeature.fromXML(target_root)  # TODO: Replace this


class LookAtDirection(CaveFeature):
    """For event triggers based on user looking in a direction

    :param tuple direction: Direction in which to look
    :param float angle: TODO: clarify"""

    argument_validators = {
        "direction": IsNumericIterable(required_length=3),
        "angle": IsNumeric()
        }

    default_arguments = {
        "angle": 30
        }

    def toXML(self, direction_root):
        """Store LookAtDirection as DirectionTarget node within Direction node

        :param :py:class:xml.etree.ElementTree.Element direction_root
        """
        CaveFeature.toXML(self, direction_root)  # TODO: Replace this

    @classmethod
    def fromXML(target_root):
        """Create LookAtDirection from DirectionTarget node

        :param :py:class:xml.etree.ElementTree.Element target_root
        """
        return CaveFeature.fromXML(target_root)  # TODO: Replace this


class LookAtObject(CaveFeature):
    """For event triggers based on user looking at an object

    :param str object: Name of the object to look at
    :param float angle: TODO: clarify"""

    argument_validators = {
        "name": AlwaysValid("The name of the object to look at"),
        }

    default_arguments = {
        }

    def toXML(self, direction_root):
        """Store LookAtObject as ObjectTarget node within Direction node

        :param :py:class:xml.etree.ElementTree.Element direction_root
        """
        CaveFeature.toXML(self, direction_root)  # TODO: Replace this

    @classmethod
    def fromXML(target_root):
        """Create LookAtObject from ObjectTarget node

        :param :py:class:xml.etree.ElementTree.Element target_root
        """
        return CaveFeature.fromXML(target_root)  # TODO: Replace this


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
        CaveFeature.toXML(self, parent_root)  # TODO: Replace this

    @classmethod
    def fromXML(box_root):
        """Create LookAtObject from ObjectTarget node

        :param :py:class:xml.etree.ElementTree.Element box_root
        """
        return CaveFeature.fromXML(box_root)  # TODO: Replace this


class HeadTrackTrigger(CaveTrigger):
    """For triggers based on head-tracking of Cave user

    :param look_at_target: A LookAtDirection, LookAtPoint, or LookAtObject
    :param EventBox box: Used to trigger events when user's head moves into or
    out of specified box
    """
    argument_validators = {
        "look_at_target": AlwaysValid(
            help_string="What should be looked at to trigger action?"),
        "box": AlwaysValid(
            help_string="Movement into or out of a box to trigger action?")}

    default_arguments = {
        "look_at_target": None,
        "box": None
        }

    def toXML(self, trigger_root):
        """Store HeadTrackTrigger as HeadTrack node within EventTrigger node

        :param :py:class:xml.etree.ElementTree.Element trigger_root
        """
        CaveFeature.toXML(self, trigger_root)  # TODO: Replace this

    @classmethod
    def fromXML(head_track_root):
        """Create HeadTrackTrigger from HeadTrack node

        :param :py:class:xml.etree.ElementTree.Element trigger_root
        """
        return CaveFeature.fromXML(head_track_root)  # TODO: Replace this


class MovementTrigger(CaveTrigger):
    """For triggers based on movement of Cave objects

    :param str type: One of "Single Object", "Group(Any)", or "Group(All)",
    depending on if action should be triggered based on movements of a single
    object, any object in group, or all objects in group. That is, should
    trigger occur when any object in the group moves into specified region or
    once all objects have moved into the region?
    ;param str name: The name of the object or group to track
    :param EventBox box: Used to trigger events when objects move into or out
    of specified box
    """
    argument_validators = {
        "type": OptionListValidator(
            "Single Object", "Group(Any)", "Group(All)"),
        "name": AlwaysValid(
            help_string="Must be the name of an object or group"),
        "box": AlwaysValid(
            help_string="Box used to check position of objects")}

    default_arguments = {
        }

    def toXML(self, trigger_root):
        """Store MovementTrigger as MoveTrack node within EventTrigger node

        :param :py:class:xml.etree.ElementTree.Element trigger_root
        """
        CaveFeature.toXML(self, trigger_root)  # TODO: Replace this

    @classmethod
    def fromXML(move_track_root):
        """Create MovementTrigger from MoveTrack node

        :param :py:class:xml.etree.ElementTree.Element movement_root
        """
        return CaveFeature.fromXML(move_track_root)  # TODO: Replace this
