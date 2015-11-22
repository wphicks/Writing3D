"""Tools for activating an event in Blender"""

import warnings
try:
    import bpy
except ImportError:
    warnings.warn(
        "Module bpy not found. \
Loading pycave.cave_logic.blender_trigger as standalone")


def generate_project_root():
    """Generate a "ROOT" object which is used to activate initial actions"""
    if "ROOT" in bpy.data.objects:
        return bpy.data.objects["ROOT"]
    bpy.ops.object.add(
        type="EMPTY",
        layers=[layer == 20 for layer in range(1, 21)],
    )
    root_object = bpy.context.object
    bpy.context.scene.objects.active = root_object
    root_object.name = "ROOT"
    bpy.ops.object.game_property_new(
        type='BOOL',
        name="ROOT"
    )
    root_object.game.properties["ROOT"].value = True
    bpy.ops.logic.sensor_add(
        type="PROPERTY",
        object="ROOT",
        name="ROOT"
    )
    root_object.game.sensors[-1].name = "ROOT"

    root_object.game.sensors["ROOT"].property = "ROOT"
    root_object.game.sensors["ROOT"].value = "True"

    bpy.ops.logic.controller_add(
        type='LOGIC_AND',
        object="ROOT",
        name="ROOT")
    root_object.game.controllers[-1].name = "ROOT"
    controller = root_object.game.controllers["ROOT"]
    controller.link(sensor=root_object.game.sensors["ROOT"])

    bpy.ops.logic.actuator_add(
        type="PROPERTY",
        object="ROOT",
        name="run_once"
    )
    root_object.game.actuators[-1].name = "run_once"
    root_object.game.actuators["run_once"].property = "ROOT"
    root_object.game.actuators["run_once"].value = "False"

    controller.link(actuator=root_object.game.actuators["run_once"])

    return root_object


