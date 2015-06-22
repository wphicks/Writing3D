"""Tools for working with actions in the Cave

Here, actions refer generically to any discrete change in elements of a Cave
project
"""
from features import CaveFeature
from validators import OptionListValidator, IsNumeric,  AlwaysValid,\
    IsNumericIterable


# Basic division into changes and transitions doesn't make sense; rethink
# design
class ObjectChange(CaveFeature):
    """Store data on a change to an object

    :param str object_name: Name of object to change
    :param Transition change: Change to apply"""

    argument_validators = {
        "object_name": AlwaysValid("Name of an object"),
        "change": AlwaysValid("Change to apply")
        }

    default_arguments = {}

    def toXML(self, parent_root):
        """Store ObjectChange as ObjectChange node within one of several node
        types

        :param :py:class:xml.etree.ElementTree.Element parent_root
        """
        CaveFeature.toXML(self, parent_root)  # TODO: Replace this

    @classmethod
    def fromXML(object_change_root):
        """Create ObjectChange from ObjectChange node

        :param :py:class:xml.etree.ElementTree.Element transition_root
        """
        return CaveFeature.fromXML(object_change_root)  # TODO: Replace this

    def blend(self):
        """Create representation of change in Blender"""
        raise NotImplementedError  # TODO


class GroupChange(CaveFeature):
    """Store data on a change to a group of objects

    :param str group_name: Name of group to change
    :param Transition change: Change to apply
    :param bool choose_random: Apply change to one object in group, selected
    randomly?
    """

    argument_validators = {
        "object_name": AlwaysValid("Name of an object"),
        "change": AlwaysValid("Change to apply"),
        "choose_random": AlwaysValid("Either true or false")
        }

    default_arguments = {
        "choose_random": False}

    def toXML(self, parent_root):
        """Store GroupChange as GroupRef node within one of several node types

        :param :py:class:xml.etree.ElementTree.Element parent_root
        """
        CaveFeature.toXML(self, parent_root)  # TODO: Replace this

    @classmethod
    def fromXML(groupref_root):
        """Create GroupChange from GroupRef node

        :param :py:class:xml.etree.ElementTree.Element transition_root
        """
        return CaveFeature.fromXML(groupref_root)  # TODO: Replace this

    def blend(self):
        """Create representation of change in Blender"""
        raise NotImplementedError  # TODO


class TimelineChange(CaveFeature):
    """Store data on a change to a timeline

    :param str timeline_name: Name of timeline to change
    :param str change: One of "Start", "Stop", "Continue", "Start if not
    started"
    """

    argument_validators = {
        "timeline_name": AlwaysValid("Name of a timeline"),
        "change": OptionListValidator(
            "Start", "Stop", "Continue", "Start if not started")
        }

    default_arguments = {}

    def toXML(self, parent_root):
        """Store TimelineChange as TimerChange node within one of several node
        types

        :param :py:class:xml.etree.ElementTree.Element parent_root
        """
        CaveFeature.toXML(self, parent_root)  # TODO: Replace this

    @classmethod
    def fromXML(timer_change_root):
        """Create TimelineChange from TimerChange node

        :param :py:class:xml.etree.ElementTree.Element transition_root
        """
        return CaveFeature.fromXML(timer_change_root)  # TODO: Replace this

    def blend(self):
        """Create representation of change in Blender"""
        raise NotImplementedError  # TODO


class SoundChange(CaveFeature):
    """Store data on a change to a sound

    :param str sound_name: Name of sound to change
    :param Transition change: Change to apply"""

    argument_validators = {
        "sound_name": AlwaysValid("Name of an object"),
        "change": AlwaysValid("Change to apply")
        }

    default_arguments = {}

    def toXML(self, parent_root):
        """Store ObjectChange as ObjectChange node within one of several node
        types

        :param :py:class:xml.etree.ElementTree.Element parent_root
        """
        CaveFeature.toXML(self, parent_root)  # TODO: Replace this

    @classmethod
    def fromXML(object_change_root):
        """Create ObjectChange from ObjectChange node

        :param :py:class:xml.etree.ElementTree.Element transition_root
        """
        return CaveFeature.fromXML(object_change_root)  # TODO: Replace this

    def blend(self):
        """Create representation of change in Blender"""
        raise NotImplementedError  # TODO


class EventChange(CaveFeature):
    """Store data on a change to an event

    :param str event_name: Name of object to change
    :param bool enable: Enable event?"""

    argument_validators = {
        "object_name": AlwaysValid("Name of an object"),
        "enable": AlwaysValid("Either true or false")
        }

    default_arguments = {}

    def toXML(self, parent_root):
        """Store EventChange as Event node within one of several node types

        :param :py:class:xml.etree.ElementTree.Element parent_root
        """
        CaveFeature.toXML(self, parent_root)  # TODO: Replace this

    @classmethod
    def fromXML(event_root):
        """Create EventChange from Event node

        :param :py:class:xml.etree.ElementTree.Element transition_root
        """
        return CaveFeature.fromXML(event_root)  # TODO: Replace this

    def blend(self):
        """Create representation of change in Blender"""
        raise NotImplementedError  # TODO


class MoveCave(CaveFeature):
    """Store data on a change to an object

    :param str object_name: Name of object to change
    :param Transition change: Change to apply"""

    argument_validators = {
        "object_name": AlwaysValid("Name of an object"),
        "change": AlwaysValid("Change to apply")
    }

    default_arguments = {}

    def toXML(self, parent_root):
        """Store MoveCave as MoveCave node within one of several node
        types

        :param :py:class:xml.etree.ElementTree.Element parent_root
        """
        CaveFeature.toXML(self, parent_root)  # TODO: Replace this

    @classmethod
    def fromXML(move_cave_root):
        """Create MoveCave from MoveCave node

        :param :py:class:xml.etree.ElementTree.Element transition_root
        """
        return CaveFeature.fromXML(move_cave_root)  # TODO: Replace this

    def blend(self):
        """Create representation of change in Blender"""
        raise NotImplementedError  # TODO

# TODO: CaveReset


class Transition(CaveFeature):
    """Store data on transitions within Cave

    :param float duration: Duration of transition in seconds
    :param bool visible: If not None, change visibility to this value
    :param CavePlacement placement: If not None, move based on this placement
    :param bool move_relative: If True, move relative to original location
    :param tuple color: If not None, transition to this color
    :param float scale: If not None, scale by this factor
    :param str sound_change: One of "Play Sound" or "Stop Sound"
    :param str link_change: One of "Enable", "Disable", "Activate", "Activate
    if enabled"
    """

    argument_validators = {
        "duration": IsNumeric(),
        "visible": AlwaysValid("Either true or false"),
        "placement": AlwaysValid("A CavePlacement object"),
        "move_relative": AlwaysValid("Either true or false"),
        "color": IsNumericIterable(required_length=3),
        "scale": IsNumeric(min_value=0),
        "sound_change": OptionListValidator("Play Sound", "Stop Sound"),
        "link_change": OptionListValidator(
            "Enable", "Disable", "Activate", "Activate if enabled")
        }

    default_arguments = {
        "duration": 1
        }

    def toXML(self, parent_root):
        """Store Transition as Transition node within one of several node types

        :param :py:class:xml.etree.ElementTree.Element parent_root
        """
        CaveFeature.toXML(self, parent_root)  # TODO: Replace this

    @classmethod
    def fromXML(transition_root):
        """Create Transition from Transition node

        :param :py:class:xml.etree.ElementTree.Element transition_root
        """
        return CaveFeature.fromXML(transition_root)  # TODO: Replace this
