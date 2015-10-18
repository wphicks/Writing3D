"""Tools for implementing changes to Blender objects"""
import warnings
try:
    import bpy
except ImportError:
    warnings.warn(
        "Module bpy not found. Loading pycave.objects as standalone")


class BlenderAction(object):
    """A single unit of action within Blender

    Note that this may correspond to part of a CaveAction or several
    CaveActions
    :param BlenderTrigger trigger: The trigger used to activate this action"""

    def create_on_script(self):
        """Create section of Blender Python controller script to activate this
        action"""
        script = "\n".join(self.on_body)
        return script

    def create_off_script(self):
        """Create section of Blender Python controller script to deactivate
        this action"""
        script = "\n".join(self.off_body)
        return script

    def __init__(self, trigger):
        self.trigger = trigger
        self.on_body = ["""
        own["{index_property}"] += 1
        """]
        self.off_body = ["""
        pass
        """]


class ActivateTrigger(BlenderAction):
    """Used to activate or pause a BlenderTrigger

    :param BlenderAction other_trigger: The trigger to activate"""

    def __init__(self, trigger, other_trigger, action="Start"):
        super(ActivateTrigger, self).__init__(trigger)
        self.other_trigger = other_trigger
        self.trigger.controller.link(actuator=other_trigger.actuator)
        self.on_body.append("""
        other_object = scene.objects["{other_object_name}"]
        current_actuator = other_object.actuators[
            "{actuator_name}"]
        """.format(
            other_object_name=self.other_trigger.blender_object_name,
            actuator_name=other_trigger.actuator.name)
        )
        if action == "Start":
            self.on_body.append("""
        current_actuator.value = "True"
        other_object["{pause_index_property}"] = 0
        other_object["{pause_time_property}"] = 0
        cont.activate(current_actuator)
        """.format(
                pause_index_property=self.other_trigger.pause_index_name,
                pause_time_property=self.other_trigger.pause_time_name)
            )
        elif action == "Stop":
            self.on_body.append("""
        current_actuator.value = "False"
        other_object["{pause_index_property}"] = other_object[
            "{index_property}"]
        """.format(
                pause_index_property=self.other_trigger.pause_index_name)
            )
            try:
                self.on_body.append("""
        other_object["{pause_time_property}"] = other_object[
            "{time_property}"]
        """.format(
                    pause_time_property=self.other_trigger.pause_time_name,
                    time_property=self.other_trigger.timer_name
                    )
                )
            except AttributeError:
                pass
            self.on_body.append("""
        cont.activate(current_actuator)
            """)
        elif action == "Continue":
            self.on_body.append("""
        current_actuator.value = "True"
        cont.activate(current_actuator)
        """)
        elif action == "Start if not started":
            self.on_body.append("""
        if other_object["{trigger_name}"]:
            current_actuator.value = "True"
            other_object["{pause_index_property}"] = 0
        """.format(
                trigger_name=self.other_trigger.name,
                pause_index_property=self.other_trigger.pause_index_name)
            )
            try:
                self.on_body.append("""
            other_object["{pause_time_property}"] = 0
        """.format(pause_time_property=self.other_trigger.pause_time_name))
            except AttributeError:
                pass
            self.on_body.append("""
            cont.activate(current_actuator)
            """)


