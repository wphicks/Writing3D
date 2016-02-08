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
import tkinter.filedialog
from tkinter import ttk
from .project import W3DProject


class ProjectOptions(tk.Frame):
    """A frame for providing global project option input"""

    def __init__(self, parent, project):
        super(ProjectOptions, self).__init__(parent)
        self.parent = parent
        self.project = project
        self.initUI()

    def add_entries(self):
        self.entries = {}
        self.entries["far_clip"] = W3DProject.argument_validators[
            "far_clip"].ui(self, "Camera far clip", self.project, "far_clip")
        self.entries["background"] = W3DProject.argument_validators[
            "background"].ui(
            self, "Background color", self.project, "background")
        self.entries["allow_movement"] = W3DProject.argument_validators[
            "allow_movement"].ui(
            self, "Allow movement", self.project, "allow_movement")
        self.entries["allow_rotation"] = W3DProject.argument_validators[
            "allow_rotation"].ui(
            self, "Allow rotation", self.project, "allow_movement")
        self.entries["camera_placement"] = W3DProject.argument_validators[
            "camera_placement"].ui(
            self, "Camera placement", self.project, "camera_placement")

    def initUI(self):
        self.add_entries()
        self.title_string = "Global Options"
        for option in [
                "far_clip", "background", "allow_movement", "allow_rotation",
                "camera_placement"]:
            self.entries[option].pack(anchor=tk.W)
        self.pack(fill=tk.BOTH, expand=1)


class InputUI(object):
    """Dummy base class for building Tkinter input widgets

    Classes that inherit from InputUI should also inherit from a TK widget
    :param parent: The parent widget for this widget
    :param str title: A title to label this widget,
    :param W3DFeature feature: The feature whose options are being modified
    :param feature_key: The key for the particular option being modified"""

    def set_project(self, project):
        """Set the current W3DProject for this UI widget

        :param W3DProject project: The project for this widget"""
        self.validator.set_project(project)
        self.destroy()
        self.initUI()

    def help_bubble(self):
        top = tk.Toplevel()
        top.title("Error")
        error_message = tk.Message(
            top, text=self.validator.help_string, width=200)
        error_message.pack()
        dismiss = tk.Button(top, text="Dismiss", command=top.destroy)
        dismiss.pack()

    def initTK(self):
        """Call base TK widget __init__ method"""
        super(InputUI, self).__init__(self.parent)

    def _clear_none(self):
        """Set value to new (non-None) default and re-initialize UI"""
        self.none_flag = False
        self.feature[self.feature_key] = self.validator.def_value
        self.none_button.destroy()
        self.initUI()

    def noneUI(self):
        """Method to handle features defaulted to None

        :param factory: A callable that will return a new sensible default for
        feature"""
        self.none_flag = True
        self.none_button = tk.Button(
            self, text="Create", command=self._clear_none)
        self.none_button.pack(fill=tk.X)

    def create_label(self):
        """Create element to label this widget"""
        if self.title_string is not None and not hasattr(self, "label"):
            self.label = tk.Label(self, text="{}:".format(self.title_string))
            self.label.pack(anchor=tk.W, side=tk.LEFT)

    def reset_label(self):
        """Reset label with new title_string"""
        self.label.config(text="{}:".format(self.title_string))

    def initUI(self):
        """Add all elements to build up this widget"""
        try:
            self.entry_value.set(str(self.feature[self.feature_key]))
        except (KeyError, IndexError):
            pass
        self.create_label()

    def evaluate(self, value):
        """Convert input from TK widget to appropriate type"""
        return self.validator.coerce(value)

    def validate(self, value, silent=False):
        if self.none_flag:
            return True
        try:
            valid = self.validator(self.evaluate(value))
        except:
            valid = False
        if not valid:
            if not silent:
                self.help_bubble()
        else:
            self.feature[self.feature_key] = self.evaluate(value)
        return valid

    def __init__(self, parent, title, validator, feature, feature_key):
        self.parent = parent
        self.title_string = title
        self.validator = validator
        self.entry_value = tk.StringVar()
        self.feature = feature
        self.feature_key = feature_key
        self.none_flag = False
        try:
            cur_value = self.feature[self.feature_key]
        except KeyError:
            cur_value = None
        if cur_value is not None:
            self.entry_value.set(str(cur_value))
        else:
            self.entry_value.set("")
        self.initTK()
        self.initUI()


