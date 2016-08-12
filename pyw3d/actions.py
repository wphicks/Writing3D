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

"""Tools for working with actions in the W3D

Here, actions refer generically to any discrete change in elements of a W3D
project
"""
import logging
import xml.etree.ElementTree as ET
from functools import total_ordering
from .features import W3DFeature
from .placement import W3DPlacement
from .validators import OptionValidator, IsNumeric,\
    ListValidator, IsBoolean, FeatureValidator, ReferenceValidator,\
    ValidPyString, IsInteger
from .errors import BadW3DXML, InvalidArgument, ConsistencyError
from .xml_tools import bool2text, text2bool, text2tuple
from .names import generate_blender_object_name, generate_group_name,\
    generate_blender_sound_name
from .metaclasses import SubRegisteredClass
try:
    import bpy
    from .blender_actions import ActionCondition, VisibilityAction,\
        MoveAction, ColorAction, LinkAction, TimelineStarter, TriggerEnabler,\
        SceneReset, ScaleAction, SoundChange
except ImportError:
    logging.debug(
        "Could not import from blender_actions submodule. Loading"
        "pyw3d.actions as standalone."
    )


@total_ordering
class W3DAction(W3DFeature, metaclass=SubRegisteredClass):
    """An action causing a change in virtual space

    Note: This is mostly a dummy class. Provides fromXML to pass XML nodes to
    appropriate subclasses"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.actuators = []

    def __lt__(self, other):
        """Order based on __repr__ of self and other

        Defined to allow unambiguous ordering of timelines"""

        return repr(self) < repr(other)

    @staticmethod
    def fromXML(action_root):
        """Create W3DAction of appropriate subclass given xml root for any
        action"""

        if action_root.tag == "ObjectChange":
            return ObjectAction.fromXML(action_root)
        elif action_root.tag == "GroupRef":
            return GroupAction.fromXML(action_root)
        elif action_root.tag == "TimerChange":
            return TimelineAction.fromXML(action_root)
        elif action_root.tag == "SoundRef":
            return SoundAction.fromXML(action_root)
        elif action_root.tag == "Event":
            return EventTriggerAction.fromXML(action_root)
        elif action_root.tag == "MoveCave":
            return MoveVRAction.fromXML(action_root)
        elif action_root.tag == "Restart":
            return W3DResetAction.fromXML(action_root)
        else:
            raise BadW3DXML(
                "Indicated action {} is not a valid action type".format(
                    action_root.tag))


def generate_object_action_logic(
        object_action, offset=0, time_condition=0, index_condition=None,
        click_condition=-1):
    """Generate Python logic for implementing action

    :param W3DAction object_action: An ObjectAction or GroupAction
    :param int offset: A number of tabs (4 spaces) to add before Python logic
    strings
    :param float time_condition: Time at which action should start
    :param int index_condition: Index used to keep track of what actions
    have already been triggered, e.g. in a timeline of multiple actions"""
    start_text = []
    cont_text = []
    end_text = []

    conditions = ActionCondition(offset=offset)
    object_action.end_time = object_action["duration"] + time_condition
    conditions.add_time_condition(
        start_time=time_condition, end_time=object_action.end_time)
    if index_condition is not None:
        conditions.add_index_condition(index_condition)
    if click_condition > 0:
        conditions.add_click_condition(click_condition)

    offset = conditions.offset + 1
    start_text.append(conditions.start_string)
    start_text.append("{}index += 1".format(
        "    " * (offset)))
    start_text.extend(object_action._blender_object_selection(
        offset=offset)
    )
    cont_text.append(conditions.continue_string)
    cont_text.extend(object_action._blender_object_selection(
        offset=offset)
    )
    end_text.append(conditions.end_string)
    end_text.extend(object_action._blender_object_selection(
        offset=offset)
    )

    offset += object_action.selection_offset
    # Yeah... I know. It's kinda ugly.

    cont_text.append("{}remaining_time = {} - time".format(
        "    " * (offset),
        object_action.end_time)
    )

    if "visible" in object_action:
        action = VisibilityAction(
            object_action["visible"], object_action["duration"],
            offset=(offset)
        )
        start_text.append(action.start_string)
        cont_text.append(action.continue_string)
        end_text.append(action.end_string)

    if "placement" in object_action:
        action = MoveAction(
            object_action["placement"],
            object_action["duration"],
            object_action["move_relative"],
            offset=(offset)
        )
        start_text.append(action.start_string)
        cont_text.append(action.continue_string)
        end_text.append(action.end_string)

    if "color" in object_action:
        action = ColorAction(
            object_action["color"], object_action["duration"],
            offset=(offset)
        )
        start_text.append(action.start_string)
        cont_text.append(action.continue_string)
        end_text.append(action.end_string)

    if "scale" in object_action:
        action = ScaleAction(
            object_action["scale"], object_action["duration"],
            offset=(offset)
        )
        start_text.append(action.start_string)
        cont_text.append(action.continue_string)
        end_text.append(action.end_string)

    if "link_change" in object_action:
        action = LinkAction(
            object_action["object_name"], object_action["link_change"],
            offset=(offset)
        )
        start_text.append(action.start_string)
        cont_text.append(action.continue_string)
        end_text.append(action.end_string)

    if "sound_change" in object_action:
        action = SoundChange(
            object_action["object_name"], object_action["sound_change"],
            offset, object_name=object_action["object_name"]
        )
        start_text.append(action.start_string)
        cont_text.append(action.continue_string)
        end_text.append(action.end_string)
        sound_actuator = bpy.data.objects[
            generate_blender_object_name(object_action["object_name"])].actuators[
                generate_blender_sound_name(object_action["object_name"])]
        object_action.actuators.append(sound_actuator)

    end_text.append(
        "{}own['random_choice'] = None".format("    " * offset)
    )

    return start_text + cont_text + end_text


class ObjectAction(W3DAction):
    """An action causing a change to a W3DObject

    :param str object_name: Name of object to change
    :param float duration: Duration of transition in seconds
    :param bool visible: If not None, change visibility to this value
    :param W3DPlacement placement: If not None, move based on this placement
    :param bool move_relative: If True, move relative to original location
    :param tuple color: If not None, transition to this color
    :param float scale: If not None, scale by this factor
    :param str sound_change: One of "Play Sound" or "Stop Sound", which will
    play or stop sound associated with this object
    :param str link_change: One of "Enable", "Disable", "Activate", "Activate
    if enabled", which will affect this object's link
    """

    argument_validators = {
        "object_name": ReferenceValidator(
            ValidPyString(),
            ["objects"],
            help_string="Must be the name of an object"),
        "duration": IsNumeric(min_value=0),
        "visible": IsBoolean(),
        "placement": FeatureValidator(
            W3DPlacement,
            help_string="Orientation and position for movement"),
        "move_relative": IsBoolean(),
        "color": ListValidator(
            IsInteger(min_value=0, max_value=255),
            required_length=3,
            help_string="Red, Green, Blue values"),
        "scale": IsNumeric(min_value=0),
        # TODO
        "sound_change": OptionValidator("Play Sound", "Stop Sound"),
        "link_change": OptionValidator(
            "Enable", "Disable", "Activate", "Activate if enabled")
    }

    default_arguments = {
        "duration": 1,
        "move_relative": False
    }

    link_xml_tags = {
        "Enable": "link_on", "Disable": "link_off", "Activate": "activate",
        "Activate if enabled": "activate_if_on"}

    sound_xml_tags = {"Start":"Play Sound", "Stop":"Stop Sound"}

    def toXML(self, parent_root):
        """Store ObjectAction as ObjectChange node within one of several node
        types

        :param :py:class:xml.etree.ElementTree.Element parent_root
        """
        change_root = ET.SubElement(
            parent_root, "ObjectChange", attrib={"name": self["object_name"]}
        )
        trans_root = ET.SubElement(
            change_root, "Transition",
            attrib={"duration": str(self["duration"])})
        if "visible" in self:
            node = ET.SubElement(trans_root, "Visible")
            node.text = bool2text(self["visible"])
        if "placement" in self:
            if self["move_relative"]:
                node = ET.SubElement(trans_root, "MoveRel")
            else:
                node = ET.SubElement(trans_root, "Movement")
            self["placement"].toXML(node)
        if "color" in self:
            node = ET.SubElement(trans_root, "Color")
            node.text = "{},{},{}".format(*self["color"])
        if "scale" in self:
            node = ET.SubElement(trans_root, "Scale")
            node.text = str(self["scale"])
        if "sound_change" in self:
            node = ET.SubElement(
                trans_root, "Sound",
                attrib={"action": self.sound_xml_tags[self["sound_change"]]}
            )
        if "link_change" in self:
            node = ET.SubElement(trans_root, "LinkChange")
            ET.SubElement(node, self.link_xml_tags[self["link_change"]])
        return change_root

    @classmethod
    def fromXML(action_class, action_root):
        """Create ObjectAction from ObjectChange node

        :param :py:class:xml.etree.ElementTree.Element action_root
        """
        new_action = action_class()
        try:
            new_action["object_name"] = action_root.attrib["name"]
        except KeyError:
            raise BadW3DXML("ObjectChange node must have name attribute set")
        trans_root = action_root.find("Transition")
        if "duration" in trans_root.attrib:
            new_action["duration"] = float(trans_root.attrib["duration"])
        node = trans_root.find("Visible")
        if node is not None:
            new_action["visible"] = text2bool(node.text)
        node = trans_root.find("MoveRel")
        if node is not None:
            new_action["move_relative"] = True
        else:
            node = trans_root.find("Movement")
        if node is not None:
            new_action["move_relative"] = new_action.get(
                "move_relative", False)
            place_root = node.find("Placement")
            if place_root is None:
                raise BadW3DXML(
                    "Movement or MoveRel node requires Placement child node")
            new_action["placement"] = W3DPlacement.fromXML(place_root)
        node = trans_root.find("Color")
        if node is not None:
            try:
                new_action["color"] = text2tuple(node.text, evaluator=int)
            except InvalidArgument:
                new_action["color"] = (255, 255, 255)
        node = trans_root.find("Scale")
        if node is not None:
            try:
                new_action["scale"] = float(node.text.strip())
            except TypeError:
                new_action["scale"] = 1
        node = trans_root.find("Sound")
        if node is not None:
            raw_sound_change = node.text.strip()
            for key, value in new_action.sound_xml_tags.items():
                if raw_sound_change == value:
                    new_action["sound_change"] = key
                    break
            if "sound_change" not in new_action:
                raise BadW3DXML("Bad value for 'Sound' node in xml")
        node = trans_root.find("LinkChange")
        if node is not None:
            for key, value in new_action.link_xml_tags.items():
                if node.find(value) is not None:
                    new_action["link_change"] = key
                    break

        return new_action

    def _blender_object_selection(self, offset=0):
        blender_object_name = generate_blender_object_name(self["object_name"])
        self.selection_offset = 0
        return ["{}blender_object = scene.objects['{}']".format(
            "    " * offset, blender_object_name)]

    def generate_blender_logic(
            self, offset=0, time_condition=0, index_condition=None,
            click_condition=-1):
        return generate_object_action_logic(
            self, offset=offset, time_condition=time_condition,
            index_condition=index_condition,
            click_condition=click_condition)


class GroupAction(W3DAction):
    """An action causing a change to a group of W3DObjects

    :param str group_name: Name of group to change
    :param bool choose_random: Apply change to one object in group, selected
    randomly?
    :param float duration: Duration of transition in seconds
    :param bool visible: If not None, change visibility to this value
    :param W3DPlacement placement: If not None, move based on this placement
    :param bool move_relative: If True, move relative to original location
    :param tuple color: If not None, transition to this color
    :param float scale: If not None, scale by this factor
    :param str sound_change: One of "Play Sound" or "Stop Sound", which will
    play or stop sound associated with this group
    :param str link_change: One of "Enable", "Disable", "Activate", "Activate
    if enabled", which will affect this object's link
    """

    argument_validators = {
        "group_name": ReferenceValidator(
            ValidPyString(),
            ["groups"],
            help_string="Must be the name of a group"),
        "choose_random": IsBoolean(),
        "duration": IsNumeric(min_value=0),
        "visible": IsBoolean(),
        "placement": IsBoolean(),
        "move_relative": IsBoolean(),
        "color": ListValidator(
            IsInteger(min_value=0, max_value=255),
            required_length=3,
            help_string="Red, Green, Blue values"),
        "scale": IsNumeric(min_value=0),
        "sound_change": OptionValidator("Play Sound", "Stop Sound"),
        "link_change": OptionValidator(
            "Enable", "Disable", "Activate", "Activate if enabled")
    }

    default_arguments = {
        "duration": 1,
        "choose_random": False
    }

    link_xml_tags = {
        "Enable": "link_on", "Disable": "link_off", "Activate": "activate",
        "Activate if enabled": "activate_if_on"}

    def toXML(self, parent_root):
        """Store GroupAction as GroupRef node within one of several node types

        :param :py:class:xml.etree.ElementTree.Element parent_root
        """
        change_root = ET.SubElement(
            parent_root, "GroupRef", attrib={"name": self["group_name"]}
        )
        if not self.is_default("choose_random"):
            change_root.attrib["random"] = bool2text(self["choose_random"])
        trans_root = ET.SubElement(
            change_root, "Transition", attrib={
                "duration": str(self["duration"])})
        if "visible" in self:
            node = ET.SubElement(trans_root, "Visible")
            node.text = bool2text(self["visible"])
        if "placement" in self:
            if self["move_relative"]:
                node = ET.SubElement(trans_root, "MoveRel")
            else:
                node = ET.SubElement(trans_root, "Movement")
            self["placement"].toXML(node)
        if "color" in self:
            node = ET.SubElement(trans_root, "Color")
            node.text = "{},{},{}".format(*self["color"])
        if "scale" in self:
            node = ET.SubElement(trans_root, "Scale")
            node.text = str(self["scale"])
        if "sound_change" in self:
            node = ET.SubElement(
                trans_root, "Sound", attrib={"action", self["sound_change"]})
        if "link_change" in self:
            node = ET.SubElement(trans_root, "LinkChange")
            if self["link_change"] == "Enable":
                ET.SubElement(node, "link_on")
            elif self["link_change"] == "Disable":
                ET.SubElement(node, "link_off")
            elif self["link_change"] == "Activate":
                ET.SubElement(node, "activate")
            elif self["link_change"] == "Activate if enabled":
                ET.SubElement(node, "activate_if_on")
        return change_root

    @classmethod
    def fromXML(action_class, action_root):
        """Create GroupAction from GroupRef node

        :param :py:class:xml.etree.ElementTree.Element transition_root
        """
        new_action = action_class()
        try:
            new_action["group_name"] = action_root.attrib["name"]
        except KeyError:
            raise BadW3DXML("GroupRef node must have name attribute set")
        try:
            new_action["choose_random"] = action_root.attrib["random"]
        except KeyError:
            pass
        trans_root = action_root.find("Transition")
        if "duration" in trans_root.attrib:
            new_action["duration"] = float(trans_root.attrib["duration"])
        node = trans_root.find("Visible")
        if node is not None:
            new_action["visible"] = text2bool(node.text)
        node = trans_root.find("MoveRel")
        if node is not None:
            new_action["move_relative"] = True
        else:
            node = trans_root.find("Movement")
        if node is not None:
            new_action["move_relative"] = new_action.get(
                "move_relative", False)
            place_root = node.find("Placement")
            if place_root is None:
                raise BadW3DXML(
                    "Movement or MoveRel node requires Placement child node")
            new_action["placement"] = W3DPlacement.fromXML(place_root)
        node = trans_root.find("Color")
        if node is not None:
            try:
                new_action["color"] = text2tuple(node.text, evaluator=int)
            except InvalidArgument:
                new_action["color"] = (255, 255, 255)
        node = trans_root.find("Scale")
        if node is not None:
            try:
                new_action["scale"] = float(node.text.strip())
            except TypeError:
                new_action["scale"] = 1
        node = trans_root.find("Sound")
        if node is not None:
            new_action["sound_change"] = node.text.strip()
        node = trans_root.find("LinkChange")
        if node is not None:
            for key, value in new_action.link_xml_tags.items():
                if node.find(value) is not None:
                    new_action["link_change"] = key
                    break

        return new_action

    def _blender_object_selection(self, offset=0):
        blender_group_name = generate_group_name(self["group_name"])
        if self["choose_random"]:
            script_text = [
                "{}if (".format("    " * offset),
                "{}        'random_choice' not in own".format("    " * offset),
                "{}        or own['random_choice'] is None):".format(
                    "    " * offset),
                "{}    own['random_choice'] = random.choice({})".format(
                    "    " * offset, blender_group_name),
                "{}blender_object = scene.objects[".format("    " * offset),
                "{}    own['random_choice']]".format("    " * offset)
            ]
            self.selection_offset = 0
        else:
            script_text = [
                "{}for object_name in {}:".format(
                    "    " * offset, blender_group_name),
                "{}    blender_object = scene.objects[object_name]".format(
                    "    " * offset)
            ]
            self.selection_offset = 1
        return script_text

    def generate_blender_logic(
            self, offset=0, time_condition=0, index_condition=None,
            click_condition=-1):
        return generate_object_action_logic(
            self, offset=offset, time_condition=time_condition,
            index_condition=index_condition,
            click_condition=click_condition)


class TimelineAction(W3DAction):
    """Start or stop a timeline

    :param str timeline_name: Name of timeline to change
    :param str change: One of "Start", "Stop", "Continue", "Start if not
    started"
    """

    argument_validators = {
        "timeline_name": ReferenceValidator(
            ValidPyString(),
            ["timelines"],
            help_string="Must be the name of a timeline"),
        "change": OptionValidator(
            "Start", "Stop", "Continue", "Start if not started")
    }

    default_arguments = {}

    change_xml_tags = {
        "Start": "start", "Stop": "stop", "Continue": "continue",
        "Start if not started": "start_if_not_started"
    }

    def toXML(self, parent_root):
        """Store TimelineChange as TimerChange node within one of several node
        types

        :param :py:class:xml.etree.ElementTree.Element parent_root
        """
        try:
            change_root = ET.SubElement(
                parent_root, "TimerChange",
                attrib={"name": self["timeline_name"]})
        except KeyError:
            raise ConsistencyError(
                "TimelineAction must have timeline_name key set")
        try:
            ET.SubElement(change_root, self.change_xml_tags[self["change"]])
        except KeyError:
            raise ConsistencyError(
                "TimelineAction must have change key set")
        return change_root

    @classmethod
    def fromXML(action_class, timer_change_root):
        """Create TimelineAction from TimerChange node

        :param :py:class:xml.etree.ElementTree.Element transition_root
        """
        new_action = action_class()
        try:
            new_action["timeline_name"] = timer_change_root.attrib["name"]
        except KeyError:
            raise BadW3DXML(
                "TimerChange node must have name attribute set")
        for key, value in new_action.change_xml_tags.items():
            if timer_change_root.find(value) is not None:
                new_action["change"] = key
        if "change" not in new_action:
            raise BadW3DXML(
                "TimerChange node must have child specifying timeline change")

        return new_action

    def generate_blender_logic(
            self, offset=0, time_condition=0, index_condition=None,
            click_condition=-1):
        start_text = []
        cont_text = []
        end_text = []

        conditions = ActionCondition(offset=offset)
        self.end_time = time_condition
        conditions.add_time_condition(
            start_time=time_condition, end_time=self.end_time)
        if index_condition is not None:
            conditions.add_index_condition(index_condition)
        if click_condition > 0:
            conditions.add_click_condition(click_condition)

        start_text.append(conditions.start_string)
        cont_text.append(conditions.continue_string)
        end_text.append(conditions.end_string)

        start_text.append("{}index += 1".format(
            "    " * (conditions.offset + 1)))
        cont_text.append("{}remaining_time = {} - time".format(
            "    " * (conditions.offset + 1),
            self.end_time)
        )

        action = TimelineStarter(
            self["timeline_name"], self["change"],
            offset=(conditions.offset + 1)
        )
        start_text.append(action.start_string)
        cont_text.append(action.continue_string)
        end_text.append(action.end_string)
        return start_text + cont_text + end_text


class SoundAction(W3DAction):
    """Start or stop a sound

    :param str sound_name: Name of sound to change
    :param str change: One of Start or Stop"""

    argument_validators = {
        "sound_name": ReferenceValidator(
            ValidPyString(),
            ["sounds"],
            help_string="Must be the name of a sound"),
        "change": OptionValidator("Start", "Stop")
    }

    default_arguments = {
        "change": "Start"}

    def toXML(self, parent_root):
        """Store SoundAction as SoundRef node within one of several node
        types

        :param :py:class:xml.etree.ElementTree.Element parent_root
        """
        try:
            attrib = {"name": self["sound_name"]}
        except KeyError:
            raise ConsistencyError(
                "SoundAction must specify sound_name to act on")
        if not self.is_default("change"):
            attrib["action"] = self["change"]
        sound_root = ET.SubElement(parent_root, "SoundRef", attrib=attrib)
        return sound_root

    @classmethod
    def fromXML(action_class, soundref_root):
        """Create SoundAction from SoundRef node

        :param :py:class:xml.etree.ElementTree.Element soundref_root
        """
        new_action = action_class()
        try:
            new_action["sound_name"] = soundref_root.attrib["name"]
        except KeyError:
            raise BadW3DXML("SoundRef node must specify name attribute")
        if "action" in soundref_root.attrib:
            new_action["change"] = soundref_root.attrib["action"]

        return new_action

    def generate_blender_logic(
            self, offset=0, time_condition=0, index_condition=None,
            click_condition=-1):
        start_text = []
        cont_text = []
        end_text = []

        conditions = ActionCondition(offset=offset)
        self.end_time = time_condition
        conditions.add_time_condition(
            start_time=time_condition, end_time=self.end_time)
        if index_condition is not None:
            conditions.add_index_condition(index_condition)
        if click_condition > 0:
            conditions.add_click_condition(click_condition)

        start_text.append(conditions.start_string)
        cont_text.append(conditions.continue_string)
        end_text.append(conditions.end_string)

        start_text.append("{}index += 1".format(
            "    " * (conditions.offset + 1)))
        cont_text.append("{}remaining_time = {} - time".format(
            "    " * (conditions.offset + 1),
            self.end_time)
        )

        action = SoundChange(
            self["sound_name"], self["change"], conditions.offset + 1
        )
        start_text.append(action.start_string)
        cont_text.append(action.continue_string)
        end_text.append(action.end_string)
        sound_actuator = bpy.data.objects["AUDIO"].game.actuators[
            generate_blender_sound_name(self["sound_name"])]
        self.actuators.append(sound_actuator)
        return start_text + cont_text + end_text

class EventTriggerAction(W3DAction):
    """Enable or disable an event trigger

    :param str trigger_name: Name of trigger to enable/disable
    :param bool enable: Enable trigger?"""

    argument_validators = {
        "trigger_name": ReferenceValidator(
            ValidPyString(),
            ["triggers"],
            help_string="Must be the name of a trigger"
        ),
        "enable": IsBoolean()
    }

    default_arguments = {}

    def toXML(self, parent_root):
        """Store EventTriggerAction as Event node within one of several node
        types

        :param :py:class:xml.etree.ElementTree.Element parent_root
        """
        try:
            action_root = ET.SubElement(
                parent_root, "Event",
                attrib={
                    "name": str(self["trigger_name"]),
                    "enable": str(self["enable"])
                }
            )
        except KeyError:
            raise ConsistencyError(
                "EventTriggerAction must specify both trigger_name and enable")

        return action_root

    @classmethod
    def fromXML(action_class, event_root):
        """Create EventTriggerAction from Event node

        :param :py:class:xml.etree.ElementTree.Element event_root
        """
        new_action = action_class()
        try:
            new_action["trigger_name"] = event_root.attrib["name"]
        except KeyError:
            raise BadW3DXML("Event node must specify name attribute")
        try:
            new_action["enable"] = event_root.attrib["enable"]
        except KeyError:
            raise BadW3DXML("Event node must specify enable attribute")
        return new_action

    def generate_blender_logic(
            self, offset=0, time_condition=0, index_condition=None,
            click_condition=-1):
        start_text = []
        cont_text = []
        end_text = []

        conditions = ActionCondition(offset=offset)
        self.end_time = time_condition
        conditions.add_time_condition(
            start_time=time_condition, end_time=self.end_time)
        if index_condition is not None:
            conditions.add_index_condition(index_condition)
        if click_condition > 0:
            conditions.add_click_condition(click_condition)

        start_text.append(conditions.start_string)
        cont_text.append(conditions.continue_string)
        end_text.append(conditions.end_string)

        start_text.append("{}index += 1".format(
            "    " * (conditions.offset + 1)))
        cont_text.append("{}remaining_time = {} - time".format(
            "    " * (conditions.offset + 1),
            self.end_time)
        )

        action = TriggerEnabler(
            self["trigger_name"], self["enable"],
            offset=(conditions.offset + 1)
        )
        start_text.append(action.start_string)
        cont_text.append(action.continue_string)
        end_text.append(action.end_string)
        return start_text + cont_text + end_text


class MoveVRAction(W3DAction):
    """Move entire VR environment within virtual space

    :param bool relative: Move relative to current position?
    :param float duration: Duration of transition in seconds
    :param W3DPlacement placement: Where to move (position and orientation)
    """

    argument_validators = {
        "move_relative": IsBoolean(),
        "duration": IsNumeric(min_value=0),
        "placement": FeatureValidator(W3DPlacement)
    }

    default_arguments = {
        "move_relative": False,
        "duration": 0
    }

    def toXML(self, parent_root):
        """Store MoveVRAction as MoveCave node within one of several node
        types

        :param :py:class:xml.etree.ElementTree.Element parent_root
        """
        action_root = ET.SubElement(parent_root, "MoveCave")
        if not self.is_default("duration"):
            action_root.attrib["duration"] = str(self["duration"])
        try:
            relative = self["move_relative"]
        except KeyError:
            raise ConsistencyError(
                'MoveVRAction must specify a value for "relative" key')
        if relative:
            ET.SubElement(action_root, "Relative")
        else:
            ET.SubElement(action_root, "Absolute")
        try:
            self["placement"].toXML(action_root)
        except KeyError:
            raise ConsistencyError(
                'MoveVRAction must specify a value for "placement" key')
        return action_root

    @classmethod
    def fromXML(action_class, move_cave_root):
        """Create MoveVRAction from MoveCave node

        :param :py:class:xml.etree.ElementTree.Element transition_root
        """
        new_action = action_class()
        if "duration" in move_cave_root.attrib:
            new_action["duration"] = float(move_cave_root.attrib["duration"])
        if move_cave_root.find("Relative") is not None:
            new_action["move_relative"] = True
        elif move_cave_root.find("Absolute") is not None:
            new_action["move_relative"] = False
        else:
            raise BadW3DXML(
                "MoveCave node must contain either Absolute or Relative child")
        place_node = move_cave_root.find("Placement")
        if place_node is None:
            raise BadW3DXML(
                "MoveCave node must contain Placement child node")
        new_action["placement"] = W3DPlacement.fromXML(place_node)
        return new_action

    def _blender_object_selection(self, offset=0):
        self.selection_offset = 0
        return ["{}blender_object = scene.objects['CAMERA']".format(
            "    " * offset)]

    def generate_blender_logic(
            self, offset=0, time_condition=0, index_condition=None,
            click_condition=-1):
        return generate_object_action_logic(
            self, offset=offset, time_condition=time_condition,
            index_condition=index_condition,
            click_condition=click_condition)


class W3DResetAction(W3DAction):
    """Reset W3D to initial state
    """

    def toXML(self, parent_root):
        """Store W3DResetAction as Restart node within one of several node
        types

        :param :py:class:xml.etree.ElementTree.Element parent_root
        """
        action_root = ET.SubElement(parent_root, "Restart")
        return action_root

    @classmethod
    def fromXML(action_class, restart_root):
        """Create W3DRestartAction from Restart node

        :param :py:class:xml.etree.ElementTree.Element transition_root
        """
        return action_class()

    def generate_blender_logic(
            self, offset=0, time_condition=0, index_condition=None,
            click_condition=-1):
        start_text = []
        cont_text = []
        end_text = []

        conditions = ActionCondition(offset=offset)
        self.end_time = time_condition
        conditions.add_time_condition(
            start_time=time_condition, end_time=self.end_time)
        if index_condition is not None:
            conditions.add_index_condition(index_condition)
        if click_condition > 0:
            conditions.add_click_condition(click_condition)

        start_text.append(conditions.start_string)
        cont_text.append(conditions.continue_string)
        end_text.append(conditions.end_string)

        start_text.append("{}index += 1".format(
            "    " * (conditions.offset + 1)))
        cont_text.append("{}remaining_time = {} - time".format(
            "    " * (conditions.offset + 1),
            self.end_time)
        )

        action = SceneReset(
            offset=(conditions.offset + 1)
        )
        start_text.append(action.start_string)
        cont_text.append(action.continue_string)
        end_text.append(action.end_string)
        return start_text + cont_text + end_text
