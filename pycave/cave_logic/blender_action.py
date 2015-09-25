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


class ActivateOtherAction(BlenderAction):
    """Used to activate another BlenderAction

    :param BlenderAction action: The other action to activate"""

    def __init__(self, trigger, action):
        super(ActivateOtherAction, self).__init__(trigger)
        self.action = action
        self.trigger.controller.link(actuator=action.trigger.actuator)
        self.on_body.append("""
        current_actuator = scene.objects["{object_name}"].actuators[
            "{actuator_name}"]
        current_actuator.value = "True"
        cont.activate(current_actuator)
        """.format(
            object_name=self.trigger.blender_object_name,
            actuator_name=action.trigger.actuator.name)
        )


class LinearMovement(BlenderAction):
    """Used to execute a linear movement of a Blender object

    :param CavePlacement target_placement: Target destination and orientation
    of object"""

    def create_movement_actuator(self):
        """Create a motion actuator for object if it does not exist"""
        if "MOVE" in self.trigger.blender_object.game.actuators:
            return self.trigger.blender_object.game.actuators["MOVE"]
        self.trigger.make_object_active()
        bpy.ops.logic.actuator_add(
            type="MOTION",
            object=self.trigger.blender_object_name,
            name="MOVE"
        )
        motion_actuator = self.trigger.blender_object.game.actuators["MOVE"]
        self.trigger.controller.link(actuator=motion_actuator)
        return motion_actuator

    def __init__(self, trigger, target_placement):
        super(LinearMovement, self).__init__(trigger)
        motion_actuator = self.create_movement_actuator()
        try:
            duration = trigger.duration
        except AttributeError:
            duration = 0
        if duration != 0:
            self.on_body.append("""
        target_position = {target_position}
        motion_actuator = cont.actuators["{motion_actuator}"]
        actuator.linV = [(target_position[i] - own.position[i])/{duration}
            for i in range(3)]
        cont.activate(motion_actuator)""".format(
                duration=duration,
                target_position=tuple(target_placement["position"]),
                motion_actuator=motion_actuator.name
                )
            )
        self.off_body.append("""
        motion_actuator = cont.actuators["{motion_actuator}"]
        motion_actuator.linV = [0, 0, 0]
        target_position = {target_position}
        motion_actuator.dLoc = [(target_position[i] - own.position[i])
            for i in range(3)]
        cont.activate(motion_actuator)
        motion_actuator.dLoc = [0, 0, 0]""".format(
            target_position=tuple(target_placement["position"]),
            motion_actuator=motion_actuator.name
            )
        )
