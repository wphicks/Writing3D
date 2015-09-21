"""Tools for creating all "game" logic associated with a Cave project
"""
import warnings
try:
    import bpy
except ImportError:
    warnings.warn(
        "Module bpy not found. Loading pycave.cave_logic as standalone")

HEADER = """import bge
"""


START_IMMEDIATELY = """
"""


BASE_FUNCTION = """
def activate_{cont_name}(cont):
    print("\\n{cont_name}")
    scene = bge.logic.getCurrentScene()
    own = cont.owner
    print(own["{cont_name}_time"])
    sensor = cont.sensors["{cont_name}"]
    time_sensor = cont.sensors["{cont_name}_time"]
    change_sensor = cont.sensors["{cont_name}_change"]
    property_actuator = cont.actuators["{cont_name}"]
    print("Controller active:", sensor.positive)
    print("Controller changed:", change_sensor.positive)
    print("Duration exceeded:", time_sensor.positive)
    if {start_immediately}:
        root_sensor = cont.sensors["ROOT"]
        if root_sensor.positive:
            own["{cont_name}_time"] = 0.0
            own["{cont_name}_ind"] = 0
            property_actuator.value = "True"
            cont.activate(property_actuator)
    if sensor.positive and change_sensor.positive:
        print("{cont_name}: ", "RESET")
        own["{cont_name}_time"] = 0.0
        own["{cont_name}_ind"] = 0
    if sensor.positive and own["{cont_name}_time"] > {duration}:
        property_actuator.value = "False"
        cont.activate(property_actuator)
"""

LINEAR_MOVEMENT = """
    print("actuator: {actuator_name}")
    actuator = cont.actuators["{actuator_name}"]
    target_position = {target_position}
    if sensor.positive and change_sensor.positive and {duration} != 0:
        print("Starting movement")
        actuator.linV = [(target_position[i] - own.position[i])/{duration}
            for i in range(3)]
    if change_sensor.positive and not sensor.positive:
        print("Stopping movement:", own.position)
        actuator.linV = [0, 0, 0]
        print("After setting:", actuator.linV)
        actuator.dLoc = [{target_position}[i] - own.position[i] for i in
            range(3)]
    cont.activate(actuator)
    print(own.position)
    print(actuator.linV)
    print(own.getVelocity())
    actuator.dLoc = [0, 0, 0]
"""


IMMEDIATE_ACTION_CONDITION = """
    if (sensor.positive):
"""
TRIGGERED_ACTION_CONDITION = """
    print("{trigger_sensor}:", cont.sensors["{trigger_sensor}"].positive)
    if (sensor.positive
            and cont.sensors["{trigger_sensor}"].positive):
"""
ACTION_ACTIVATION = """
        if own["{cont_name}_ind"] == {activation_index}:
            print("Activating action")
            actuator = scene.objects["{target_object}"].actuators[
                "{target_controller_name}"]
            actuator.value = "True"
            cont.activate(actuator)
            own["{cont_name}_ind"] += 1
"""


def generate_object_control_script(object_name):
    """Generates initial script for Blender Python controller for this object

    :return Name of script
    """
    script_name = ".".join((object_name, "py"))
    bpy.data.texts.new(script_name)
    bpy.data.texts[script_name].write(HEADER)
    return script_name


def generate_project_root():
    """Generate a root object used to activate initial actions"""
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


