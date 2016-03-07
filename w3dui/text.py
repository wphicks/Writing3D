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
import os
from .base import InputUI, help_bubble, W3DValidatorInput, ProjectInput


class TextBlock(InputUI, tk.Frame):
    """Widget for inputting a formatted block of text"""

    def get_input_value(self):
        return self.entries[0].get("1.0", tk.END)

    def set_input_value(self, value):
        if value is not None:
            self.editor.insert(tk.END, str(value))

    def _pack_entry_widgets(self):
        super(TextBlock, self)._pack_entry_widgets(
            pack_arguments={"fill": tk.BOTH, "expand": 1}
        )

    def initUI(self, initial_value=None):
        self.entry_widgets.append(tk.Text(self.target_frame))
        super(TextBlock, self).initUI(initial_value=initial_value)


class ValidatedTextBlock(TextBlock, W3DValidatorInput):
    """Widget for inputting a text block with W3D-style validation"""


class ProjectTextBlock(TextBlock, ProjectInput):
    """Widget for inputting a text block as an element in a W3DProject"""


class StringInput(InputUI, tk.Frame):

    def get_input_value(self):
        return self.entry_value.get()

    def set_input_value(self, value):
        if value is not None:
            self.entry_value.set(value)

    def _pack_entry_widgets(self):
        super(StringInput, self)._pack_entry_widgets(
            pack_arguments={"fill": tk.X, "expand": 1}
        )

    def initUI(self, initial_value=None):
        self.entry_value = tk.StringVar()
        self.entry_widgets.append(tk.Entry(
            self.target_frame, textvariable=self.entry_value))
        super(StringInput, self).initUI(initial_value=initial_value)


class ValidatedStringInput(StringInput, W3DValidatorInput):
    """Widget for inputting a string with W3D-style validation"""


class ProjectStringInput(StringInput, ProjectInput):
    """Widget for inputting a string as an element in a W3DProject"""


class FileInput(StringInput, tk.Frame):
    """Widget for inputting a filename"""

    def validate_input(self):
        return (
            super(FileInput, self).validate_input() and
            os.path.exists(self.get_input_value)
        )  # Should we do isfile instead here?

    def open_file_dialog(self):
        """Open GUI dialog for obtaining filename"""
        filename = tk.filedialog.askopenfilename()
        old_value = self.get_input_value()
        self.set_input_value(self, filename)
        if not self.validate_input():
            help_bubble(self.error_message)
            self.set_input_value(self, old_value)

    def initUI(self, initial_value=None):
        super(FileInput, self).initUI(initial_value=initial_value)
        self.entry_widgets[-1].bind('<Button-1>', self.open_file_dialog)

    def __init__(self, parent, validator, initial_value=None):
        super(FileInput, self).__init__(
            parent, validator, initial_value=initial_value,
            error_message="Invalid filename")


class ValidatedFileInput(FileInput, W3DValidatorInput):
    """Widget for inputting a filename with W3D-style validation"""


class ProjectFileInput(FileInput, W3DValidatorInput):
    """Widget for inputting a filename as an element in a W3DProject"""
