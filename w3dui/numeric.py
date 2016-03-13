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

"""Tk widgets for inputting numeric W3D options"""

import tkinter as tk
from .base import InputUI, InvalidInput, W3DValidatorInput, ProjectInput


class NumericInput(InputUI, tk.Frame):
    """Widget for inputting numeric values"""

    def get_input_value(self, value=None):
        try:
            if value is None:
                value = float(self.entry_value.get())
            return super().get_input_value(value=value)
        except TypeError:
            raise InvalidInput("Must be a numeric value")

    def set_input_value(self, value):
        if value is not None:
            self.entry_value.set("{:.5f}".format(value))

    def initUI(self, initial_value=None):
        self.entry_value = tk.StringVar()
        self.entry_widgets.append(tk.Entry(
            self.target_frame, textvariable=self.entry_value))
        super(NumericInput, self).initUI(initial_value=initial_value)


class ValidatedNumericInput(NumericInput, W3DValidatorInput):
    """Widget for inputting a number with W3D-style validation"""


class ProjectNumericInput(NumericInput, ProjectInput):
    """Widget for inputting a float as an element in a W3DProject"""


class IntInput(NumericInput, tk.Frame):
    """Widget for inputting integer values"""

    def get_input_value(self, value=None):
        try:
            if value is None:
                value = int(self.entry_value.get())
        except TypeError:
            raise InvalidInput("Must be an integer value")
        value = super().get_input_value(value=value)
        self.set_input_value(value)
        return value

    def set_input_value(self, value):
        if value is not None:
            self.entry_value.set(str(value))


class ValidatedIntInput(IntInput, W3DValidatorInput):
    """Widget for inputting an int with W3D-style validation"""


class ProjectIntInput(IntInput, ProjectInput):
    """Widget for inputting an int as an element in a W3DProject"""