class BlenderTrigger(object):
    """A control element used to activate events within Blender

    Note that while this frequently corresponds to a single CaveFeature, it may
    correspond to part of a CaveFeature or several CaveFeatures. For instance,
    a CaveTimeline constitutes a single BlenderTrigger, which will trigger
    multiple events.

    :param str blender_object_name: The name of the blender object to which
    trigger is attached
    :ivar blender_object: The blender object to which this trigger is attached
    :ivar name: A unique (to the associated object) name for this trigger
    """

    def get_object(self):
        """Return the Blender object associated with this trigger

        :note Subclasses may create the object if necessary but should check to
        see if the object already exists
        """
        blender_object = bpy.data.objects[self.blender_object_name]
        return blender_object

    def make_object_active(self):
        """Make this trigger's object the currently active object"""
        bpy.context.scene.objects.active = self.blender_object
        return self.blender_object

    def create_controller(self):
        """Create a Python controller for this trigger

        This controller will have the same name as the trigger itself
        """
        self.make_object_active()
        bpy.ops.logic.controller_add(
            type='PYTHON',
            object=self.blender_object_name,
            name=self.name)
        controller = self.blender_object.game.controllers[self.name]
        controller.mode = "MODULE"
        controller.module = "{}.activate_{}".format(
            self.blender_object_name, self.name)
        return controller

    def create_control_property(self):
        """Create a boolean property to control this trigger

        Iff this property is set to True, the trigger will be activated.
        Triggers should not change anything within Blender unless this property
        is True.  This property will have the same name as the trigger itself.
        """
        self.make_object_active()
        bpy.ops.object.game_property_new(
            type='STRING',
            name=self.name
        )
        control_property = self.blender_object.game.properties[self.name]
        control_property.value = "Stop"
        return control_property

    def create_control_sensor(self):
        """Create a sensor to detect when control property is set to True

        This sensor will have the same name as the trigger itself.
        """
        self.make_object_active()
        bpy.ops.logic.sensor_add(
            type="PROPERTY",
            object=self.blender_object_name,
            name=self.name
        )
        self.blender_object.game.sensors[-1].name = self.name
        sensor = self.blender_object.game.sensors[self.name]
        sensor.property = self.name
        sensor.value = "True"
        self.controller.link(sensor=sensor)
        return sensor

    def create_change_sensor(self):
        """Create a sensor to detect when control property is changed

        This sensor will be named [NAME]_change where [NAME] is the name of the
        trigger.
        """
        self.make_object_active()
        sensor_name = "{}_change".format(self.name)
        bpy.ops.logic.sensor_add(
            type="PROPERTY",
            object=self.blender_object_name,
            name=sensor_name
        )
        sensor = self.blender_object.game.sensors[sensor_name]
        sensor.property = self.name
        sensor.evaluation_type = "PROPCHANGED"
        self.controller.link(sensor=sensor)
        return sensor

    def create_actuator(self):
        """Create an actuator that will set control property to desired
        value

        This actuator will have the same name as the trigger itself.
        """
        self.make_object_active()
        bpy.ops.logic.actuator_add(
            type="PROPERTY",
            object=self.blender_object_name,
            name=self.name
        )
        self.blender_object.game.actuators[-1].name = self.name
        actuator = self.blender_object.game.actuators[self.name]
        actuator.property = self.name
        actuator.value = "True"
        self.controller.link(actuator=actuator)
        return actuator

    def create_pause_index_property(self):
        """Create a property which will keep track of timer value when last
        stopped

        This property is used to facilitate pausing of an action or series of
        actions. For instance, when a timeline is stopped, the current action
        index is stored. If the timeline is then told to continue, the action
        index will be set to the stored index, allowing execution to continue
        from that point.  This property will have a name specified by the
        pause_index_name attribute of this object. See also the
        create_pause_time_property method for TimedTrigger objects.
        """
        self.make_object_active()
        bpy.ops.object.game_property_new(
            type='INT',
            name=self.pause_index_name
        )
        pause_property = self.blender_object.game.properties[
            self.pause_index_name]
        pause_property.value = 0
        return pause_property

    def create_index_property(self):
        """Create a property that keeps track of how many actions have been
        triggered by this trigger

        This index should increment with each action associated with this
        trigger in order to keep track of which actions have already been
        triggered. This is mostly useful for preventing timed actions from
        being repeatedly triggered but may be used for other cases in which a
        sensor remains active after the associated action has already occurred.
        """
        self.make_object_active()
        property_name = "{}_index".format(self.name)
        bpy.ops.object.game_property_new(
            type='INT',
            name=property_name
        )
        index_property = self.blender_object.game.properties[property_name]
        index_property.value = 0
        return index_property

    def start_immediately(self):
        """Causes trigger to start immediately when project starts"""
        root_object = generate_project_root()
        self.controller.link(sensor=root_object.game.sensors["ROOT"])
        self.add_to_script_body("""
    root_sensor = cont.sensors["ROOT"]
    if root_sensor.positive:
        control_actuator.value = "True"
        cont.activate(control_actuator)
        """)

    def get_script_template_values(self):
        """Generate a dictionary used to fill in templates which will create
        the control script for this trigger"""
        return {
            "name": self.name,
            "control_sensor": self.control_sensor.name,
            "change_sensor": self.change_sensor.name,
            "index_property": self.index_property.name,
            "control_actuator": self.actuator.name,
            "pause_index_property": self.pause_index_name
        }

    def add_to_script_body(self, script_string, section=0):
        """Append to body of script (after header but before footer)"""
        while len(self.body) <= section:
            self.body.append([])
        self.body[section].append(script_string)

    def write_to_script(self):
        """Write this trigger to the Python script associated with its
        object"""
        script_name = ".".join((self.blender_object_name, "py"))
        if script_name not in bpy.data.texts:
            bpy.data.texts.new(script_name)
            bpy.data.texts[script_name].write("""
import bge
from mathutils import Quaternion""")
        script = bpy.data.texts[script_name]
        template_values = self.get_script_template_values()
        script.write("\n".join(self.header).format(**template_values))
        script.write("\n".join(
            "\n".join(section) for section in self.body
            ).format(**template_values)
        )
        script.write("\n".join(self.footer).format(**template_values))
        return script

    def __init__(self, blender_object_name):
        self.blender_object_name = blender_object_name
        self.blender_object = self.get_object()
        # Create a unique name for this trigger
        trigger_count = 0
        while True:
            self.name = "trigger_{}".format(trigger_count)
            if self.name not in self.blender_object.game.controllers:
                break
            trigger_count += 1

        self.controller = self.create_controller()
        self.actuator = self.create_actuator()
        self.control_property = self.create_control_property()
        self.control_sensor = self.create_control_sensor()
        self.change_sensor = self.create_change_sensor()
        self.index_property = self.create_index_property()
        self.pause_index_name = "{}_pausei".format(self.name)
        self.create_pause_index_property()

        self.header = ["""
def activate_{name}(cont):
    scene = bge.logic.getCurrentScene()
    own = cont.owner
    sensor = cont.sensors["{control_sensor}"]
    change_sensor = cont.sensors["{change_sensor}"]
    control_actuator = cont.actuators["{control_actuator}"]
"""]
        self.footer = [""]
        self.body = [[], []]
        # Note: Body is divided up into multiple sections to allow for
        # separation of execution when order matters. For instance, after
        # resetting the timer in a timed trigger, no timed actions should be
        # activated until the next frame.
        self.add_to_script_body("""
    if sensor.positive and change_sensor.positive:
        own["{index_property}"] = own["{pause_index_property}"]
        """)


