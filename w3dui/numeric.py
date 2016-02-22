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
from .base import InputUI, InvalidInput
from .factories import ValidatedWidget


class NumericInput(InputUI, tk.Frame):
    """Widget for inputting numeric values"""

    def get_input_value(self):
        try:
            return float(self.entry_value.get())
        except TypeError:
            raise InvalidInput("Must be a numeric value")

    def set_input_value(self, value):
        if value is not None:
            self.entry_value.set("{:.5f}".format(value))

    def initUI(self, initial_value=None):
        self.entry_widgets.append(tk.Entry(
            self, textvariable=self.entry_value))
        super(NumericInput, self).initUI(initial_value=initial_value)

    def __init__(self, parent, validator, initial_value=None):
        self.entry_value = tk.stringVar()
        super(NumericInput, self).__init__(
            parent, validator, initial_value=initial_value,
            error_message="Invalid input")


ValidatedNumericInput = ValidatedWidget(NumericInput)
"""Widget for inputting a number with W3D-style validation"""


class IntInput(InputUI, tk.Frame):
    """Widget for inputting integer values"""

    def get_input_value(self):
        try:
            new_value = int(self.entry_value.get())
        except TypeError:
            raise InvalidInput("Must be an integer value")
        self.set_input_value(new_value)
        return new_value

    def set_input_value(self, value):
        if value is not None:
            self.entry_value.set(str(value))

    def __init__(self, parent, validator, initial_value=None):
        self.entry_value = tk.stringVar()
        super(NumericInput, self).__init__(
            parent, validator, initial_value=initial_value,
            error_message="Invalid input")


ValidatedIntInput = ValidatedWidget(
    IntInput, replacements={NumericInput: ValidatedNumericInput})
"""Widget for inputting a number with W3D-style validation"""
