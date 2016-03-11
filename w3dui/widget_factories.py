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


class WidgetCreationError(Exception):
    """Exception thrown when invalid input is given to widget_creator helper
    function"""
    def __init__(self, message):
        super(WidgetCreationError, self).__init__(message)


def class_chooser(validator, project_widget=True):
    """Choose what widget class to create given a validator

    :param str validator_name: The class name of the validator
    :param bool project_widget: True if this widget should directly input to a
    project option"""
    if project_widget:
        from .validator_widgets import P_VAL_UI_DICT as ui_dict
        # TODO: This is ugly...
    else:
        from .validator_widgets import VAL_UI_DICT as ui_dict
    try:
        entry_class = ui_dict[type(validator).__name__]
    except KeyError:
        raise WidgetCreationError(
            "Cannot choose widget for validator with given options")
    try:
        if (
                entry_class.__name__ == "ListInput" and
                validator.required_length is not None):
            entry_class = ui_dict["FixedListAlt"]
    except AttributeError:
        pass
    return entry_class


def widget_creator(
        validator=None, input_parent=None, frame=None, option_name=None,
        project_path=None, initial_value=None, error_message="Invalid input",
        project_widget=True):
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
            widget_path = input_parent.project_path.create_child_path(
                option_name)
            validator = widget_path.get_validator()
        except AttributeError as e:
            raise e
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

    entry_class = class_chooser(validator, project_widget=project_widget)
    entry_args = [frame]
    entry_kwargs = {}
    if initial_value is None:
        if input_parent is not None and option_name is not None:
            try:
                initial_value = input_parent.get_input_value()[option_name]
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

    new_widget = entry_class(*entry_args, **entry_kwargs)

    return new_widget
