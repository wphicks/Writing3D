"""A Blender-based implementation of triggers based on the state of the user in
virtual space
"""
from .triggers import BlenderTrigger


class BlenderPositionTrigger(BlenderTrigger):
    """Activator based on position of user in virtual space"""

    def generate_detection_logic(self):
        """Add a function to Python control script to detect user position"""
        detection_logic = [
            "\ndef detect_event(cont):",
            "    scene = bge.logic.getCurrentScene()",
            "    own = cont.owner",
            "    position = own.position",
            "    inside = True",
            "    corners = {}".format(
                zip(self.box["corner1"], self.box["corner2"])),
            "    trigger = scene.objects['{}']".format(
                self.name),
            "    for i in range({}):".format((3, 2)[self.box["ignore_y"]]),
            "        if (",
            "                position[i] < min(corners[i]) or",
            "                position[i] > max(corners[i])):",
            "            inside = False",
            "            break",
            "    if ({} and trigger['enabled'] and".format(
                ("not inside", "inside")[
                    self.box["direction"] == "Inside"]),
            "            trigger['status'] == 'Stop'):"
            "        trigger['status'] = 'Start'"
        ]
        detection_logic = "\n".join(detection_logic)
        return detection_logic

    def __init__(
            self, name, actions, box, duration=0, enable_immediately=True,
            remain_enabled=True):
        super(BlenderPositionTrigger, self).__init__(
            name, actions, enable_imediately=enable_immediately,
            remain_enabled=remain_enabled)
        self.box = box
