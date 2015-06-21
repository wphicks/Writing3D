"""Tools for working with particular Cave events that can trigger actions

Here, triggers are any events within the Cave that can be used to start another
action. For example, when the viewer reaches a particular location, a timeline
can be started."""
from features import CaveFeature
from validators import AlwaysValid, IsNumeric, IsNumericIterable, \
    OptionListValidator


class CaveTrigger(CaveFeature):
    """Store data on a trigger event in the cave

    :param str name: Unique name for this trigger
    :param bool enabled: Is this trigger enabled?
    :param bool remain-enabled: Should this remain enabled after it is
    triggered?
    :param float duration: TODO: Clarify
    :param actions: List of CaveActions to be triggered"""

    argument_validators = {
        "name": AlwaysValid(
            help_string="This string should specify a unique name for this"
            " trigger"),
        "enabled": AlwaysValid(
            help_string="Either true or false"),
        "remain-enabled": AlwaysValid(
            help_string="Either true or false"),
        "duration": IsNumeric(min_value=0),
        "actions": AlwaysValid(help_string="A list of CaveActions")
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


# Kinda got bunny classes here, but seems necessary given legacy format...
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


class LookAtDirection(CaveFeature):
    """For event triggers based on user looking in a direction

    :param tuple direction: Direction in which to look
    :param float angle: TODO: clarify"""

    argument_validators = {
        "direction": IsNumericIterable(required_length=3),
        "angle": IsNumeric()
        }

    default_arguments = {
        "direction": 30
        }


class LookAtObject(CaveFeature):
    """For event triggers based on user looking at an object

    :param CaveObject object: The object to look at
    :param float angle: TODO: clarify"""

    argument_validators = {
        "point": IsNumericIterable(required_length=3),
        "angle": IsNumeric()
        }

    default_arguments = {
        "angle": 30
        }


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


class HeadTrackTrigger(CaveFeature):
    """For triggers based on head-tracking of Cave user

    :param look_at_target: A LookAtDirection, LookAtPoint, or LookAtObject
    :param EventBox box: Used to trigger events when user's head moves into or
    out of specified box
    """
