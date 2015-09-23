"""Tools for implementing a CaveTrigger in blender"""

import warnings
try:
    import bpy
except ImportError:
    warnings.warn(
        "Module bpy not found. \
Loading pycave.cave_logic.blender_trigger as standalone")


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
        controller.module = "{}.{}".format(self.blender_object_name, self.name)
        return controller

    def create_control_property(self):
        """Create a boolean property to control this trigger

        Iff this property is set to True, the trigger will be activated. Triggers
        should not change anything within Blender unless this property is True.
        This property will have the same name as the trigger itself.
        """
        self.make_object_active()
        bpy.ops.object.game_property_new(
            type='BOOL',
            name=self.name
        )
        return self.blender_object.game.properties[self.name]

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
        actuator = self.blender_object.game.actuators[self.name]
        actuator.property = self.name
        actuator.value = "True"
        self.controller.link(actuator=actuator)
        return actuator

    def __init__(self, blender_object_name):
        self.blender_object_name = blender_object_name
        self.blender_object = self.get_object()
        # Create a unique name for this trigger
        trigger_count = 0
        while True:
            trigger_name = "trigger_{}".format(trigger_count)
            if trigger_name not in self.blender_object.game.controllers:
                break
            trigger_count += 1

        self.controller = self.create_controller()
        self.actuator = self.create_actuator()
        self.control_property = self.create_control_property()
        self.control_sensor = self.create_control_sensor()
        self.change_sensor = self.create_change_sensor()


class TimedTrigger(BlenderTrigger):
    """A Blender trigger which turns itself off after a specified duration

    TimedTriggers also create an associated Timer property in Blender which
    keeps track of how long they have been active"""

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

    def __init__(self, blender_object_name, duration):
        super(TimedTrigger, self).__init__(blender_object_name)
        self.duration = duration
        self.timer_name = "{}_timer".format(self.name)
        self.timer = self.create_timer_property()
        self.duration_sensor = self.create_duration_sensor(self.duration)
