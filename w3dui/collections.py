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

"""Tk widgets for inputting structured collections of W3D features"""

import tkinter as tk
from .base import ProjectInput
from .struct_widgets import ScrollableFrame
from .widget_factories import widget_creator


class ListInput(ProjectInput, ScrollableFrame):
    """Widget for entering lists of project elements"""

    def get_input_value(self):
        return [widget.get_input_value() for widget in self.entry_elements]

    def _remove_index(self, index):
        """Remove element at given index from project"""
        self.project_path.remove_index(index)
        self.entry_widgets[index + 2].destroy()
        del self.entry_widgets[index + 2]
        del self.entry_elements[index]

    def _add_element(self, initial_value=None):
        self.entry_widgets.append(tk.Frame(self.entry_widgets[0]))
        creator_kwargs = {
            "validator": self.validator.base_validator, "input_parent": self,
            "frame": self.entry_widgets[-1],
            "option_name": len(self.get_input_value())
        }
        if initial_value is not None:
            creator_kwargs["initial_value"] = initial_value
        new_entry = widget_creator(**creator_kwargs)
        entry_destroy = tk.Button(
            self.entry_widgets[-1], text="Delete",
            command=lambda: self._remove_index(
                new_entry.project_path.get_specifier()
            )
        )
        new_entry.pack(side=tk.LEFT, expand=1)
        self.entry_elements.append(new_entry)
        entry_destroy.pack(side=tk.RIGHT, expand=1, fill=tk.Y)

    def _pack_entry_widgets(self):
        super(ListInput, self)._pack_entry_widgets(
            pack_arguments={"fill": tk.X, "expand": 1}
        )

    def initUI(self, initial_value=None):
        self.entry_widgets.append(tk.Frame(self.target_frame))
        self.entry_widgets.append(tk.Button(
            self.target_frame, text="Add", command=self._add_element)
        )
        super(ListInput, self).initUI(initial_value=initial_value)

    def __init__(
            self, parent, validator, project_path, initial_value=None,
            error_message=None):
        self.project_path = project_path
        super(ListInput, self).__init__(
            parent, validator, initial_value=initial_value,
            error_message=error_message)
        self.target_frame = self.inside_frame
        self.entry_elements = []


class FixedListInput(ProjectInput, tk.Frame):
    """Widget for inputting a list of fixed size as a project option"""

    def get_input_value(self):
        return [widget.get_input_value() for widget in self.entry_widgets]

    def set_input_value(self, iterable):
        for widget, value in zip(self.entry_widgets, iterable):
            widget.set_input_value(value)

    def _pack_entry_widgets(self):
        super(ListInput, self)._pack_entry_widgets(
            pack_arguments={"anchor": tk.W, "side": tk.LEFT}
        )

    def initUI(self, initial_value=None):
        for i in range(self.validator.required_length):
            creator_kwargs = {
                "validator": self.validator.base_validator,
                "input_parent": self,
                "frame": self,
                "option_name": i
            }
            if initial_value is not None:
                creator_kwargs["initial_value"] = initial_value[i]
            self.entry_widgets.append(widget_creator(
                **creator_kwargs))
        super(FixedListInput, self).initUI(initial_value=initial_value)