def generate_python_controller(
        object_name, duration=0, start_immediately=False):
    """Generate a new Python controller for object

    This produces a Python controller with a unique name [controller_name]
    attached to two sensors and one actuator. Furthermore, it adds a property
    to the given object with the same name as that controller. One of the
    sensors, also named [controller_name], is activated when this property is
    True. The other sensor, named [controller_name]_change, is activated when
    the value of this property changes. When either of these sensors is
    activated, the controller is itself activated, doing all of the heavy
    lifting for an ObjectAction. When the controller is activated, it activates
    an actuator, also named [controller_name], which sets the [controller_name]
    property to either True or False. This allows the controller to turn itself
    off after a certain duration.

    :param str object_name: Name of object to which controller will be added
    :param float duration: Duration of action started by this controller
    :param bool start_immediately: Whether or not this action should start as
    soon as the Cave starts
    :return Name of new controller
    """
    blender_object = bpy.data.objects[object_name]
    bpy.context.scene.objects.active = blender_object
    controller_count = 0
    while True:
        controller_name = "_".join(
            (object_name, "controller", "{}".format(controller_count)))
        if controller_name not in blender_object.game.controllers:
            break
        controller_count += 1
    bpy.ops.logic.controller_add(
        type='PYTHON',
        object=object_name,
        name=controller_name)
    controller = blender_object.game.controllers[controller_name]
    controller.mode = "MODULE"
    controller.module = "{}.activate_{}".format(
        object_name, controller_name)

    # Property used to control when controller is triggered
    property_name = controller_name
    bpy.ops.object.game_property_new(
        type='BOOL',
        name=property_name
    )
    blender_object.game.properties[property_name].value = False
    # Actuator to change said property
    actuator_name = controller_name
    bpy.ops.logic.actuator_add(
        type="PROPERTY",
        object=object_name,
        name=actuator_name
    )
    blender_object.game.actuators[-1].name = actuator_name
    blender_object.game.actuators[actuator_name].property = property_name
    blender_object.game.actuators[actuator_name].value = "True"
    controller.link(actuator=blender_object.game.actuators[actuator_name])
    # Sensor to detect when property gets set to True
    sensor_name = controller_name
    bpy.ops.logic.sensor_add(
        type="PROPERTY",
        object=object_name,
        name=sensor_name
    )
    blender_object.game.sensors[-1].name = sensor_name
        # WARNING: For some reason, setting the name via sensor_add results in
        # distorted sensor names sometimes. The above line is a workaround
        # which guarantees that the sensor is properly named. Blender source
        # bug?
    blender_object.game.sensors[sensor_name].property = property_name
    blender_object.game.sensors[sensor_name].value = "True"
    controller.link(sensor=blender_object.game.sensors[sensor_name])
    # Sensor to detect when property has changed
    change_sensor_name = "_".join((controller_name, "change"))
    bpy.ops.logic.sensor_add(
        type="PROPERTY",
        object=object_name,
        name=change_sensor_name
    )
    blender_object.game.sensors[-1].name = change_sensor_name
    blender_object.game.sensors[change_sensor_name].property =\
        property_name
    blender_object.game.sensors[change_sensor_name].evaluation_type =\
        "PROPCHANGED"
    controller.link(sensor=blender_object.game.sensors[change_sensor_name])

    #Sensor and property to detect time since activation
    timer_property_name = "_".join((controller_name, "time"))
    bpy.ops.object.game_property_new(
        type='TIMER',
        name=timer_property_name
    )
    add_time_sensor(
        object_name, controller_name, duration, timer_property_name)

    if start_immediately:
        link_to_root(object_name, controller_name)

    script_name = ".".join((object_name, "py"))
    bpy.data.texts[script_name].write(BASE_FUNCTION.format(
        cont_name=controller_name,
        duration=duration,
        start_immediately=start_immediately
        )
    )

    return controller_name


def add_time_sensor(object_name, controller_name, time, sensor_name):
    """Add a property sensor to trigger after a particular time

    :param str object_name: Name of object to add sensor to
    :param str controller_name: Name of controller to add sensor to
    :param float time: Time after which to trigger sensor
    :param str sensor_name: Name of sensor to be created"""
    blender_object = bpy.data.objects[object_name]
    bpy.context.scene.objects.active = blender_object
    controller = blender_object.game.controllers[controller_name]
    timer_property_name = "_".join((controller_name, "time"))
    bpy.ops.logic.sensor_add(
        type="PROPERTY",
        object=object_name,
        name=sensor_name
    )
    blender_object.game.sensors[-1].name = sensor_name
    blender_object.game.sensors[sensor_name].property =\
        timer_property_name
    blender_object.game.sensors[sensor_name].evaluation_type =\
        "PROPINTERVAL"
    blender_object.game.sensors[sensor_name].value_min = "{}".format(
        time)
    blender_object.game.sensors[sensor_name].value_max = "9999999"
    controller.link(sensor=blender_object.game.sensors[sensor_name])

    return sensor_name


def link_to_root(object_name, controller_name):
    """Set action to start immediately when project runs

    Links action to root object, which will set the property associated with
    that controller to True"""
    blender_object = bpy.data.objects[object_name]
    root_object = bpy.data.objects["ROOT"]
    controller = blender_object.game.controllers[controller_name]
    controller.link(
        sensor=root_object.game.sensors["ROOT"])


def add_motion_logic(
        object_name, controller_name, target_position, duration):
    blender_object = bpy.data.objects[object_name]
    blender_object.game.physics_type = 'DYNAMIC'
    controller = blender_object.game.controllers[controller_name]
    script_name = ".".join((object_name, "py"))
    actuator_name = "_".join((object_name, "motion_actuator"))
    if actuator_name not in blender_object.game.actuators:
        bpy.ops.logic.actuator_add(
            type="MOTION",
            object=object_name,
            name=actuator_name
        )
    controller.link(
        actuator=blender_object.game.actuators[actuator_name])
    bpy.data.texts[script_name].write(LINEAR_MOVEMENT.format(
        actuator_name=actuator_name,
        target_position=target_position,
        duration=duration
        )
    )


def add_action_activation_logic(
        object_name, controller_name, target_object_name,
        target_controller_name, trigger=None, activation_index=0):
    blender_object = bpy.data.objects[object_name]
    target_object = bpy.data.objects[target_object_name]
    controller = blender_object.game.controllers[controller_name]
    script_name = ".".join((object_name, "py"))
    controller.link(
        actuator=target_object.game.actuators[target_controller_name])
    if trigger is None:
        action_script = "".join(
            (IMMEDIATE_ACTION_CONDITION, ACTION_ACTIVATION))
    else:
        action_script = "".join(
            (TRIGGERED_ACTION_CONDITION, ACTION_ACTIVATION))
    bpy.data.texts[script_name].write(
        action_script.format(
            cont_name=controller_name,
            target_object=target_object_name,
            target_controller_name=target_controller_name,
            trigger_sensor=trigger,
            activation_index=activation_index
        )
    )