class TextUI(InputUI, tk.Frame):

    def destroy(self):
        self.validate(silent=True)
        super(TextUI, self).destroy()

    def validate(self, silent=False):
        if self.none_flag:
            return True
        value = self.editor.get("1.0", tk.END)
        try:
            valid = self.validator(self.evaluate(value))
        except:
            valid = False
        if not valid:
            if not silent:
                self.help_bubble()
        else:
            self.feature[self.feature_key] = self.evaluate(value)
        return valid

    def initUI(self):
        self.editor = tk.Text(self)
        try:
            self.editor.insert(tk.END, self.feature[self.feature_key])
        except (KeyError, IndexError):
            pass
        self.editor.bind("<FocusOut>", self.validate)
        self.editor.pack(fill=tk.BOTH, expand=1)


class FileUI(InputUI, tk.Frame):

    def validate(self, value):
        return super(FileUI, self).validate(value, silent=True)

    def file_dialog(self, event):
        filename = tk.filedialog.askopenfilename()
        self.entry_value.set(filename)
        self.validate(self.entry_value.get())

    def initUI(self):
        self.create_label()
        vcmd = (self.register(self.validate), '%P')
        try:
            self.entry_value.set(str(self.feature[self.feature_key]))
        except (KeyError, IndexError):
            pass
        self.entry = tk.Entry(
            self, validate='focusout', validatecommand=vcmd,
            textvariable=self.entry_value)
        self.entry.bind('<Button-1>', self.file_dialog)
        self.entry.pack()


