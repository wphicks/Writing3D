"""Tools for scaling Blender objects"""


class ScaleAction(object):
    """Generate Python logic for how color should change when action first
    starts, as it continues, and when it ends

    :param float scale: The scale to transition to
    :param float duration: Time for action to complete in seconds
    :param int offset: A number of tabs (4 spaces) to add before Python logic
    strings"""

    @property
    def start_string(self):
        script_text = []
        script_text.extend([
            "new_scale = {}".format(self.scale),
            "blender_object['scaleV'] = ["
            "    (new_scale - blender_object.scaling[i])/{}.".format(
                (self.duration*60, 1)[self.duration == 0]),
            "    for i in range(len(blender_object.scaling))]"]
        )

        try:
            script_text[0] = "{}{}".format("    "*self.offset, script_text[0])
        except IndexError:
            return ""
        return "\n{}".format("    "*self.offset).join(script_text)

    @property
    def continue_string(self):
        script_text = [
            "blender_object.scaling = [",
            "    (blender_object.scaling[i] + blender_object['scaleV'][i]]"
        ]
        try:
            script_text[0] = "{}{}".format("    "*self.offset, script_text[0])
        except IndexError:
            return ""
        return "\n{}".format("    "*self.offset).join(script_text)

    @property
    def end_string(self):
        script_text = [
            "blender_object.scaling = {}".format([self.scale]*3)]
        try:
            script_text[0] = "{}{}".format("    "*self.offset, script_text[0])
        except IndexError:
            return ""
        return "\n{}".format("    "*self.offset).join(script_text)

    def __init__(self, scale, duration, offset=0):
        self.scale = scale
        self.duration = duration
        self.offset = offset
