"""Tools for changing the visibility of a Blender object"""


class VisibilityAction(object):
    """Generate Python logic for how visibility should change when action first
    starts, as it continues, and when it ends

    :param bool visibility: The visibility to transition to
    :param float duration: Time for action to complete in seconds
    :param int offset: A number of tabs (4 spaces) to add before Python logic
    strings"""

    @property
    def start_string(self):
        script_text = []
        script_text.extend([
            "blender_object.color[3] = int(blender_object.visible)",
            "blender_object.setVisible(True)",
            "delta_alpha = {} - blender_object.color[3]".format(
                int(self.visibility)),
            "blender_object['visV'] = delta_alpha/{}".format(
                (self.duration*60., 1)[self.duration == 0])]
        )

        try:
            script_text[0] = "{}{}".format("    "*self.offset, script_text[0])
        except IndexError:
            return ""
        return "\n{}".format("    "*self.offset).join(script_text)

    @property
    def continue_string(self):
        script_text = [
            "new_color = blender_object.color",
            "new_color[3] += blender_object['visV']",
            "blender_object.color = new_color"
        ]
        try:
            script_text[0] = "{}{}".format("    "*self.offset, script_text[0])
        except IndexError:
            return ""
        return "\n{}".format("    "*self.offset).join(script_text)

    @property
    def end_string(self):
        script_text = [
            "new_color = blender_object.color",
            "new_color[3] = {}".format(int(self.visible)),
            "blender_object.color = new_color",
            "blender_object.setVisible({})".format(self.visible)]
        try:
            script_text[0] = "{}{}".format("    "*self.offset, script_text[0])
        except IndexError:
            return ""
        return "\n{}".format("    "*self.offset).join(script_text)

    def __init__(self, visibility, duration, offset=0):
        self.visibility = visibility
        self.duration = duration
        self.offset = offset
