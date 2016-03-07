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
from pyw3d.structs import SortedList


class ListInput(ProjectInput, ScrollableFrame):
    """Widget for entering lists of project elements"""

    def get_input_value(self):
        return [widget.get_input_value() for widget in self.entry_elements]

    def _remove_index(self, index):
        """Remove element at given index from project"""
        self.entry_widgets[index + 2].destroy()
        del self.entry_widgets[index + 2]
        del self.entry_elements[index]

    def _add_element(self, initial_value=None):
        self.project_path.get_element().append(self.validator.def_value)
        self.entry_widgets.append(tk.Frame(self.entry_widgets[0]))
        self.entry_widgets[-1].pack(fill=tk.X, expand=1)
        creator_kwargs = {
            "validator": self.validator.get_base_validator(
                len(self.entry_elements)),
            "input_parent": self,
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
            pack_arguments={"fill": tk.X, "anchor": tk.NW, "expand": 1}
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
        self.entry_elements = []
        super(ListInput, self).__init__(
            parent, validator, project_path, initial_value=initial_value,
            error_message=error_message)
        self.target_frame = self.inside_frame


class SortedListInput(ListInput, tk.Frame):
    """Widget for inputting a SortedList"""

    def get_input_value(self):
        return SortedList(super(SortedListInput, self).get_input_value())


class FixedListInput(ProjectInput, tk.Frame):
    """Widget for inputting a list of fixed size as a project option"""

    def get_input_value(self):
        return [widget.get_input_value() for widget in self.entry_widgets]

    def set_input_value(self, iterable):
        for widget, value in zip(self.entry_widgets, iterable):
            widget.set_input_value(value)

    def _pack_entry_widgets(self):
        super(FixedListInput, self)._pack_entry_widgets(
            pack_arguments={"anchor": tk.W, "side": tk.LEFT}
        )

    def initUI(self, initial_value=None):
        for i in range(self.validator.required_length):
            creator_kwargs = {
                "validator": self.validator.get_base_validator(i),
                "input_parent": self,
                "frame": self,
                "option_name": i
            }
            if initial_value is not None:
                creator_kwargs["initial_value"] = initial_value[i]
            self.entry_widgets.append(widget_creator(
                **creator_kwargs))
        super(FixedListInput, self).initUI(initial_value=initial_value)


class DictIndexError(Exception):
    """Exception thrown when a bad pair_index is used in DictInput"""
    def __init__(self, message):
        super(DictIndexError, self).__init__(message)


class DictInput(ProjectInput, ScrollableFrame):
    """Widget for editing dictionary elements"""

    def store_value(self):
        return

    def get_input_value(self):
        base = self.validator.def_value
        for pair_index in self.value_widgets:
            base[self.key_widgets[
                pair_index].get_input_value()] = self.value_widgets[
                pair_index].get_input_value()
        return base

    def _index_from_key_widget(self, key_widget):
        """Return pair_index for given key_widget"""
        for index, widget in self.key_widgets.items():
            if widget is key_widget:
                return index
        raise DictIndexError(
            "Given widget is not in key_widgets dictionary")

    def _remove_pair(self, pair_index):
        """Remove key, value pair specified by pair_index and delete associated
        widgets"""
        self.pair_frames[pair_index].destroy()
        try:
            self.value_widgets[pair_index].project_path.del_element()
            del self.value_widgets[pair_index]
        except KeyError:
            pass
        del self.key_widgets[pair_index]
        del self.pair_frames[pair_index]

    def _add_value(self, pair_index, initial_value=None):
        """Create new widget to accept value for key specified by pair_index"""
        key_widget = self.key_widgets[pair_index]
        new_key = key_widget.get_input_value()
        creator_kwargs = {
            "validator": self.validator.get_value_validator(),
            "option_name": new_key,
            "input_parent": self,
            "frame": self.pair_frames[pair_index],
        }
        if initial_value is not None:
            creator_kwargs["initial_value"] = initial_value
        value_widget = widget_creator(**creator_kwargs)
        self.value_widgets[pair_index] = value_widget
        value_widget.pack(side=tk.RIGHT, fill=tk.X, expand=1)
        pair_destroy = tk.Button(
            self.pair_frames[pair_index], text="Delete",
            command=lambda: self._remove_pair(
                self._index_from_key_widget(key_widget)
            )
        )
        pair_destroy.pack(side=tk.RIGHT)

    def _update_key(self, key_widget, initial_value=None):
        """Update key associated with given widget, creating new value widget
        if necessary"""
        if not key_widget.validate_input():
            return
        pair_index = self._index_from_key_widget(key_widget)
        new_key = key_widget.get_input_value()
        new_path = self.project_path.create_child_path(
            new_key)
        if pair_index in self.value_widgets.keys():
            value_widget = self.value_widgets[pair_index]
            old_key = value_widget.project_path.get_specifier()
            value_widget.project_path = new_path
            del self.project_path.get_element()[old_key]
        else:
            self._add_value(self, pair_index, initial_value=initial_value)

    def _add_key(self, initial_value=None):
        """Add a widget to accept another key value for dictionary"""
        if len(self.key_widgets) > len(self.value_widgets):
            return
        self.entry_widgets.append(tk.Frame(self.entry_widgets[0]))
        self.entry_widgets[-1].pack(fill=tk.X, expand=1)
        creator_kwargs = {
            "validator": self.validator.get_key_validator(),
            "input_parent": self,
            "frame": self.entry_widgets[-1],
            "project_widget": False
        }
        if initial_value is not None:
            creator_kwargs["initial_value"] = initial_value
        new_entry = widget_creator(**creator_kwargs)
        new_entry.bind("<FocusOut>", lambda: self._update_key(new_entry))
        new_entry.pack(side=tk.LEFT, expand=1)
        self.key_widgets[self._pair_index] = new_entry
        self.pair_frames[self._pair_index] = self.entry_widgets[-1]
        self._pair_index += 1

    def _pack_entry_widgets(self):
        super(DictInput, self)._pack_entry_widgets(
            pack_arguments={"fill": tk.X, "expand": 1}
        )

    def initUI(self, initial_value=None):
        self.entry_widgets.append(tk.Frame(self.target_frame))
        self.entry_widgets.append(tk.Button(
            self.target_frame, text="Add", command=self._add_element)
        )
        super(DictInput, self).initUI(initial_value=initial_value)

    def __init__(
            self, parent, validator, project_path, initial_value=None,
            error_message=None):
        super(DictInput, self).__init__(
            parent, validator, project_path, initial_value=initial_value,
            error_message=error_message)
        self.target_frame = self.inside_frame
        self._pair_index = 0
        self.key_widgets = {}
        self.pair_frames = {}
        self.value_widgets = {}
