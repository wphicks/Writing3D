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

import tkinter as tk
from tkinter import ttk
from .base import ProjectInput, InvalidInput
from .widget_factories import widget_creator
from pyw3d.path import UnsetValueError


class FeatureInput(ProjectInput, tk.Frame):
    """Widget for editing an entire W3DFeature"""

    def get_input_value(self):
        try:
            feature = self.get_stored_value()
        except UnsetValueError:
            feature = self.validator.def_value
        for widget in self.entry_widgets:
            try:
                option_name = widget.project_path.get_specifier()
            except AttributeError:
                continue
            feature[option_name] = widget.get_input_value()
        return feature

    def set_input_value(self, value):
        for widget in self.entry_widgets:
            try:
                option_name = widget.project_path.get_specifier()
            except AttributeError:
                continue
            try:
                widget.set_input_value(value[option_name])
            except KeyError:
                widget.set_input_value(widget.validator.def_value)

    def _process_input(self, event, silent=False):
        super()._process_input(event, silent=True)

    def _get_chosen_class(self):
        """Return selected class for this widget

        :raises InvalidInput: if invalid class name is given"""
        class_name = self.class_selection.get()
        for class_ in self.classes:
            if class_.__name__ == class_name:
                return class_
        raise InvalidInput("Given class name is invalid")

    def _create_editor(self):
        """Generate widget for editing feature options"""
        if len(self.classes) == 1:
            target = ttk.LabelFrame(self.target_frame)
            target.pack(fill=tk.X)
        else:
            target = tk.Toplevel()
            target.title("Edit")
        self.entry_widgets.append(target)
        try:
            value = self.get_stored_value()
        except UnsetValueError:
            value = None
        if type(value) != self._get_chosen_class():
            self.store_value(self._get_chosen_class()())
        for option in self._get_chosen_class().ui_order:
            cur_frame = tk.Frame(target)
            cur_frame.pack(anchor=tk.NW)
            self.entry_widgets.append(
                tk.Label(cur_frame, text="{}:".format(option))
            )
            self.entry_widgets[-1].pack(anchor=tk.W, side=tk.LEFT)

            self.entry_widgets.append(widget_creator(
                frame=cur_frame, input_parent=self, option_name=option))
            self.entry_widgets[-1].pack(anchor=tk.W, side=tk.LEFT, fill=tk.X)

    def _create_class_picker(self):
        """Generate widget for choosing feature class"""
        self.entry_widgets.append(tk.OptionMenu(
            self, self.class_selection,
            *[cls.__name__ for cls in self.classes])
        )
        self.entry_widgets.append(tk.Button(
            self, text="Edit", command=self._create_editor)
        )
        self.entry_widgets[-1].pack(fill=tk.X)

    def _create_input_ui(self):
        """Create interface for editing this feature"""
        for widget in self.entry_widgets:
            widget.destroy()
        if len(self.classes) == 1:
            self._create_editor()
        else:
            self._create_class_picker()

    def initUI(self, initial_value=None):
        try:
            value = self.get_stored_value()
        except UnsetValueError:
            value = None
        if value is None:
            self.entry_widgets.append(tk.Button(
                self.target_frame, text="Add", command=self._create_input_ui)
            )
        else:
            self._create_input_ui()
        super(FeatureInput, self).initUI(initial_value=initial_value)

    def __init__(
            self, parent, validator, project_path, initial_value=None,
            error_message="Invalid input"):
        self.classes = [validator.correct_class]
        try:
            self.classes.extend(
                sorted(
                    validator.correct_class._subclass_registry.values(),
                    key=lambda x: x.__name__
                )
            )
        except AttributeError:
            pass
        self.class_selection = tk.StringVar()
        self.class_selection.set(
            self.classes[0].__name__)
        super(FeatureInput, self).__init__(
            parent, validator, project_path, initial_value=initial_value,
            error_message=error_message)
