"""Tools for changing the color of a Blender object"""


class ColorAction(object):
    """Generate Python logic for how color should change when action first
    starts, as it continues, and when it ends

    :param list color: The color to transition to (specified as a 3-element
    list of integers between 0 and 255
    :param float duration: Time for action to complete in seconds
    :param int offset: A number of tabs (4 spaces) to add before Python logic
    strings"""

    @property
    def start_string(self):
        script_text = []
        script_text.extend([
            "new_color = {}".format(self.color),
            "blender_object['colorV'] = [",
            "    (new_color[i] - blender_object.color[i])/{}".format(
                (self.duration*60, 1)[self.duration == 0]),
            "    for i in range(len(new_color))]"]
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
            "for i in range(len(blender_object['colorV'])):",
            "    new_color[i] += blender_object['colorV'][i]",
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
            "new_color = {}".format(self.color),
            "if len(new_color) < 4:",
            "    new_color.append(blender_object.color[3])",
            "blender_object.color = new_color"]
        try:
            script_text[0] = "{}{}".format("    "*self.offset, script_text[0])
        except IndexError:
            return ""
        return "\n{}".format("    "*self.offset).join(script_text)

    def __init__(self, color, duration, offset=0):
        self.color = [channel/255. for channel in color]
        self.duration = duration
        self.offset = offset
