"""Tools for starting, pausing, etc. timelines in Blender"""


class SceneReset(object):
    """Generate Python logic for resetting scene

    :param int offset: A number of tabs (4 spaces) to add before Python logic
    strings"""

    @property
    def start_string(self):
        script_text = [
            "scene.restart()"
            ]

        try:
            script_text[0] = "{}{}".format("    "*self.offset, script_text[0])
        except IndexError:
            return ""
        return "\n{}".format("    "*self.offset).join(script_text)

    @property
    def continue_string(self):
        return ""

    @property
    def end_string(self):
        return ""

    def __init__(self, offset=0):
        self.offset = offset