class LinearMovement(BlenderAction):
    """Used to execute a linear movement of a Blender object

    :param CavePlacement target_placement: Target destination and orientation
    of object"""

    def create_movement_actuator(self):
        """Create a motion actuator for object if it does not exist"""
        try:
            motion_actuator = self.trigger.blender_object.game.actuators[
                "MOVE"]
        except KeyError:
            self.trigger.make_object_active()
            bpy.ops.logic.actuator_add(
                type="MOTION",
                object=self.trigger.blender_object_name,
                name="MOVE"
            )
            motion_actuator = self.trigger.blender_object.game.actuators[
                "MOVE"]
            motion_actuator.mode = "OBJECT_NORMAL"
        self.trigger.controller.link(actuator=motion_actuator)
        return motion_actuator

    def create_rotation_logic(self):
        """Add rotation logic to trigger script"""
        if self.target_placement["rotation"]["rotation_mode"] == "Axis":
            target_rotation = self.target_placement[
                "rotation"].get_rotation_matrix(
                self.trigger.blender_object).to_quaternion()
            if self.relative:
                pass
            else:
                self.on_body.append("""
        rotation = own.orientation.to_quaternion()
        target_rotation = Quaternion()
        target_rotation.w={w}
        target_rotation.x={x}
        target_rotation.y={y}
        target_rotation.z={z}
        rotation_delta = target_rotation.rotation_difference(rotation)
        angular_velocity = rotation_delta.angle*rotation_delta.axis/{duration}
        motion_actuator = cont.actuators["{motion_actuator}"]
        motion_actuator.angV = angular_velocity
        cont.activate(motion_actuator)
        """.format(
                    w=target_rotation.w,
                    x=target_rotation.x,
                    y=target_rotation.y,
                    z=target_rotation.z,
                    duration=self.duration,
                    motion_actuator=self.motion_actuator.name
                    )
                )
        self.off_body.append("""
        motion_actuator = cont.actuators["{motion_actuator}"]
        motion_actuator.angV = [0, 0, 0]
        own.angularVelocity = [0, 0, 0]
        cont.activate(motion_actuator)
        """.format(
            motion_actuator=self.motion_actuator.name
            )
        )

    def create_position_logic(self):
        """Add positional movement logic to trigger script"""
        if self.duration != 0:
            if self.relative:
                self.on_body.append("""
        target_position = [own.position[i] + {target_position}[i] for i in
            range(3)]""".format(
                    target_position=tuple(self.target_placement["position"]))
                )
            else:
                self.on_body.append("""
        target_position = {target_position}""".format(
                    target_position=tuple(self.target_placement["position"]))
                )
            self.on_body.append("""
        motion_actuator = cont.actuators["{motion_actuator}"]
        motion_actuator.linV = [
            (target_position[i] - own.position[i])/{duration} for i in
            range(3)]
        cont.activate(motion_actuator)""".format(
                duration=self.duration,
                target_position=tuple(self.target_placement["position"]),
                motion_actuator=self.motion_actuator.name
                )
            )
        self.off_body.append("""
        motion_actuator = cont.actuators["{motion_actuator}"]
        motion_actuator.linV = [0, 0, 0]
        target_position = {target_position}
        motion_actuator.dLoc = [(target_position[i] - own.position[i])
            for i in range(3)]
        cont.activate(motion_actuator)
        motion_actuator.dLoc = [0, 0, 0]
        own.setLinearVelocity([0,0,0]) # Nasty workaround for Blender 2.69
        cont.activate(motion_actuator)""".format(
            target_position=tuple(self.target_placement["position"]),
            motion_actuator=self.motion_actuator.name
            )
        )

    def __init__(self, trigger, target_placement, relative=False):
        super(LinearMovement, self).__init__(trigger)
        self.relative = relative
        self.motion_actuator = self.create_movement_actuator()
        self.trigger = trigger
        self.target_placement = target_placement
        try:
            self.duration = trigger.duration
        except AttributeError:
            self.duration = 0
        self.create_position_logic()
        self.create_rotation_logic()


class VisibilityChange(BlenderAction):
    """Used to change the visibility of a Blender object

    :param bool visibility: Whether object should be visible after action has
    been executed"""

    def create_visibility_actuator(self):
        try:
            visibility_actuator = self.trigger.blender_object.game.actuators[
                "VISIBILITY"]
        except KeyError:
            self.trigger.make_object_active()
            bpy.ops.logic.actuator_add(
                type="VISIBILITY",
                object=self.trigger.blender_object_name,
                name="VISIBILITY"
            )
            visibility_actuator = self.trigger.blender_object.game.actuators[
                "VISIBILITY"]
        self.trigger.controller.link(actuator=visibility_actuator)
        return visibility_actuator

    def create_visibility_logic(self):
        self.on_body.append("""
        visibility_actuator = cont.actuators["{visibility_actuator}"]
        visibility_actuator.visibility = {visibility}
        cont.activate(visibility_actuator)""".format(
            visibility_actuator=self.visibility_actuator.name,
            visibility=self.visibility
            )
        )

    def __init__(self, trigger, visibility):
        super(VisibilityChange, self).__init__(trigger)
        self.visibility = visibility
        self.visibility_actuator = self.create_visibility_actuator()
        self.create_visibility_logic()
