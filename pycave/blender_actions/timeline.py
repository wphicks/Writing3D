"""Tools for starting, pausing, etc. timelines in Blender"""
from pycave.names import generate_blender_timeline_name
from pycave.errors import EBKAC


class TimelineStarter(object):
    """Generate Python logic for how link should change when action first
    starts, as it continues, and when it ends

    :param str change: The change to be performed (one of "Start", "Stop",
    "Continue", or "Start if not started")
    :param int offset: A number of tabs (4 spaces) to add before Python logic
    strings"""

    @property
    def start_string(self):
        script_text = [
            "trigger = scene.objects['{}']".format(self.timeline)
            ]
        if self.change == "Start":
            script_text.append(
                "trigger['status'] = 'Start'"
            )
        elif self.change == "Stop":
            script_text.append(
                "trigger['status'] = 'Stop'"
            )
        elif self.change == "Continue":
            script_text.append(
                "trigger['status'] = 'Continue'"
            )
        elif self.change == "Start if not started":
            script_text.extend([
                "if trigger['status'] == 'Stop':",
                "    trigger['status'] = 'Start'"]
            )
        else:
            raise EBKAC(
                "Timeline action must be one of 'Start', 'Stop', 'Continue', "
                "'Start if not started'")

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

    def __init__(self, timeline, change, offset=0):
        self.timeline = generate_blender_timeline_name(timeline)
        self.change = change
        self.offset = offset
