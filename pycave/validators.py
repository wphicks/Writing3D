"""Tools for validating options provided to Cave features"""

import tkinter as tk
from tkinter import ttk


class Validator(object):
    """Callable object for validating input"""

    def __init__(self):
        self.help_string = "No help available for this option"

    def __call__(self, value):
        return False

    def help(self):
        return self.help_string


class OptionListValidator(Validator):
    """Callable object that returns true if value is in given list"""

    def __init__(self, *valid_options):
        self.valid_options = set(valid_options)
        self.help_string = "Value must be one of " + " ,".join(
            self.valid_options)

    def __call__(self, value):
        return value in self.valid_options


class NumericUI(tk.Frame):
    """Tkinter widget for inputting numeric values"""

    def help_bubble(self):
        top = tk.Toplevel()
        top.title("Error")
        error_message = tk.Message(
            top, text=self.validator.help_string, width=200)
        error_message.pack()
        dismiss = tk.Button(top, text="Dismiss", command=top.destroy)
        dismiss.pack()

    def validate(self, value):
        try:
            valid = self.validator(float(value))
        except:
            valid = False
        if not valid:
            self.help_bubble()
        return valid

    def __init__(self, parent, title, validator):
        super(NumericUI, self).__init__(parent)
        self.parent = parent
        self.title_string = title
        self.initUI()
        self.validator = validator

    def initUI(self):
        self.label = tk.Label(self, text="{}:".format(self.title_string))
        self.label.pack(anchor=tk.W, side=tk.LEFT)
        vcmd = (self.register(self.validate), '%P')
        self.entry = tk.Entry(
            self, validate='focusout', validatecommand=vcmd)
        self.entry.pack(side=tk.LEFT, anchor=tk.W, expand=1)


class IsNumeric(Validator):
    """Return true if value can be interpreted as a numeric type

    :param min_value: Optionally sets minimum value. If set to None, check is
    not performed
    :param max_value: Optionally sets maximum value. If set to None, check is
    not performed
    """

    def __init__(self, min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value

        self.help_string = "Value must be numeric"
        if self.min_value is not None:
            self.help_string = " ".join(
                (self.help_string,  "and greater than {}".format(
                    self.min_value)))
        if self.max_value is not None:
            self.help_string = " ".join(
                (self.help_string,  "and less than {}".format(
                    self.max_value)))

    def __call__(self, value):
        try:
            float(value)
            if ((self.min_value is None or value >= self.min_value) and
                    (self.max_value is None or value <= self.max_value)):
                return True

        except TypeError:
            return False

    def ui(self, parent, label):
        return NumericUI(parent, label, self)


class IsNumericIterable(Validator):
    """Callable object that returns true if value is a numeric iterable

    :param required_length: Optionally sets required length for iterable. If
    this attribute is set to None, length is not checked."""

    def __init__(self, required_length=None):
        self.required_length = required_length
        if self.required_length is not None:
            self.help_sting = \
                "Value must be a sequence of {} numeric values".format(
                    self.required_length)
        else:
            self.help_string = "Value must be a sequence of numeric values"

    def __call__(self, iterable):
        try:
            for value in iterable:
                if not IsNumeric(value):
                    return False  # Non-numeric
            return (self.required_length is None or len(iterable) ==
                    self.required_length)
        except TypeError:
            return False  # Non-iterable


class AlwaysValid(Validator):
    """Always returns True"""

    def __init__(self,
                 help_string="All Python objects are valid for this option"):
        self.help_string = help_string

    def __call__(self, value):
        return True


class CheckClass(Validator):
    """Returns True if value is of given class

    Also offers the "coerce" method, which will attempt to create object of
    specified class from value.
    Note: While this is not an especially Pythonic check, it is used sparsely
    and avoids the hassle of building up individual validators for input
    purposes."""

    def __init__(self, correct_class=bool, help_string=None):
        self.correct_class = correct_class
        if help_string is None:
            self.help_string = "Value must be of type {}".format(
                self.correct_class)
        else:
            self.help_string = help_string

    def __call__(self, value):
        return isinstance(value, self.correct_class)

    def coerce(self, value):
        return self.correct_class(value)


class FeatureListUI(ttk.LabelFrame):
    """Tkinter widget for inputting a list of CaveFeatures"""

    def __init__(self, parent, title):
        super(FeatureListUI, self).__init__(parent, text=title)
        self.title_string = title
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.add_button = tk.Button(self, text="Add...")
        self.add_button.pack(anchor=tk.S, fill=tk.X, expand=1)


class FeatureListValidator(Validator):
    """Check if value is an iterable of CaveFeatures of a particular type"""

    def __init__(self, correct_class, help_string=None):
        self.correct_class = correct_class
        if help_string is None:
            self.help_string = "Value must be an iterable of elements of type "
            "{}".format(
                self.correct_class)
        else:
            self.help_string = help_string

    def __call__(self, iterable):
        for item in iterable:
            if not isinstance(item, self.correct_class):
                return False
        return True

    def ui(self, parent, label):
        return FeatureListUI(parent, label)
