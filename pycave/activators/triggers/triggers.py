"""A Blender-based implementation of event triggers"""
from pycave.names import generate_trigger_name
from pycave.activators import Activator


class BlenderTrigger(Activator):
    """Activator based on detection of events in virtual space"""

    @property
    def name(self):
        return generate_trigger_name(self.name_string)

    def generate_action_logic(self):
        action_logic = [super(BlenderTrigger, self).generate_action_logic()]
        max_time = self.duration
        #TODO: The above is incorrect. Duration is actually a measure of how
        #long a trigger must remain triggered before its actions begin
        action_index = 0
        for action in self.actions:
            action_logic.extend(
                ["".join(("        ", line)) for line in
                    action.generate_blender_logic(
                        time_condition=0,
                        index_condition=action_index
                    )]
            )
            action_index += 1
            max_time = max(max_time, action.end_time)
        self.script_footer = self.script_footer.format(max_time=max_time)
        self.script_footer = "\n".join(
            [
                self.script_footer,
                "            own['enabled'] = {}".format(self.remain_enabled)
            ]
        )
        return "\n".join(action_logic)

    def generate_detection_logic(self):
        """Create logic for detecting triggering event

        Dummy method intended to be overridden by subclasses"""
        return ""

    def write_python_logic(self):
        """Write any necessary Python controller scripts for this activator"""
        script_text = [
            self.script_header,
            self.generate_action_logic(),
            self.script_footer,
            self.generate_detection_logic()
        ]
        self.script.write("\n".join(script_text))
        return self.script

    def __init__(
            self, name, actions, duration=0, enable_immediately=True,
            remain_enabled=True):
        super(BlenderTrigger, self).__init__(name, actions)
        self.duration = duration
        self.enable_immediately = enable_immediately
        self.remain_enabled = remain_enabled
