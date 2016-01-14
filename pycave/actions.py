"""Tools for working with actions in the Cave

Here, actions refer generically to any discrete change in elements of a Cave
project
"""
#import warnings
import mathutils
import math
import xml.etree.ElementTree as ET
from .features import CaveFeature
from .placement import CavePlacement
from .validators import OptionListValidator, IsNumeric,  AlwaysValid,\
    IsNumericIterable
from .errors import BadCaveXML, InvalidArgument, ConsistencyError
from .xml_tools import bool2text, text2bool, text2tuple
from .names import generate_blender_object_name
#try:
#    import bpy
#except ImportError:
#    warnings.warn(
#        "Module bpy not found. Loading pycave.actions as standalone")

# TODO: Switch linear motion over to same style as angV


class CaveAction(CaveFeature):
    """An action causing a change in the Cave

    Note: This is mostly a dummy class. Provides fromXML to pass XML nodes to
    appropriate subclasses"""

    @staticmethod
    def fromXML(action_root):
        """Create CaveAction of appropriate subclass given xml root for any
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
            return MoveCaveAction.fromXML(action_root)
        elif action_root.tag == "Restart":
            return CaveResetAction.fromXML(action_root)
        else:
            raise BadCaveXML(
                "Indicated action {} is not a valid action type".format(
                    action_root.tag))


class ObjectAction(CaveAction):
    """An action causing a change to a CaveObject

    :param str object_name: Name of object to change
    :param float duration: Duration of transition in seconds
    :param bool visible: If not None, change visibility to this value
    :param CavePlacement placement: If not None, move based on this placement
    :param bool move_relative: If True, move relative to original location
    :param tuple color: If not None, transition to this color
    :param float scale: If not None, scale by this factor
    :param str sound_change: One of "Play Sound" or "Stop Sound", which will
    play or stop sound associated with this object
    :param str link_change: One of "Enable", "Disable", "Activate", "Activate
    if enabled", which will affect this object's link
    """

    argument_validators = {
        "object_name": AlwaysValid("Name of an object"),
        "duration": IsNumeric(min_value=0),
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
        "duration": 1,
        "move_relative": False
        }

    link_xml_tags = {
        "Enable": "link_on", "Disable": "link_off", "Activate": "activate",
        "Activate if enabled": "activate_if_on"}

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
                trans_root, "Sound", attrib={"action", self["sound_change"]})
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
            raise BadCaveXML("ObjectChange node must have name attribute set")
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
                raise BadCaveXML(
                    "Movement or MoveRel node requires Placement child node")
            new_action["placement"] = CavePlacement.fromXML(place_root)
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
        for key, value in new_action.link_xml_tags:
            if node.find(value) is not None:
                new_action["link_change"] = key
                break

        return new_action

    def _blender_object_selection(self):
        blender_object_name = generate_blender_object_name(self["object_name"])
        return "blender_object = scene.objects['{}']".format(
            blender_object_name)

    def generate_blender_logic(
            self, time_condition=0, index_condition=None, click_condition=-1):
        """Generate Python logic for implementing action

        :param float time_condition: Time at which action should start
        :param int index_condition: Index used to keep track of what actions
        have already been triggered, e.g. in a timeline of multiple actions"""
        script_text = [self._blender_object_selection()]

        #Specify conditions under which action should proceed
        start_conditional = []
        continue_conditional = []
        end_conditional = []
        self.end_time = self["duration"] + time_condition

        start_conditional.append("time >= {}".format(time_condition))
        continue_conditional.append("time >= {} and time < {}".format(
            time_condition, self.end_time))
        end_conditional.append("time >= {}".format(self.end_time))

        if index_condition is not None:
            start_conditional.append("index == {}".format(index_condition))
            continue_conditional.append("index >= {}".format(index_condition))

        if click_condition > 0:
            start_conditional.append("own['clicks'] == {}".format(
                click_condition))

        start_conditional = "if {}:".format(" and ".join(start_conditional))
        continue_conditional = "if {}:".format(
            " and ".join(continue_conditional))
        end_conditional = "if {}:".format(" and ".join(end_conditional))

        #Actions to take immediately when condition is first activated
        script_text.append(start_conditional)
        script_text.append("    index += 1")
        if "visible" in self:
            script_text.append("    blender_object.setVisible(True)")
        # Is the above line really correct?
        if "placement" in self and "rotation" in self["placement"]:
            vector = mathutils.Vector(
                self["placement"]["rotation"]["rotation_vector"])
            vector.normalize()
            if self["move_relative"]:
                if self["placement"][
                        "rotation"]["rotation_mode"] == "Axis":
                    axis = mathutils.Vector(
                        self["placement"]["rotation"]["rotation_vector"])
                    axis.normalize()
                    angle = math.radians(
                        self["placement"]["rotation"]["rotation_angle"])
                    script_text.append(
                        "    rotation = mathutils.Quaternion({}, {})".format(
                            tuple(vector), -angle))
                elif self["placement"][
                        "rotation"]["rotation_mode"] == "Normal":
                    # TODO: Is this the legacy behavior?
                    script_text.extend([
                        "    current_normal = mathutils.Vector((1, 0, 0))",
                        "    rotation = mathutils.Vector(",
                        "        {}).rotation_difference(".format(
                            tuple(vector)),
                        "        current_normal)"]
                    )
                elif self["placement"][
                        "rotation"]["rotation_mode"] == "LookAt":
                    script_text.extend([
                        "    look_direction = (",
                        "        blender_object.position +",
                        "        mathutils.Vector({}) -".format(
                            self["placement"]["position"]),
                        "        mathutils.Vector({})).normalized()".format(
                            self["placement"]["rotation"]["rotation_vector"]),
                        "    up_direction = mathutils.Vector(",
                        "        {}).normalized()".format(
                            self["placement"]["rotation"]["up_vector"]),
                        "    rotation_matrix = mathutils.Matrix.Rotation("
                        "    0, 4, (0, 0, 1))",
                        "    frame_y = look_direction",
                        "    frame_x = frame_y.cross(up_direction)",
                        "    frame_z = frame_x.cross(frame_y)",
                        "    rotation_matrix = mathutils.Matrix().to_3x3()",
                        "    rotation_matrix.col[0] = frame_x",
                        "    rotation_matrix.col[1] = frame_y",
                        "    rotation_matrix.col[2] = frame_z",
                        "    rotation = rotation_matrix.to_quaternion()"]
                    )
            else:  # Not move relative
                script_text.append(
                    "    orientation ="
                    "blender_object.orientation.to_quaternion()")

                if self["placement"][
                        "rotation"]["rotation_mode"] == "Axis":
                    angle = math.radians(
                        self["placement"]["rotation"]["rotation_angle"])
                    script_text.extend([
                        "    target_orientation = mathutils.Quaternion(",
                        "        {}, {})".format(tuple(vector), -angle),
                        "    rotation = (",
                        "        target_orientation.rotation_difference(",
                        "            orientation))"]
                    )

                elif self["placement"][
                        "rotation"]["rotation_mode"] == "Normal":
                    script_text.extend([
                        "    current_normal = mathutils.Vector((1, 0, 0))",
                        "    current_normal.rotate(",
                        "        blender_object.orientation)",
                        "    rotation = mathutils.Vector(",
                        "        {}).rotation_difference(".format(
                            tuple(vector)),
                        "        current_normal)"]
                    )

                elif self["placement"][
                        "rotation"]["rotation_mode"] == "LookAt":
                    script_text.extend([
                        "    look_direction = (",
                        "        mathutils.Vector({}) -".format(
                            self["placement"]["position"]),
                        "        mathutils.Vector({})).normalized()".format(
                            self["placement"]["rotation"]["rotation_vector"]),
                        "    up_direction = mathutils.Vector(",
                        "        {}).normalized()".format(
                            self["placement"]["rotation"]["up_vector"]),
                        "    rotation_matrix = mathutils.Matrix.Rotation("
                        "    0, 4, (0, 0, 1))",
                        "    frame_y = look_direction",
                        "    frame_x = frame_y.cross(up_direction)",
                        "    frame_z = frame_x.cross(frame_y)",
                        "    rotation_matrix = mathutils.Matrix().to_3x3()",
                        "    rotation_matrix.col[0] = frame_x",
                        "    rotation_matrix.col[1] = frame_y",
                        "    rotation_matrix.col[2] = frame_z",
                        "    rotation = rotation_matrix.to_quaternion()"]
                    )

            script_text.extend([
                "    blender_object['angV'] = (",
                "        rotation.angle /",
                "        {} *".format(
                    (self["duration"]*30, 1)[self["duration"] == 0]),
                # Don't know why the factor of 2, but it works
                "        rotation.axis)"]
            )

        #Actions to take at each timestep for which action is active
        script_text.append(continue_conditional)
        script_text.append("    remaining_time = {} - time".format(
            self.end_time)
        )
        if "visible" in self:
            script_text.append(
                "    remaining_alpha = {} - blender_object.color[3]".format(
                    int(self["visible"])
                )
            )
            script_text.append(
                "    delta_alpha = remaining_alpha/remaining_time/60"
            )  # Logic tick rate is 60 Hz
            script_text.extend([
                "    new_color = blender_object.color",
                "    new_color[3] += delta_alpha",
                "    blender_object.color = new_color"]
            )
        if "placement" in self and self["duration"] != 0:
            if "position" in self["placement"]:
                if self["move_relative"]:
                    script_text.append("    delta_pos = {}".format(
                        [coord/self["duration"]/60. for coord in
                            self["placement"]["position"]]
                        )
                    )
                else:
                    script_text.extend([
                        "    delta_pos = [",
                        "        ({}[i] - blender_object.position[i]".format(
                            list(self["placement"]["position"])),
                        "            )/remaining_time/60",
                        "        for i in range(3)]",
                        ]
                    )
                script_text.extend([
                    "    blender_object.position = [",
                    "        delta_pos[i] + blender_object.position[i]",
                    "        for i in range(3)]"]
                )
            if "rotation" in self["placement"]:
                script_text.append(
                    "    delta_rot = blender_object['angV']"
                )

                script_text.append(
                    "    blender_object.applyRotation(delta_rot)")
        if "color" in self:
            script_text.extend([
                "    delta_color = [",
                "        ({}[i] -".format(
                    [channel/255.0 for channel in self["color"]]),
                "            blender_object.color[i])/remaining_time/60",
                "        for i in range(3)]",
                "    delta_color.append(0)",
                "    blender_object.color = [",
                "        (blender_object.color[i] + delta_color[i])",
                "        for i in range(4)]"
                ]
            )
        if "scale" in self:
            script_text.extend([
                "    delta_scale = [",
                "        ({}[i] -".format([self["scale"]]*3),
                "            blender_object.scaling[i])/remaining_time/60",
                "        for i in range(3)]",
                "    blender_object.scaling = [",
                "        (blender_object.scaling[i] + delta_scale[i])",
                "        for i in range(3)]"
                ]
            )

        #Actions to take at end of action
        script_text.append(end_conditional)
        if "visible" in self:
            script_text.extend([
                "    new_color = blender_object.color",
                "    new_color[3] = {}".format(int(self["visible"])),
                "    blender_object.color = new_color"]
            )
            script_text.append("    blender_object.setVisible({})".format(
                self["visible"]))
        if "color" in self:
            script_text.extend([
                "    new_color = {}".format(
                    [channel/255.0 for channel in self["color"]]),
                "    new_color.append(blender_object.color[3])",
                "    blender_object.color = new_color"]
            )
        if "scale" in self:
            script_text.append(
                "    blender_object.scaling = {}".format([self["scale"]]*3)
            )
        if "placement" in self and self["duration"] == 0:
            if self["move_relative"]:
                if "position" in self["placement"]:
                    script_text.extend([
                        "    blender_object.position = [",
                        "        {}[i] + blender_object.position[i]".format(
                            self["placement"]["position"]),
                        "        for i in range(3)]"]
                    )
            else:
                if "position" in self["placement"]:
                    script_text.append(
                        "    blender_object.position = {}".format(
                            self["placement"]["position"]
                        )
                    )
                if "rotation" in self["placement"]:
                    if (self["placement"]["rotation"]["rotation_mode"] ==
                            "Axis"):
                        script_text.extend([
                            "    delta_rot = blender_object['angV']",
                            "    blender_object.applyRotation(delta_rot)"]
                        )

        return script_text


class GroupAction(CaveAction):
    """An action causing a change to a group of CaveObjects

    :param str group_name: Name of group to change
    :param bool choose_random: Apply change to one object in group, selected
    randomly?
    :param float duration: Duration of transition in seconds
    :param bool visible: If not None, change visibility to this value
    :param CavePlacement placement: If not None, move based on this placement
    :param bool move_relative: If True, move relative to original location
    :param tuple color: If not None, transition to this color
    :param float scale: If not None, scale by this factor
    :param str sound_change: One of "Play Sound" or "Stop Sound", which will
    play or stop sound associated with this group
    :param str link_change: One of "Enable", "Disable", "Activate", "Activate
    if enabled", which will affect this object's link
    """

    argument_validators = {
        "group_name": AlwaysValid("Name of a group"),
        "choose_random": AlwaysValid("Either true or false"),
        "duration": IsNumeric(min_value=0),
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
            change_root, "Transition", attrib={"duration": self["duration"]})
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
            raise BadCaveXML("GroupRef node must have name attribute set")
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
                raise BadCaveXML(
                    "Movement or MoveRel node requires Placement child node")
            new_action["placement"] = CavePlacement.fromXML(place_root)
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
        for key, value in new_action.link_xml_tags:
            if node.find(value) is not None:
                new_action["link_change"] = key
                break

        return new_action

    def blend(self):
        """Create representation of change in Blender"""
        raise NotImplementedError  # TODO


class TimelineAction(CaveAction):
    """Start or stop a timeline

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
        new_action = action_class
        try:
            new_action["timeline_name"] = timer_change_root.attrib["name"]
        except KeyError:
            raise BadCaveXML(
                "TimerChange node must have name attribute set")
        for key, value in new_action.change_xml_tags:
            if timer_change_root.find(value) is not None:
                new_action["change"] = key
        if "change" not in new_action:
            raise BadCaveXML(
                "TimerChange node must have child specifying timeline change")

        return new_action

    def blend(self):
        """Create representation of change in Blender"""
        self.blender_object_name = "_".join(
            (self["timeline_name"], "timeline"))
        #self.blender_trigger = BlenderTrigger(self.blender_object_name)
        #self.blender_action = ActivateTrigger(
        raise NotImplementedError  # TODO


