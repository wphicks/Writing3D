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

"""Tk widgets for inputting W3DProject options"""

import tkinter as tk


def help_bubble(message):
    top = tk.Toplevel()
    top.title("Error")
    error_message = tk.Message(
        top, text=message, width=200)
    error_message.pack()
    dismiss = tk.Button(top, text="Dismiss", command=top.destroy)
    dismiss.pack()


class InputUI(object):
    """Base class for building Tkinter input widgets

    Classes that inherit from InputUI should also inherit from a TK widget like
    tk.Frame or ttk.LabelFrame
    :param parent: The parent widget for this widget
    """

    def destroy(self):
        if self.validate_input():
            self.store_value()
        super(InputUI, self).destroy()

    def get_stored_value(self):
        """Gets the current value of this option in the associated
        W3DProject"""
        pass

    def store_value(self):
        """Stores the current input value in a W3DProject"""
        pass

    def validate_input(self):
        """Return true if input is valid for this option"""
        return True

    def get_input_value(self):
        """Returns the current input value for this widget"""
        return None

    def set_input_value(self, value):
        """Sets the displayed input value to given value"""
        pass

    def _process_input(self):
        """Store input if valid; otherwise display error message"""
        if self.validate_input():
            self.store_value()
        else:
            help_bubble(self.error_message)

    def _pack_entry_widgets(self, pack_arguments={}):
        """Pack all entry widgets in self

        :param dict pack_arguments: A dictionary of keyword arguments used to
        pack the entry_widgets"""
        for entry in self.entry_widgets:
            self.entry_widgets.pack(**pack_arguments)

    def initUI(self, initial_value=None):
        """Set up all necessary children

        This can safely be called multiple times to reset the UI, e.g. when a
        new project is loaded"""
        self.set_input_value(initial_value)
        self._pack_entry_widgets()
        for entry in self.entry_widgets:
            entry.bind("<FocusOut>", self._process_input)

    def __init__(
            self, parent, initial_value=None, error_message="Invalid input"):
        super(InputUI, self).__init__(parent)  # Base TK widget __init__
        self.entry_widgets = []
        self.error_message = error_message
        self.initUI(initial_value=initial_value)


class W3DValidatorInput(InputUI):
    """TK widget for getting input and validating with a W3D-style validator

    :param Validator validator: A W3D-style validator"""

    def validate_input(self):
        return self.validator(self.get_input_value())

    def __init__(
            self, parent, validator, initial_value=None,
            error_message="Invalid input"):
        self.validator = validator
        super(W3DValidatorInput, self).__init__(
            parent, initial_value=initial_value, error_message=error_message)


class TextBlockInput(W3DValidatorInput, tk.Frame):
    """Widget for inputting a formatted block of text"""

    def get_input_value(self):
        return self.entries[0].get("1.0", tk.END)

    def set_input_value(self, value):
        self.editor.insert(tk.END, str(value))

    def _pack_entry_widgets(self):
        super(TextBlockInput, self)._pack_entry_widgets(
            pack_arguments={"fill": tk.BOTH, "expand": 1}
        )

    def initUI(self, initial_value=None):
        self.entry_widgets.append(tk.Text(self))
        super(TextBlockInput, self).initUI(initial_value=initial_value)


class StringInput(W3DValidatorInput, tk.Frame):

    def get_input_value(self):
        return self.entry_value.get()

    def set_input_value(self, value):
        self.entry_value.set(value)

    def initUI(self, initial_value=None):
        self.entry_widgets.append(tk.Entry(
            self, textvariable=self.entry_value))
        super(StringInput, self).initUI(initial_value=initial_value)

    def __init__(self, parent, validator, initial_value=None):
        self.entry_value = tk.stringVar()
        super(StringInput, self).__init__(
            parent, validator, initial_value=None,
            error_message="Invalid input")


class FileInput(W3DValidatorInput, tk.Frame):
    """Widget for inputting a filename"""
