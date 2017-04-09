# Copyright (C) 2016 William Hicks
#
# This file is part of Writing3D.
#
# Writing3D is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

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
            start_string = start_string.format(" and ".join(self.start))
            return start_string
        else:
            return "".join((start_string, "if True:"))

    @property
    def continue_string(self):
        continue_string = "    "*self.offset
        if len(self.cont):
            continue_string = "".join((continue_string, "if {}:"))
            continue_string = continue_string.format(" and ".join(self.cont))
            return continue_string
        else:
            return "".join((continue_string, "if True:"))

    @property
    def end_string(self):
        end_string = "    "*self.offset
        if len(self.end):
            end_string = "".join((end_string, "if {}:"))
            end_string = end_string.format(" and ".join(self.end))
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
            cont.append("time < {}".format(end_time))
            self.end.append("time >= {}".format(end_time))
        cont = " and ".join(cont)
        self.cont.append(cont)

    def add_index_condition(self, index_value):
        """Add condition based on how many sub-actions have been completed"""
        self.start.append("index == {}".format(index_value))
        self.cont.append("index >= {}".format(index_value))

    def add_click_condition(self, click_value):
        """Add condition based on how many times object is clicked"""
        self.start.append("own['clicks'] == {}".format(click_value))
        self.cont.append("own['clicks'] == {}".format(click_value))
        self.end.append("own['clicks'] == {}".format(click_value))

    def __init__(self, offset=0):
        self.start = []
        self.cont = []
        self.end = []
        self.offset = offset