class SoundAction(CaveAction):
    """Start or stop a sound

    :param str sound_name: Name of sound to change
    :param str change: One of Start or Stop"""

    argument_validators = {
        "sound_name": AlwaysValid("Name of a sound"),
        "change": OptionListValidator("Start", "Stop")
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
            raise BadCaveXML("SoundRef node must specify name attribute")
        if "action" in soundref_root.attrib:
            new_action["change"] = soundref_root.attrib["action"]

        return new_action

    def blend(self):
        """Create representation of change in Blender"""
        raise NotImplementedError  # TODO


class EventTriggerAction(CaveAction):
    """Enable or disable an event trigger

    :param str trigger_name: Name of trigger to enable/disable
    :param bool enable: Enable trigger?"""

    argument_validators = {
        "trigger_name": AlwaysValid("Name of a trigger"),
        "enable": AlwaysValid("Either true or false")
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
                    "name": self["trigger_name"], "enable": self["enable"]
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
            raise BadCaveXML("Event node must specify name attribute")
        try:
            new_action["enable"] = event_root.attrib["enable"]
        except KeyError:
            raise BadCaveXML("Event node must specify enable attribute")

    def blend(self):
        """Create representation of change in Blender"""
        raise NotImplementedError  # TODO


class MoveCaveAction(CaveAction):
    """Move entire Cave within virtual space

    :param bool relative: Move relative to current position?
    :param float duration: Duration of transition in seconds
    :param CavePlacement placement: Where to move (position and orientation)
    """

    argument_validators = {
        "relative": AlwaysValid("Either true or false"),
        "duration": IsNumeric(min_value=0),
        "placement": AlwaysValid("A CavePlacement object")
        }

    default_arguments = {
        "duration": 0
        }

    def toXML(self, parent_root):
        """Store MoveCaveAction as MoveCave node within one of several node
        types

        :param :py:class:xml.etree.ElementTree.Element parent_root
        """
        action_root = ET.SubElement(parent_root, "MoveCave")
        if not self.is_default("duration"):
            action_root.attrib["duration"] = str(self["duration"])
        try:
            relative = self["relative"]
        except KeyError:
            raise ConsistencyError(
                'MoveCaveAction must specify a value for "relative" key'
                )
        if relative:
            ET.SubElement(action_root, "Relative")
        else:
            ET.SubElement(action_root, "Absolute")
        try:
            self["placement"].toXML(action_root)
        except KeyError:
            raise ConsistencyError(
                'MoveCaveAction must specify a value for "placement" key'
                )
        return action_root

    @classmethod
    def fromXML(action_class, move_cave_root):
        """Create MoveCaveAction from MoveCave node

        :param :py:class:xml.etree.ElementTree.Element transition_root
        """
        new_action = action_class()
        if "duration" in move_cave_root.attrib:
            new_action["duration"] = move_cave_root.attrib["duration"]
        if move_cave_root.find("Relative") is not None:
            new_action["relative"] = True
        elif move_cave_root.find("Absolute") is not None:
            new_action["relative"] = False
        else:
            raise BadCaveXML(
                "MoveCave node must contain either Absolute or Relative child"
                )
        place_node = move_cave_root.find("Placement")
        if place_node is None:
            raise BadCaveXML(
                "MoveCave node must contain Placement child node"
                )
        new_action["placement"] = CavePlacement.fromXML(place_node)
        return new_action

    def blend(self):
        """Create representation of change in Blender"""
        raise NotImplementedError  # TODO


class CaveResetAction(CaveAction):
    """Reset Cave to initial state
    """

    def toXML(self, parent_root):
        """Store CaveResetAction as Restart node within one of several node
        types

        :param :py:class:xml.etree.ElementTree.Element parent_root
        """
        action_root = ET.SubElement(parent_root, "Restart")
        return action_root

    @classmethod
    def fromXML(action_class, restart_root):
        """Create CaveRestartAction from Restart node

        :param :py:class:xml.etree.ElementTree.Element transition_root
        """
        return action_class()

    def blend(self):
        """Create representation of change in Blender"""
        raise NotImplementedError  # TODO
