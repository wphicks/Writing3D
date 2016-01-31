"""Tools for enabling/disabling triggers in Blender"""
from pycave.names import generate_trigger_name


class TriggerEnabler(object):
    """Generate Python logic for how link should change when action first
    starts, as it continues, and when it ends

    :param str change: The change to be performed (one of "Start", "Stop",
    "Continue", or "Start if not started")
    :param int offset: A number of tabs (4 spaces) to add before Python logic
    strings"""

    @property
    def start_string(self):
        script_text = [
            "trigger = scene.objects['{}']".format(self.trigger)
            ]
        script_text.append(
            "trigger['enabled'] = {}".format(self.enable)
        )

        try:
            script_text[0] = "{}{}".format("    "*self.offset, script_text[0])
        except IndexError:
            return ""
        return "\n{}".format("    "*self.offset).join(script_text)

    @property
    def continue_string(self):
        return "{}pass".format("    "*self.offset)

    @property
    def end_string(self):
        return "{}pass".format("    "*self.offset)

    def __init__(self, trigger, enable, offset=0):
        self.trigger = generate_trigger_name(trigger)
        self.enable = enable
        self.offset = offset
