"""Tools for dynamically changing clickable links in Blender"""
from pycave.names import generate_link_name, generate_blender_object_name
from pycave.errors import EBKAC


class LinkAction(object):
    """Generate Python logic for how link should change when action first
    starts, as it continues, and when it ends

    :param str change: The change to be performed (one of "Enable", "Disable",
    "Activate", or "Activate if enabled")
    :param int offset: A number of tabs (4 spaces) to add before Python logic
    strings"""

    @property
    def start_string(self):
        script_text = [
            "trigger = scene.objects['{}']".format(self.link_name)
            ]
        if self.change == "Enable":
            script_text.append(
                "trigger['enabled'] = True"
            )
        elif self.change == "Disable":
            script_text.append(
                "trigger['enabled'] = False"
            )
        elif self.change == "Activate":
            script_text.append(
                "trigger['status'] = 'Start'"
            )
        elif self.change == "Activate if enabled":
            script_text.extend([
                "if trigger['enabled']:",
                "    trigger['status'] = 'Start'"]
            )
        else:
            raise EBKAC(
                "Link action must be one of 'Enable', 'Disable', 'Activate', "
                "'Activate if enabled'")

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

    def __init__(self, object_name, change, offset=0):
        self.link_name = generate_link_name(
            generate_blender_object_name(object_name))
        self.change = change
        self.offset = offset
