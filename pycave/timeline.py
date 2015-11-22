"""Tools for working with timelines in Cave projects
"""
import warnings
import xml.etree.ElementTree as ET
from collections import MutableSequence
from .features import CaveFeature
from .actions import CaveAction
from .validators import AlwaysValid
from .errors import ConsistencyError, BadCaveXML
from .xml_tools import bool2text, text2bool
try:
    import bpy
except ImportError:
    warnings.warn(
        "Module bpy not found. Loading pycave.actions as standalone")


def generate_blender_timeline_name(string):
    return "{}_timeline".format(string)


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
            if self.sort_key(new_item) < self.sort_key(item):
                self._data.insert(index, new_item)
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


class CaveTimeline(CaveFeature):
    """Represent timeline for choreography of actions in the Cave

    :param str name: Name of timeline
    :param bool start_immediately: Start timeline when project starts?
    :param list actions: A list of two-element tuples specifying (start time
    for action, CaveAction)
    """
    argument_validators = {
        "name": AlwaysValid(
            help_string="A string specifying a unique name for this timeline"),
        "start_immediately": AlwaysValid(help_string="Either true or false"),
        "actions": AlwaysValid(
            help_string="A list of (float, CaveAction) tuples")
        }
    default_arguments = {
        "start_immediately": True
        }

    def __init__(self, *args, **kwargs):
        super(CaveTimeline, self).__init__(*args, **kwargs)
        if "actions" not in self:
            self["actions"] = SortedList()
        else:
            self["actions"] = SortedList(self["actions"])

    def toXML(self, all_timelines_root):
        """Store CaveTimeline as Timeline node within TimelineRoot node
        """
        try:
            timeline_attribs = {"name": self["name"]}
        except KeyError:
            raise ConsistencyError("CaveTimeline must specify a name")
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
        """Create CaveTimeline from Timeline node of Cave XML

        :param :py:class:xml.etree.ElementTree.Element timeline_root
        """
        new_timeline = timeline_class()
        try:
            new_timeline["name"] = timeline_root.attrib["name"]
        except KeyError:
            raise BadCaveXML(
                "Timeline node must specify name attribute")
        if "start-immediately" in timeline_root.attrib:
            new_timeline["start_immediately"] = text2bool(timeline_root.attrib[
                "start-immediately"])
        for timed_action in timeline_root.findall("TimedActions"):
            try:
                action_time = float(timed_action.attrib["seconds-time"])
            except (KeyError, ValueError):
                raise BadCaveXML(
                    "TimedActions node must specify numeric seconds-time "
                    "attribute")
            for child in timed_action.getchildren():
                new_timeline["actions"].add(
                    (action_time, CaveAction.fromXML(child)))

        return new_timeline

    def blend(self):
        """Create representation of CaveTimeline in Blender"""
        blender_object_name = generate_blender_timeline_name(self["name"])
        #Create EMPTY object to represent timeline
        bpy.ops.object.add(
            type="EMPTY",
            layers=[layer == 20 for layer in range(1, 21)],
        )
        timeline_object = bpy.context.object
        bpy.context.scene.objects.active = timeline_object
        timeline_object.name = blender_object_name

        #Create property to start, continue, or stop timeline
        bpy.ops.object.game_property_new(
            type='STRING',
            name='status'
        )
        if self["start_immediately"]:
            timeline_object.game.properties["status"].value = "Start"
        else:
            timeline_object.game.properties["status"].value = "Stop"

        #Create property sensor to initiate timeline
        bpy.ops.logic.sensor_add(
            type="PROPERTY",
            object=blender_object_name,
            name="start_sensor"
        )
        timeline_object.game.sensors[-1].name = "start_sensor"
        start_sensor = timeline_object.game.sensors["start_sensor"]
        start_sensor.property = "status"
        start_sensor.value = "Start"

        #Create property sensor to activate actions
        bpy.ops.logic.sensor_add(
            type="PROPERTY",
            object=blender_object_name,
            name="active_sensor"
        )
        timeline_object.game.sensors[-1].name = "active_sensor"
        active_sensor = timeline_object.game.sensors["active_sensor"]
        active_sensor.use_pulse_true_level = True
        active_sensor.frequency = 1
        active_sensor.property = "status"
        active_sensor.value = "Continue"

        #Create property sensor to pause timeline
        bpy.ops.logic.sensor_add(
            type="PROPERTY",
            object=blender_object_name,
            name="stop_sensor"
        )
        timeline_object.game.sensors[-1].name = "stop_sensor"
        stop_sensor = timeline_object.game.sensors["stop_sensor"]
        stop_sensor.property = "status"
        stop_sensor.value = "Stop"

        #Create controller to effect timeline actions
        bpy.ops.logic.controller_add(
            type='PYTHON',
            object=blender_object_name,
            name="activate")
        controller = timeline_object.game.controllers["activate"]
        controller.mode = "MODULE"
        controller.module = "{}.activate".format(blender_object_name)
        controller.link(sensor=start_sensor)
        controller.link(sensor=active_sensor)
        controller.link(sensor=stop_sensor)

        return timeline_object

    def write_blender_logic(self):
        blender_object_name = generate_blender_timeline_name(self["name"])

        #Create controller script
        script_name = ".".join((blender_object_name, "py"))
        bpy.data.texts.new(script_name)
        script = bpy.data.texts[script_name]
        script_text = [
            "import bge",
            "from time import monotonic",
            "def activate(cont):",
            "    scene = bge.logic.getCurrentScene()",
            "    own = cont.owner",
            "    status = own['status']",
            "    if status == 'Start':",
            "        own['start_time'] = monotonic()",
            "        own['action_index'] = 0",
            "        own['offset_time'] = 0",
            "        own['offset_index'] = 0",
            "        own['status'] = 'Continue'",
            "    if status == 'Stop':",
            "        try:",
            "            own['offset_time'] = monotonic() - own['start_time']",
            "            own['offset_index'] = own['action_index']",
            "        except KeyError:",
            "            pass",
            "    if status == 'Continue':",
            "        try:",
            "            if own['offset_time'] != 0:",
            "                own['start_time'] = (",
            "                    monotonic() - own['offset_time'])",
            "                own['offset_time] = 0",
            "        except KeyError:",
            "            raise RuntimeError(",
            "                'Must start timeline before continue is used')",
            "        time = monotonic() - own['start_time']",
            "        index = own['offset_index'] + own['action_index']"
        ]
        action_index = 0
        for time, action in self["actions"]:
            script_text.extend(
                ["".join(("        ", line)) for line in
                    action.generate_blender_logic(
                        time_condition=time,
                        index_condition=action_index
                    )]
            )
            script_text.append("        index += 1")
            action_index += 1
        script_text.append("        own['action_index'] = index")
        script_text.append("        own['offset_index'] = 0")
        script.write("\n".join(script_text))