class ScrollableFrame(tk.Frame):
    """Scrollable frame widget

    This implementation based on the one presented at
    http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame"""

    def __init__(self, parent, *args, **kwargs):
        super(ScrollableFrame, self).__init__(parent, *args, **kwargs)
        self.scroll = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.scroll.pack(fill=tk.Y, side=tk.RIGHT, expand=0)
        self.canvas = tk.Canvas(
            self, bd=0, highlightthickness=0, yscrollcommand=self.scroll.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.scroll.config(command=self.canvas.yview)

        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        self.inside_frame = tk.Frame(self.canvas)
        self.in_id = self.canvas.create_window(
            0, 0, window=self.inside_frame, anchor=tk.NW)

        self.inside_frame.bind('<Configure>', self._update_inside_dimensions)
        self.canvas.bind('<Configure>', self._update_canvas_dimensions)

    def _update_inside_dimensions(self, event):
        new_dims = (
            self.inside_frame.winfo_reqwidth(),
            self.inside_frame.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 {} {}".format(*new_dims))
        if self.inside_frame.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.config(width=self.inside_frame.winfo_reqwidth())

    def _update_canvas_dimensions(self, event):
        if self.inside_frame.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.itemconfigure(
                self.in_id, width=self.canvas.winfo_width())


class FeatureUI(InputUI, ttk.LabelFrame):
    """Tkinter widget for creating a W3DFeature"""

    def __init__(self, parent, title, validator, feature, feature_key):
        super(FeatureUI, self).__init__(
            parent, title, validator, feature, feature_key)
        self.config(text=self.title_string)

    def initUI(self):
        try:
            if self.feature[self.feature_key] is None:
                self.noneUI()
                return
        except KeyError:
            self.noneUI()
            return
        self.entries = {}
        for option in self.feature[self.feature_key].ui_order:
            self.entries[option] = self.feature[
                self.feature_key].argument_validators[option].ui(
                self, option, self.feature[self.feature_key], option)
            self.entries[option].pack(fill=tk.X, anchor=tk.W)


class FeatureListUI(InputUI, ttk.LabelFrame):
    """Tkinter widget for inputting a list of W3DFeatures"""

    def __init__(
            self, parent, title, validator, feature, feature_key,
            item_label="Item"):
        self.add_label = "Add {}...".format(item_label)
        self.item_label = item_label
        super(FeatureListUI, self).__init__(
            parent, title, validator, feature, feature_key)
        self.config(text=self.title_string)

    def create_add_button(self):
        try:
            self.add_button.destroy()
        except AttributeError:
            pass
        self.add_button = tk.Button(
            self.scroll_area.inside_frame, text=self.add_label,
            command=self.add_feature)
        self.add_button.pack(fill=tk.X, expand=0)

    def add_feature(self):
        self.feature[self.feature_key].append(self.validator.correct_class())
        self.entries.append(self.validator.base_validator.ui(
            self.scroll_area.inside_frame,
            "{} {}".format(
                self.item_label, len(self.feature[self.feature_key]) - 1),
            self.feature[self.feature_key],
            len(self.feature[self.feature_key]) - 1,
            pop_out=True)
        )
        new_entry = self.entries[-1]
        destroy_button = tk.Button(
            self.entries[-1], text="Delete",
            command=lambda: self.remove_feature(new_entry.feature_key)
        )
        new_entry.pack(anchor=tk.NW)
        destroy_button.pack(side=tk.LEFT, fill=tk.X)
        self.create_add_button()

    def remove_feature(self, index):
        removed_entry = self.entries.pop(index)
        removed_entry.destroy()
        self.feature[self.feature_key].pop(index)
        for i in range(len(self.entries)):
            if i >= index:
                self.entries[i].feature_key += -1
            if "name" not in self.entries[
                    i].feature[self.entries[i].feature_key]:
                self.entries[i].title_string = "Object {}".format(i)
            self.entries[i].reset_label()

    def initUI(self):
        if self.feature[self.feature_key] is None:
            self.noneUI()
            return
        self.entries = []
        self.scroll_area = ScrollableFrame(self)
        self.scroll_area.pack(fill=tk.BOTH, expand=1)
        self.create_add_button()


class MultiFeatureListUI(InputUI, tk.Frame):
    """Tkinter widget for inputting a list of W3DFeatures of multiple types"""

    def __init__(
            self, parent, title, validator, feature, feature_key,
            item_label="Item"):
        self.add_label = "Add {}...".format(item_label)
        self.item_label = item_label
        super(MultiFeatureListUI, self).__init__(
            parent, title, validator, feature, feature_key)

    def add_feature(self):
        self.feature[self.feature_key].append(
            self.validator.base_validator.def_value)
        self.entries.append(self.validator.base_validator.ui(
            self.scroll_area.inside_frame,
            "{} {}".format(
                self.item_label, len(self.feature[self.feature_key]) - 1),
            self.feature[self.feature_key],
            len(self.feature[self.feature_key]) - 1,
            pop_out=True)
        )
        new_entry = self.entries[-1]
        destroy_button = tk.Button(
            self.entries[-1], text="Delete",
            command=lambda: self.remove_feature(new_entry.feature_key)
        )
        new_entry.pack(anchor=tk.NW)
        destroy_button.pack(side=tk.LEFT, fill=tk.X)
        self.create_add_button()

    def remove_feature(self, index):
        removed_entry = self.entries.pop(index)
        removed_entry.destroy()
        self.feature[self.feature_key].pop(index)
        for i in range(len(self.entries)):
            if i >= index:
                self.entries[i].feature_key += -1
            if "name" not in self.entries[
                    i].feature[self.entries[i].feature_key]:
                self.entries[i].title_string = "Object {}".format(i)
            self.entries[i].reset_label()

    def create_add_button(self):
        try:
            self.add_button.destroy()
        except AttributeError:
            pass
        self.add_button = tk.Button(
            self.scroll_area.inside_frame, text=self.add_label,
            command=self.add_feature)
        self.add_button.pack(fill=tk.X, expand=0)

    def initUI(self):
        if self.feature[self.feature_key] is None:
            self.noneUI()
            return
        self.entries = []
        self.scroll_area = ScrollableFrame(self)
        self.scroll_area.pack(fill=tk.X, expand=1)
        self.create_add_button()


class PopOutUI(InputUI, tk.Frame):

    def edit(self):
        self.edit_window = tk.Toplevel()
        self.edit_window.title("Edit")
        self.edit_window.protocol("WM_DELETE_WINDOW", self.exit_editor)
        self.editor = self.validator.ui(
            self.edit_window, self.title_string, self.feature,
            self.feature_key, pop_out=False)
        self.editor.pack(fill=tk.BOTH)

    def exit_editor(self):
        # TODO: Make sure last-edited value gets saved when window is destroyed
        self.edit_window.destroy()
        try:
            if ("name" in self.feature[self.feature_key] and
                    self.featre[self.feature_key]["name"] != ""):
                self.title_string = self.feature[self.feature_key]["name"]
                self.reset_label()
        except:
            pass

    def initUI(self):
        self.create_label()
        self.edit_button = tk.Button(self, text="Edit", command=self.edit)
        self.edit_button.pack(side=tk.LEFT, fill=tk.X)


class MultiFeatureUI(InputUI, ttk.LabelFrame):
    """Tkinter widget for creating one of several subclasses of W3DFeature"""

    def __init__(self, parent, title, validator, feature, feature_key):
        super(MultiFeatureUI, self).__init__(
            parent, title, validator, feature, feature_key)
        self.config(text=self.title_string)

    def create_editor(self, *args):
        self.base_validator = self.validator.base_validators[
            self.validator.valid_menu_items.index(
                self.entry_value.get())]
        if not self.base_validator(self.feature[self.feature_key]):
            self.feature[self.feature_key] = self.base_validator.def_value
        try:
            self.editor.destroy()
        except AttributeError:
            pass
        self.editor = self.base_validator.ui(
            self, self.base_validator.correct_class.__name__, self.feature,
            self.feature_key)
        self.editor.pack()

    def initUI(self):
        try:
            self.entry_value.set(
                self.feature[self.feature_key].__class__.__name__)
        except KeyError:
            self.feature[self.feature_key] = self.validator.def_value
            self.entry_value.set(
                self.feature[self.feature_key].__class__.__name__)
        self.create_label()
        self.class_picker = tk.OptionMenu(
            self, self.entry_value, *self.validator.valid_menu_items)
        self.class_picker.pack(anchor=tk.W)
        self.create_editor()

        self.entry_value.trace("w", self.create_editor)


class BaseUI(InputUI, tk.Frame):
    """Tkinter widget for inputting "primitive" values

    (e.g. ints, floats, strings, etc.)"""

    def destroy(self):
        self.validate(self.entry_value.get(), silent=True)
        super(BaseUI, self).destroy()

    def initUI(self):
        self.create_label()
        vcmd = (self.register(self.validate), '%P')
        try:
            self.entry_value.set(str(self.feature[self.feature_key]))
        except (KeyError, IndexError):
            pass
        self.entry = tk.Entry(
            self, validate='focusout', validatecommand=vcmd,
            textvariable=self.entry_value)
        self.entry.pack(side=tk.LEFT, anchor=tk.NW, expand=1)


class IterableUI(InputUI, tk.Frame):
    """Tkinter widget for inputting several of the same type of value"""

    def __init__(self, parent, title, validator, feature, feature_key):
        super(IterableUI, self).__init__(
            parent, title, validator, feature, feature_key)

    def initUI(self):
        self.create_label()
        try:  # Test for item assignment
            self.feature[
                self.feature_key][0] = self.feature[self.feature_key][0]
        except TypeError:  # Item assignment unavailable
            try:
                self.feature[self.feature_key] = list(
                    self.feature[self.feature_key])
            except TypeError:  # Feature value is None
                self.noneUI()
                return
        except (KeyError, IndexError):  # feature_key not yet assigned or len 0
                                        # iterable
            self.noneUI()
            return
        self.entry = []
        if self.validator.required_length is not None:
            self.entry = [
                self.validator.base_validator.ui(
                    self, None, self.feature[self.feature_key], i)
                for i in range(self.validator.required_length)]
            for widget in self.entry:
                widget.pack(anchor=tk.W, side=tk.LEFT)


class OptionUI(InputUI, tk.Frame):
    """Tkinter widget for selecting from a limited list of options"""

    def destroy(self):
        self.validate(self.entry_value.get())
        super(OptionUI, self).destroy()

    def initUI(self):
        self.create_label()
        try:
            if self.feature[self.feature_key] is None:
                self.noneUI()
                return
        except KeyError:
            self.noneUI()
            return
        try:
            self.entry_value.set(str(self.feature[self.feature_key]))
        except (KeyError, IndexError):
            pass
        self.entry = tk.OptionMenu(
            self, self.entry_value, *self.validator.valid_menu_items)
        self.entry.pack(anchor=tk.W, side=tk.LEFT)


class UpdateOptionUI(InputUI, tk.Frame):
    """Tkinter widget for selecting from an updateable list of options"""

    def destroy(self):
        self.validate(self.entry_value.get())
        super(UpdateOptionUI, self).destroy()

    def create_entry(self):
        try:
            self.entry.destroy()
        except AttributeError:
            pass
        self.entry = tk.OptionMenu(
            self, self.entry_value, *self.validator.valid_options)
        self.entry.bind("<FocusIn>", self.create_entry)
        self.entry.pack(anchor=tk.W, side=tk.LEFT)

    def initUI(self):
        self.create_label()
        try:
            if self.feature[self.feature_key] is None:
                self.noneUI()
                return
        except KeyError:
            self.noneUI()
            return
        try:
            self.entry_value.set(str(self.feature[self.feature_key]))
        except (KeyError, IndexError):
            pass
        self.create_entry()


class NonFeatureUI(tk.Frame):
    """Tkinter widget for input and validation of values that are not
    associated with a W3DFeature option"""

    def help_bubble(self):
        top = tk.Toplevel()
        top.title("Error")
        error_message = tk.Message(
            top, text=self.validator.help_string, width=200)
        error_message.pack()
        dismiss = tk.Button(top, text="Dismiss", command=top.destroy)
        dismiss.pack()

    def create_label(self):
        """Create element to label this widget"""
        if self.title_string is not None and not hasattr(self, "label"):
            self.label = tk.Label(self, text="{}:".format(self.title_string))
            self.label.pack(anchor=tk.W, side=tk.LEFT)

    def evaluate(self):
        return self.validator.coerce(self.entry_value.get())

    def validate(self, silent=False):
        try:
            valid = self.validator(self.evaluate())
        except:
            valid = False
        if not valid:
            if not silent:
                self.help_bubble()
        return valid

    def destroy(self):
        self.validate(silent=True)
        super(NonFeatureUI, self).destroy()

    def initUI(self):
        """Add all elements to build up this widget"""
        self.create_label()
        vcmd = (self.register(self.validate), '%P')
        self.entry = tk.Entry(
            self, validate='focusout', validatecommand=vcmd,
            textvariable=self.entry_value)
        self.entry.pack(side=tk.LEFT, anchor=tk.NW, fill=tk.X, expand=1)

    def __init__(self, parent, title, validator):
        self.parent = parent
        self.title_string = title
        self.validator = validator
        self.entry_value = tk.StringVar()
        super(NonFeatureUI, self).__init__(self.parent)
        self.initUI()


class DictEntryUI(tk.Frame):
    """Tkinter widget for inputting dictionary key-value pairs"""

    def create_value_entry(self, key):
        self.value_entry = self.value_validator.ui(
            self.data_frame, None, self.dictionary, key)
        self.value_entry.pack(side=tk.LEFT, fill=tk.X)

    def evaluate_key(self):
        return self.key_validator.coerce(self.key_entry.entry_value.get())

    def update_key(self, *args):
        new_key = self.evaluate_key()
        try:
            old_key = self.value_entry.feature_key
        except AttributeError:
            self.create_value_entry(new_key)
            return
        self.value_entry.feature[
            new_key] = self.value_entry.feature.pop(old_key)
        self.value_entry.feature_key = new_key

    def initUI(self):
        self.data_frame = tk.Frame(self.parent)
        self.key_entry = NonFeatureUI(
            self.data_frame, self.key_label, self.key_validator)
        self.key_entry.entry_value.trace('w', self.update_key)
        self.key_entry.pack(side=tk.LEFT, anchor=tk.NW)
        self.data_frame.pack(anchor=tk.N, fill=tk.X)

    def destroy_entry(self):
        self.value_entry.feature.pop(self.value_entry.feature_key)
        self.destroy()

    def __init__(
            self, parent, dictionary, key_label, key_validator,
            value_validator):
        self.parent = parent
        self.dictionary = dictionary
        self.key_label = key_label
        self.key_validator = key_validator
        self.value_validator = value_validator
        super(DictEntryUI, self).__init__(self.parent)
        self.initUI()


class FeatureDictUI(InputUI, tk.Frame):
    """Tkinter widget for building a dictionary with lists of W3DFeatures as
    values"""

    def __init__(
            self, parent, title, validator, feature, feature_key,
            item_label="Item"):
        self.add_label = "Add..."
        self.item_label = item_label
        super(FeatureDictUI, self).__init__(
            parent, title, validator, feature, feature_key)

    def add_feature(self):
        self.entries.append(
            DictEntryUI(
                self.scroll_area.inside_frame, self.feature[self.feature_key],
                self.key_label, self.validator.key_validator,
                self.validator.value_validator
            )
        )
        self.entries[-1].pack()
        self.create_add_button()

    def create_add_button(self):
        try:
            self.add_button.destroy()
        except AttributeError:
            pass
        self.add_button = tk.Button(
            self.scroll_area.inside_frame, text=self.add_label,
            command=self.add_feature)
        self.add_button.pack(fill=tk.X, expand=0)

    def initUI(self):
        self.create_label()
        self.entries = []
        self.scroll_area = ScrollableFrame(self)
        self.scroll_area.pack(fill=tk.X, expand=1)
        self.create_add_button()
        if self.validator.key_label is not None:
            self.key_label = self.validator.key_label
        else:
            self.key_label = "Key"


class ListUI(InputUI, ttk.LabelFrame):

    def __init__(
            self, parent, title, validator, feature, feature_key,
            item_label="Item", pop_out=False):
        self.add_label = "Add {}...".format(item_label)
        self.item_label = item_label
        super(ListUI, self).__init__(
            parent, title, validator, feature, feature_key)
        self.config(text=self.title_string)
        self.pop_out = pop_out

    def create_add_button(self):
        try:
            self.add_button.destroy()
        except AttributeError:
            pass
        self.add_button = tk.Button(
            self.scroll_area.inside_frame, text=self.add_label,
            command=self.add_item)
        self.add_button.pack(fill=tk.X, expand=0)

    def add_item(self):
        self.feature[self.feature_key].append(
            self.validator.base_validator.def_value)
        self.entries.append(self.validator.base_validator.ui(
            self.scroll_area.inside_frame,
            "{} {}".format(
                self.item_label, len(self.feature[self.feature_key]) - 1),
            self.feature[self.feature_key],
            len(self.feature[self.feature_key]) - 1,
            pop_out=self.pop_out)
        )
        new_entry = self.entries[-1]
        destroy_button = tk.Button(
            self.entries[-1], text="Delete",
            command=lambda: self.remove_feature(new_entry.feature_key)
        )
        new_entry.pack(anchor=tk.NW)
        destroy_button.pack(side=tk.LEFT, fill=tk.X)
        self.create_add_button()

    def remove_feature(self, index):
        removed_entry = self.entries.pop(index)
        removed_entry.destroy()
        self.feature[self.feature_key].pop(index)
        for i in range(len(self.entries)):
            if i >= index:
                self.entries[i].feature_key += -1
            if "name" not in self.entries[
                    i].feature[self.entries[i].feature_key]:
                self.entries[i].title_string = "{} {}".format(
                    self.item_label, i)
            self.entries[i].reset_label()

    def initUI(self):
        if self.feature[self.feature_key] is None:
            self.noneUI()
            return
        self.entries = []
        self.scroll_area = ScrollableFrame(self)
        self.scroll_area.pack(fill=tk.BOTH, expand=1)
        self.create_add_button()
