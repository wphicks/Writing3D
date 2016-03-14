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
import warnings


def help_bubble(message):
    top = tk.Toplevel()
    top.title("Error")
    error_message = tk.Message(
        top, text=message, width=200)
    error_message.pack()
    dismiss = tk.Button(top, text="Dismiss", command=top.destroy)
    dismiss.pack()


class InvalidInput(Exception):
    """Exception thrown when invalid input value is given"""
    def __init__(self, message):
        super(InvalidInput, self).__init__(message)


class InputUI(object):
    """Base class for building Tkinter input widgets

    Classes that inherit from InputUI should also inherit from a TK widget like
    tk.Frame or ttk.LabelFrame
    :param parent: The parent widget for this widget
    :param initial_value: The initial value for this input option
    :param str error_message: An error message to be displayed if this option
    received invalid input
    :ivar target_frame: The widget that should act as a parent for child
    widgets. This is usually self but need not necessarily be so
    """

    def destroy(self):
        try:
            if self.validate_input():
                self.store_value()
            else:
                warnings.warn(
                    "Error processing input on exit!"
                )
        except Exception as proc_error:
            warnings.warn(
                "Error processing input on exit:\n{}".format(str(proc_error))
            )
        super(InputUI, self).destroy()

    def get_stored_value(self):
        """Gets the current value of this option in the associated
        W3DProject"""
        pass

    def store_value(self, value=None):
        """Stores the current input value in a W3DProject"""
        pass

    def validate_input(self):
        """Return true if input is valid for this option"""
        return True

    def get_input_value(self, value=None):
        """Returns the current input value for this widget

        :raise InvalidInput: if input value can't be read as a valid value"""
        return value

    def set_input_value(self, value):
        """Sets the displayed input value to given value"""
        pass

    def _process_input(self, event, silent=False):
        """Store input if valid; otherwise display error message"""
        try:
            if self.validate_input():
                self.store_value()
            else:
                help_bubble(self.error_message)
        except Exception as proc_error:
            if not silent:
                help_bubble("\n".join(
                    (
                        self.error_message,
                        "\nError during processing:",
                        str(proc_error)
                    )
                ))

    def _pack_entry_widgets(self, pack_arguments={}):
        """Pack all entry widgets in self

        :param dict pack_arguments: A dictionary of keyword arguments used to
        pack the entry_widgets"""
        for entry in self.entry_widgets:
            entry.pack(**pack_arguments)

    def initUI(self, initial_value=None):
        """Set up all necessary child widgets
        """
        self.set_input_value(initial_value)
        self._pack_entry_widgets()
        self.bind("<FocusOut>", self._process_input)

    def __init__(
            self, parent, initial_value=None, error_message="Invalid input"):
        try:  # Base TK widget __init__
            super(InputUI, self).__init__(parent.target_frame)
        except AttributeError:
            super(InputUI, self).__init__(parent)
        self.entry_widgets = []
        self.error_message = error_message
        self.target_frame = self
        self.initUI(initial_value=initial_value)


class W3DValidatorInput(InputUI):
    """TK widget for getting input and validating with a W3D-style validator

    :param Validator validator: A W3D-style validator"""

    def get_input_value(self, value=None):
        return super().get_input_value(value=self.validator.coerce(value))

    def validate_input(self):
        return (
            self.validator(self.get_input_value()) and
            super(W3DValidatorInput, self).validate_input()
        )

    def __init__(
            self, parent, validator, initial_value=None,
            error_message=None):
        self.validator = validator
        if error_message is None:
            error_message = self.validator.help_string
        if initial_value is None:
            initial_value = self.validator.def_value
        super(W3DValidatorInput, self).__init__(
            parent, initial_value=initial_value, error_message=error_message)


class ProjectInput(W3DValidatorInput):
    """TK widget for validating and storing options for a W3D-style project

    This widget overrides methods from InputUI for storing and retrieving
    W3DFeature options conveniently

    :param ProjectPath project_path: Specifies the option associated with this
    input widget"""

    def get_stored_value(self):
        return self.project_path.get_element()

    def store_value(self, value=None):
        if value is None:
            self.project_path.set_element(self.get_input_value())
        else:
            self.project_path.set_element(value)

    def __init__(
            self, parent, validator, project_path, initial_value=None,
            error_message=None):
        self.project_path = project_path
        super(ProjectInput, self).__init__(
            parent, validator, initial_value=initial_value,
            error_message=error_message)
        self.project_path.set_element(self.get_input_value())
