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

"""Tk widgets for inputting entire W3D features"""

from .base import ProjectInput, W3DValidatorInput
from .text import ValidatedTextBlock, ValidatedStringInput, ValidatedFileInput


VAL_UI_DICT = {
    "TextValidator": ValidatedTextBlock,
    "ValidPyString": ValidatedStringInput,
    "ValidFile": ValidatedFileInput
}


class WidgetCreationError(Exception):
    """Exception thrown when invalid input value is given"""
    def __init__(self, message):
        super(WidgetCreationError, self).__init__(message)


def widget_creator(
        validator=None, input_parent=None, frame=None, option_name=None,
        project_path=None, initial_value=None, error_message="Invalid input"):
    """Create a widget with the given information, if possible

    :param Validator validator: The validator for this widget
    :param ProjectInput input_parent: The editing widget for the parent of this
    option
    :param frame: The tk element to serve as the tk parent of this widget
    :param option_name: The name/index specifying the option being edited
    :param ProjectPath project_path: The project_path for the parent of this
    object
    :param initial_value: An initial_value to set this option to
    :param error_message: An error message to be displayed if this option
    receives an invalid value"""
    if validator is None:
        if input_parent is None or option_name is None:
            raise WidgetCreationError(
                "Insufficient information to determine widget type")
        try:
            validator = input_parent.get_input_value(
                ).argument_validators[option_name]
        except KeyError:
            raise WidgetCreationError(
                "Validator must be specified for this widget")
    if frame is None:
        if input_parent is None:
            raise WidgetCreationError(
                "No valid parent widget specified")
        frame = input_parent

    entry_class = VAL_UI_DICT[type(validator).__name__]
    entry_args = [frame]
    entry_kwargs = {}
    if initial_value is None:
        if input_parent is not None and option_name is not None:
            try:
                initial_value = input_parent.get_stored_value()[option_name]
            except (KeyError, IndexError):
                pass
    if initial_value is not None:
        entry_kwargs["initial_value"] = initial_value

    if issubclass(entry_class, W3DValidatorInput):
        entry_args.append(validator)
    if issubclass(entry_class, ProjectInput):
        if input_parent is None:
            raise WidgetCreationError(
                "option_name must be specified for this widget")
        entry_args.append(
            input_parent.project_path.create_child_path(option_name)
        )

    return entry_class(*entry_args, **entry_kwargs)