class TimedTrigger(BlenderTrigger):
    """A Blender trigger which turns itself off after a specified duration

    TimedTriggers also create an associated Timer property in Blender which
    keeps track of how long they have been active"""

    def create_pause_time_property(self):
        """Create a property which will keep track of timer value when last
        stopped

        This property is used to facilitate pausing of an action or series of
        actions. For instance, when a timeline is stopped, the current time is
        stored. If the timeline is then told to continue, the timer will be set
        to the stored time, allowing execution to continue from that point.
        This property will have a name specified by the pause_time_name
        attribute of this object. See also the create_pause_index_property
        method.
        """
        self.make_object_active()
        bpy.ops.object.game_property_new(
            type='FLOAT',
            name=self.pause_time_name
        )
        pause_property = self.blender_object.game.properties[
            self.pause_time_name]
        pause_property.value = 0
        return pause_property

    def create_timer_property(self):
        """Create a property which will keep track of time since activation

        This property will have a name specified by the timer_name attribute of
        this object.
        """
        self.make_object_active()
        bpy.ops.object.game_property_new(
            type='TIMER',
            name=self.timer_name
        )
        return self.blender_object.game.properties[self.timer_name]

    def create_time_sensor(self, time):
        """Create a sensor which will register True when the specified time is
        exceeded by the timer property

        The sensor will have a unique name of the form [TIMER_NAME]_#, where
        [TIMER_NAME] is specified by the timer_name attribute of this object,
        and # is a unique number
        """
        self.make_object_active()
        sensor_count = 0
        while True:
            sensor_name = "{}_{}".format(self.timer_name, sensor_count)
            if sensor_name not in self.blender_object.game.sensors:
                break
            sensor_count += 1
        bpy.ops.logic.sensor_add(
            type="PROPERTY",
            object=self.blender_object_name,
            name=sensor_name
        )
        sensor = self.blender_object.game.sensors[sensor_name]
        sensor.property = self.timer_name
        sensor.evaluation_type = "PROPINTERVAL"
        # Note: In Blender 7.1, this can be replaced by a direct Greater Than
        # evaluation
        sensor.value_min = "{}".format(time)
        sensor.value_max = "9999999"
        self.controller.link(sensor=sensor)

        return sensor

    def get_script_template_values(self):
        template_values = super(
            TimedTrigger, self).get_script_template_values()
        template_values.update({
            "duration_sensor": self.duration_sensor.name,
            "timer_name": self.timer_name,
            "pause_time_property": self.pause_time_name
            }
        )
        return template_values

    def __init__(self, blender_object_name, duration):
        super(TimedTrigger, self).__init__(blender_object_name)
        self.duration = duration
        self.timer_name = "{}_timer".format(self.name)
        self.pause_time_name = "{}_pauset".format(self.name)
        self.timer = self.create_timer_property()
        self.duration_sensor = self.create_time_sensor(self.duration)
        self.create_pause_time_property()

        self.header.append("""
    duration_sensor = cont.sensors["{duration_sensor}"]
    """)

        self.add_to_script_body("""
    if sensor.positive and change_sensor.positive:
        own["{timer_name}"] = own["{pause_time_property}"]
        return
        """, section=1)

        self.footer.append("""
    if sensor.positive and duration_sensor.positive:
        control_actuator.value = "False"
        cont.activate(control_actuator)
    """)
