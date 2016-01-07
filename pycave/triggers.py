"""Tools for working with particular Cave events that can trigger actions

Here, triggers are any events within the Cave that can be used to start another
action. For example, when the viewer reaches a particular location, a timeline
can be started."""
import warnings
import math
import xml.etree.ElementTree as ET
from .features import CaveFeature
from .actions import CaveAction
from .validators import AlwaysValid, IsNumeric, IsNumericIterable, \
    OptionListValidator
from .errors import ConsistencyError, BadCaveXML, InvalidArgument
from .xml_tools import bool2text, text2tuple, text2bool
from .names import generate_trigger_name, generate_enabled_name, \
    generate_blender_object_name
try:
    import bpy
except ImportError:
    warnings.warn(
        "Module bpy not found. Loading pycave.actions as standalone")


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
        trigger_name = generate_trigger_name(self["name"])
        enabled_name = generate_enabled_name(trigger_name)
        #Create EMPTY object to represent trigger
        bpy.ops.object.add(
            type="EMPTY",
            layers=[layer == 20 for layer in range(1, 21)],
        )
        trigger_object = bpy.context.object
        bpy.context.scene.objects.active = trigger_object
        trigger_object.name = trigger_name

        #Create property to start, continue, or stop trigger actions
        bpy.ops.object.game_property_new(
            type='STRING',
            name='status'
        )
        trigger_object.game.properties["status"].value = "Stop"

        #Create property sensor to initiate trigger actions
        bpy.ops.logic.sensor_add(
            type="PROPERTY",
            object=trigger_name,
            name="start_sensor"
        )
        trigger_object.game.sensors[-1].name = "start_sensor"
        start_sensor = trigger_object.game.sensors["start_sensor"]
        start_sensor.property = "status"
        start_sensor.value = "Start"

        #Create property sensor to continue actions
        bpy.ops.logic.sensor_add(
            type="PROPERTY",
            object=trigger_name,
            name="active_sensor"
        )
        trigger_object.game.sensors[-1].name = "active_sensor"
        active_sensor = trigger_object.game.sensors["active_sensor"]
        active_sensor.use_pulse_true_level = True
        active_sensor.frequency = 1
        active_sensor.property = "status"
        active_sensor.value = "Continue"

        #Create property sensor to stop trigger execution
        bpy.ops.logic.sensor_add(
            type="PROPERTY",
            object=trigger_name,
            name="stop_sensor"
        )
        trigger_object.game.sensors[-1].name = "stop_sensor"
        stop_sensor = trigger_object.game.sensors["stop_sensor"]
        stop_sensor.property = "status"
        stop_sensor.value = "Stop"

        #Create controller to effect trigger actions
        bpy.ops.logic.controller_add(
            type='PYTHON',
            object=trigger_name,
            name="activate")
        controller = trigger_object.game.controllers["activate"]
        controller.mode = "MODULE"
        controller.module = "{}.activate".format(trigger_name)
        controller.link(sensor=start_sensor)
        controller.link(sensor=active_sensor)
        controller.link(sensor=stop_sensor)

        #Enable or disable trigger on main camera
        camera_object = bpy.data.objects["CAMERA"]
        bpy.context.scene.objects.active = camera_object
        bpy.ops.object.game_property_new(
            type='BOOLEAN',
            name=enabled_name
        )
        camera_object.game.properties[enabled_name].value = self["enabled"]

        #Create property sensor to enable position detection
        bpy.ops.logic.sensor_add(
            type="PROPERTY",
            object="CAMERA",
            name=enabled_name
        )
        camera_object.game.sensors[-1].name = enabled_name
        enable_sensor = camera_object.game.sensors[enabled_name]
        enable_sensor.use_pulse_true_level = True
        enable_sensor.frequency = 1
        enable_sensor.property = enabled_name
        enable_sensor.value = self["enabled"]

        #Create controller to activate trigger actions
        bpy.ops.logic.controller_add(
            type='PYTHON',
            object="CAMERA",
            name=trigger_name)
        controller = trigger_object.game.controllers[trigger_name]
        controller.mode = "MODULE"
        controller.module = "{}.detect_event".format(trigger_name)
        controller.link(sensor=enabled_name)

        return trigger_object

    def write_blender_logic(self):
        trigger_name = generate_trigger_name(self["name"])
        enabled_name = generate_enabled_name(trigger_name)

        #Create controller script
        script_name = ".".join((trigger_name, "py"))
        bpy.data.texts.new(script_name)
        script = bpy.data.texts[script_name]
        script_text = [
            "import bge",
            "from group_defs import *",
            "import mathutils",
            "from time import monotonic",
            "def activate(cont):",
            "    scene = bge.logic.getCurrentScene()",
            "    own = cont.owner",
            "    status = own['status']",
            "    if not own['enabled']:",
            "        own['status'] = 'Stop'",
            "        return",
            "    if status == 'Start':",
            "        own['start_time'] = monotonic()",
            "        own['action_index'] = 0",
            "        own['status'] = 'Continue'",
            "    if status == 'Continue':",
            "        try:",
            "            time = monotonic() - own['start_time']",
            "            index = own['action_index']"
            "        except KeyError:",
            "            raise RuntimeError(",
            "                'Must activate trigger before continue is used')",
        ]
        action_index = 0
        max_time = self["duration"]
        for action in self["actions"]:
            script_text.extend(
                ["".join(("        ", line)) for line in
                    action.generate_blender_logic(
                        time_condition=0,
                        index_condition=action_index
                    )]
            )
            action_index += 1
            max_time = max(max_time, action.end_time)
        script_text.append("        own['action_index'] = index")
        script_text.append("        own['offset_index'] = 0")
        script_text.append("        if time >= {}:".format(max_time))
        script_text.append("            own['status'] = 'Stop'")
        script_text.append(
            "            scene.cameras['CAMERA'][{}] = {}".format(
                enabled_name, self["remain_enabled"]))
        script.write("\n".join(script_text))


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

    def write_blender_logic(self):
        super(HeadPositionTrigger, self).write_blender_logic()
        trigger_name = generate_trigger_name(self["name"])

        #Create script to detect head position
        script_name = ".".join((trigger_name, "py"))
        script = bpy.data.texts[script_name]
        script_text = [
            "\ndef detect_event(cont):",
            "    scene = bge.logic.getCurrentScene()",
            "    own = cont.owner",
            "    position = own.position",
            "    inside = True",
            "    corners = {}".format(
                zip(self["box"]["corner1"], self["box"]["corner2"])),
            "    for i in range({}):".format((3, 2)[self["box"]["ignore_y"]]),
            "        if (",
            "                position[i] < min(corners[i]) or",
            "                position[i] > max(corners[i])):",
            "            inside = False",
            "            break",
            "    if {}:".format(
                ("not inside", "inside")[
                    self["box"]["direction"] == "Inside"]),
            "        trigger = scene.objects['{}']".format(
                trigger_name),
            "        trigger['status'] = 'Start'"
        ]
        script.write("\n".join(script_text))


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

    def write_blender_logic(self):
        super(LookAtPoint, self).write_blender_logic()
        trigger_name = generate_trigger_name(self["name"])

        #Create script to detect head position
        script_name = ".".join((trigger_name, "py"))
        script = bpy.data.texts[script_name]
        script_text = [
            "\ndef detect_event(cont):",
            "    scene = bge.logic.getCurrentScene()",
            "    own = cont.owner",
            "    if own.pointInsideFrustrum({}):".format(
                tuple(self["point"])),
            "        trigger = scene.objects['{}']".format(
                trigger_name),
            "        trigger['status'] = 'Start'"
        ]
        script.write("\n".join(script_text))


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

    def write_blender_logic(self):
        super(LookAtDirection, self).write_blender_logic()
        trigger_name = generate_trigger_name(self["name"])

        #Create script to detect head position
        script_name = ".".join((trigger_name, "py"))
        script = bpy.data.texts[script_name]
        script_text = [
            "\ndef detect_event(cont):",
            "    scene = bge.logic.getCurrentScene()",
            "    own = cont.owner",
            "    cam_dir = (own.matrix_world.to_quaternion() *",
            "        mathutils.Vector((0, 1, 0)))",
            "    target_dir = mathutils.Vector({})".format(
                tuple(self["direction"])),
            "    angle = abs(cam_dir.angle(target_dir, 1.571))",
            "    if angle < {}:".format(
                math.radians(self["angle"])),
            "        trigger = scene.objects['{}']".format(
                trigger_name),
            "        trigger['status'] = 'Start'"
        ]
        script.write("\n".join(script_text))


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

    def write_blender_logic(self):
        super(LookAtObject, self).write_blender_logic()
        trigger_name = generate_trigger_name(self["name"])

        #Create script to detect head position
        script_name = ".".join((trigger_name, "py"))
        script = bpy.data.texts[script_name]
        script_text = [
            "\ndef detect_event(cont):",
            "    scene = bge.logic.getCurrentScene()",
            "    own = cont.owner",
            "    position = scene.objects[{}].position".format(
                generate_blender_object_name(self["object"])),
            "    if own.pointInsideFrustrum({}):".format(
                tuple(self["point"])),
            "        trigger = scene.objects['{}']".format(
                trigger_name),
            "        trigger['status'] = 'Start'"
        ]
        script.write("\n".join(script_text))


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

    def write_blender_logic(self):
        super(MovementTrigger, self).write_blender_logic()
        trigger_name = generate_trigger_name(self["name"])

        #Create script to detect head position
        script_name = ".".join((trigger_name, "py"))
        script = bpy.data.texts[script_name]
        script_text = [
            "\ndef detect_event(cont):",
            "    scene = bge.logic.getCurrentScene()",
            "    own = cont.owner",
            "    corners = {}".format(
                zip(self["box"]["corner1"], self["box"]["corner2"]))
        ]
        if self["type"] == "Single Object":
            script_text.append(
                "    all_objects = ['{}']".format(
                    self["object_name"])
            )
        else:
            script_text.append(
                "    all_objects = {}".format(
                    self["object_name"])
            )
        script_text.extend([
            "    all_objects = [",
            "scene.objects[object_name] for object_name in all_objects",
            "    in_region = {}".format(
                self["type"] == "Group(All)"),
            "    for object_ in all_objects:",
            "        position = object_.position",
            "        in_region = (in_region {}".format(
                ("or", "and")[self["type"] == "Group(All)"]),
            "            {}(position[i] < min(corners[i]) or".format(
                ("", "not ")[self["box"]["direction"] == "Inside"]),
            "               position[i] > max(corners[i])))",
            "    if in_region:",
            "        trigger = scene.objects['{}']".format(
                trigger_name),
            "        trigger['status'] = 'Start'"
        ])
        script.write("\n".join(script_text))


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
