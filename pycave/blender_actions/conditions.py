"""Tools for establishing conditions under which an action in Blender should
precede"""


class ActionCondition(object):
    """Generate Python logic specifying when action should, start, continue,
    and end

    :param int offset: A number of tabs (4 spaces) to add before condition
    strings"""

    @property
    def start_string(self):
        start_string = "    "*self.offset
        if len(self.start):
            start_string = "".join((start_string, "if {}:"))
            start_string.format(" and ".join(self.start))
            return start_string
        else:
            return "".join((start_string, "if True:"))

    @property
    def continue_string(self):
        continue_string = "    "*self.offset
        if len(self.cont):
            continue_string = "".join((continue_string, "if {}:"))
            continue_string.format(" and ".join(self.cont))
            return continue_string
        else:
            return "".join((continue_string, "if True:"))

    @property
    def end_string(self):
        end_string = "    "*self.offset
        if len(self.end):
            end_string = "".join((end_string, "if {}:"))
            end_string.format(" and ".join(self.end))
            return end_string
        else:
            return "".join((end_string, "if True:"))

    def add_time_condition(self, start_time=None, end_time=None):
        """Add condition based on time since activation"""
        cont = []
        if start_time is not None:
            self.start.append("time >= {}".format(start_time))
            cont.append("time >= {}".format(start_time))
        if end_time is not None:
            self.start.append("time >= {}".format(end_time))
            cont.append("time < {}".format(end_time))
        cont = " and ".join(cont)
        self.cont.append(cont)

    def add_index_condition(self, index_value):
        """Add condition based on how many sub-actions have been completed"""
        self.start.append("index == {}".format(index_value))
        self.cont.append("index >= {}".format(index_value))

    def add_click_condition(self, click_value):
        """Add condition based on how many times object is clicked"""
        self.start.append("own['clicks'] == {}".format(click_value))

    def __init__(self, offset=0):
        self.start = []
        self.cont = []
        self.end = []
        self.offset = offset
