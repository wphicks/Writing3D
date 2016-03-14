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

"""Tk widgets for inputting text-based W3D options"""

import tkinter as tk
from .base import W3DValidatorInput, ProjectInput


class OptionInput(W3DValidatorInput, tk.Frame):
    """Widget for choosing from a pre-determined set of options"""

    def get_input_value(self):
        return self.validator.coerce(self.entry_value.get())

    def set_input_value(self, value):
        if value is not None:
            self.entry_value.set(str(value))

    def _pack_entry_widgets(self):
        super(OptionInput, self)._pack_entry_widgets(
            pack_arguments={"anchor": tk.W}
        )

    def initUI(self, initial_value=None):
        self.entry_value = tk.StringVar()
        self.entry_widgets.append(tk.OptionMenu(
            self.target_frame, self.entry_value,
            *self.validator.valid_menu_items)
        )
        super(OptionInput, self).initUI(initial_value=initial_value)


class ProjectOptionInput(OptionInput, ProjectInput):
    """Widget for validating a project element that takes one of a set number
    of values"""


class ReferenceInput(ProjectOptionInput):
    """Widget for choosing from a set of options defined by another project
    element"""

    def _reset_menu(self):
        menu = self.entry_widgets[-1]["menu"]
        menu.delete(0, "end")
        for option in self.validator.valid_menu_items:
            menu.add_command(
                label=option,
                command=lambda value=option: self.entry_value.set(value)
            )

    def initUI(self, initial_value=None):
        self.validator.set_project(self.project_path.get_project())
        super(ReferenceInput, self).initUI(initial_value=initial_value)
        self.entry_widgets[-1].bind("<FocusIn>", self._reset_menu)
