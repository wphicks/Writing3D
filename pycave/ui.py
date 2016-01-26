"""Tk widgets for inputting W3DProject options"""

import tkinter as tk
from tkinter import ttk


class InputUI(object):
    """Dummy base class for building Tkinter input widgets

    Classes that inherit from InputUI should also inherit from a TK widget
    :param parent: The parent widget for this widget
    :param str title: A title to label this widget,
    :param CaveFeature feature: The feature whose options are being modified
    :param feature_key: The key for the particular option being modified"""

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
        self.feature[self.feature_key] = self.validator.def_value
        self.none_button.destroy()
        self.initUI()

    def noneUI(self):
        """Method to handle features defaulted to None

        :param factory: A callable that will return a new sensible default for
        feature"""
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
        self.create_label()

    def evaluate(self, value):
        """Convert input from TK widget to appropriate type"""
        return self.validator.coerce(value)

    def validate(self, value, silent=False):
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
    """Tkinter widget for creating a CaveFeature"""

    def __init__(self, parent, title, validator, feature, feature_key):
        super(FeatureUI, self).__init__(
            parent, title, validator, feature, feature_key)
        self.config(text=self.title_string)

    def initUI(self):
        try:
            self.feature[self.feature_key]
        except KeyError:
            self.feature[self.feature_key] = self.validator.def_value
        if self.feature[self.feature_key] is None:
            self.noneUI()
            return
        self.entries = {}
        for option in self.feature[self.feature_key].ui_order:
            self.entries[option] = self.feature[
                self.feature_key].argument_validators[option].ui(
                self, option, self.feature[self.feature_key], option)
            self.entries[option].pack(anchor=tk.W)


class FeatureListUI(InputUI, ttk.LabelFrame):
    """Tkinter widget for inputting a list of CaveFeatures"""

    def __init__(self, parent, title, validator, feature, feature_key):
        super(FeatureListUI, self).__init__(
            parent, title, validator, feature, feature_key)
        self.config(text=self.title_string)

    def add_feature(self):
        self.feature[self.feature_key].append(self.validator.correct_class())
        self.entries.append(self.validator.base_validator.ui(
            self.scroll_area.inside_frame,
            "Object {}".format(len(self.feature[self.feature_key]) - 1),
            self.feature[self.feature_key],
            len(self.feature[self.feature_key]) - 1,
            pop_out=True)
        )
        self.entries[-1].pack(anchor=tk.NW)

    def initUI(self):
        if self.feature[self.feature_key] is None:
            self.noneUI()
            return
        self.entries = []
        self.scroll_area = ScrollableFrame(self)
        self.scroll_area.pack(fill=tk.BOTH, expand=1)
        self.add_button = tk.Button(
            self, text="Add...", command=self.add_feature)
        self.add_button.pack(fill=tk.X, expand=0)


class PopOutUI(InputUI, tk.Frame):

    def edit(self):
        self.edit_window = tk.Toplevel()
        self.edit_window.title("Edit")
        self.edit_window.protocol("WM_DELETE_WINDOW", self.exit_editor)
        self.editor = self.validator.ui(
            self.edit_window, self.title_string, self.feature,
            self.feature_key)
        self.editor.pack(fill=tk.BOTH)

    def exit_editor(self):
        # TODO: Make sure last-edited value gets saved when window is destroyed
        self.edit_window.destroy()
        try:
            if "name" in self.feature[self.feature_key]:
                self.title_string = self.feature[self.feature_key]["name"]
                self.reset_label()
        except:
            pass

    def initUI(self):
        self.create_label()
        self.edit_button = tk.Button(self, text="Edit", command=self.edit)
        self.edit_button.pack(fill=tk.X)


class MultiFeatureUI(InputUI, ttk.LabelFrame):
    """Tkinter widget for creating one of several subclasses of CaveFeature"""

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
        self.entry = tk.Entry(
            self, validate='focusout', validatecommand=vcmd,
            textvariable=self.entry_value)
        self.entry.pack(side=tk.LEFT, anchor=tk.NW, expand=1)


class IterableUI(InputUI, tk.Frame):
    """Tkinter widget for inputting several of the same type of value"""

    def __init__(self, parent, title, validator, feature, feature_key):
        if feature[feature_key] is not None:
            try:
                feature[feature_key][0] = feature[feature_key][0]
            except (TypeError, IndexError):
                feature[feature_key] = list(feature[feature_key])
        super(IterableUI, self).__init__(
            parent, title, validator, feature, feature_key)

    def initUI(self):
        self.create_label()
        if self.feature[self.feature_key] is None:
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
        self.entry = tk.OptionMenu(
            self, self.entry_value, *self.validator.valid_menu_items)
        self.entry.pack(anchor=tk.W, side=tk.LEFT)
