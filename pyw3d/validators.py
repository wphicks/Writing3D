"""Tools for validating options provided to W3D features"""

import re
import os
import warnings
from collections import defaultdict
try:
    from .ui import BaseUI, FeatureListUI, IterableUI, OptionUI, FeatureUI,\
        PopOutUI, MultiFeatureUI, MultiFeatureListUI, FeatureDictUI, FileUI,\
        TextUI, UpdateOptionUI, ListUI
except ImportError:
    warnings.warn(
        "Could not load tkinter; GUI editor will not be available")


PY_ID_REGEX = re.compile(r"^[A-Za-z0-9_]+$")


class Validator(object):
    """Callable object for validating input

    :param W3DProject project: The project this validator is being used for.
    If specified, this allows for consistency checks between related elements
    of the project."""

    def __init__(self, project=None):
        self.help_string = "No help available for this option"
        # def_value is an attribute used to provide some guidance on a
        # reasonable value to default to when first creating an instance of
        # this option in a GUI environment
        self.def_value = ""
        self.project = project

    def __call__(self, value):
        return False

    def set_project(self, project):
        self.project = project

    def help(self):
        return self.help_string

    def ui(self, parent, label, feature, feature_key, pop_out=False):
        if pop_out:
            return PopOutUI(parent, label, self, feature, feature_key)
        return BaseUI(parent, label, self, feature, feature_key)


class TextValidator(Validator):
    """Callable object for checking if value is valid text"""

    def __init__(self):
        self.help_string = "Must be text"
        self.def_value = ""

    def __call__(self, value):
        return True

    def coerce(self, value):
        new_value = str(value)
        return new_value

    def ui(self, parent, label, feature, feature_key, pop_out=True):
        if pop_out:
            return PopOutUI(parent, label, self, feature, feature_key)
        return TextUI(parent, label, self, feature, feature_key)


class ValidPyString(Validator):
    """Callable object for checking if string can be used as part of a Python
    variable name"""

    def __init__(self):
        self.help_string = "Name must be unique and contain only alphanumeric"
        " characters or underscore"
        self.def_value = ""

    def __call__(self, value):
        return bool(PY_ID_REGEX.match(str(value))) or not len(str(value))

    def coerce(self, value):
        new_value = str(value)
        new_value = re.sub(r"[^A-Za-z0-9_]", lambda x: "_", new_value)
        return new_value


class ValidFile(Validator):

    def __init__(self, help_string=None):
        if help_string is None:
            self.help_string = "Must be an existing file"
        else:
            self.help_string = help_string
        self.def_value = ""

    def __call__(self, value):
        return os.path.isfile(value)

    def coerce(self, value):
        # TODO: Think about something clever with os.path here
        return str(value)

    def ui(self, parent, label, feature, feature_key, pop_out=False):
        if pop_out:
            return PopOutUI(parent, label, self, feature, feature_key)
        return FileUI(parent, label, self, feature, feature_key)


class OptionListValidator(Validator):
    """Callable object that returns true if value is in given list"""

    def __init__(self, *valid_options):
        self.valid_options = valid_options
        self.valid_menu_items = [
            str(option) for option in self.valid_options]
        self.help_string = "Value must be one of " + ", ".join(
            self.valid_menu_items)
        try:
            self.def_value = self.valid_options[0]
        except IndexError:
            self.def_value = ""

    def __call__(self, value):
        return value in self.valid_options

    def coerce(self, value):
        if value in self.valid_options:
            return value
        return self.valid_options[
            self.valid_menu_items.index(str(value))]

    def ui(self, parent, label, feature, feature_key, pop_out=False):
        if pop_out:
            return PopOutUI(parent, label, self, feature, feature_key)
        return OptionUI(parent, label, self, feature, feature_key)


class ListValidator(Validator):
    """Used to validate an option which takes a list of values

    :param Validator base_validator: Used to validate each item in list"""

    def __init__(self, base_validator, item_label="Item", help_string=None):
        self.base_validator = base_validator
        self.item_label = item_label
        if help_string is None:
            self.help_string = "No help available for this option"
        else:
            self.help_string = help_string

    @property
    def def_value(self):
        return []

    def __call__(self, iterable):
        for value in iterable:
            if not self.base_validator(value):
                return False
        return True

    def ui(self, parent, label, feature, feature_key, pop_out=False):
        return ListUI(
            parent, label, self, feature, feature_key,
            item_label=self.item_label, pop_out=pop_out)


class ProjectOptionValidator(Validator):
    """OptionListValidator populated with options specified in a W3DProject

    For example, this validator could be used to select from the objects in a
    particular project
    :param Validator fallback_validator: A fallback validator used in case
    project has not been set for this validator
    :param project_option_selector: A callable that takes a W3DProject as
    input and returns a list of strings representing valid options"""

    def __init__(
            self, fallback_validator, project_option_selector, project=None,
            help_string=None):
        self.project = project
        if help_string is None:
            self.help_string = "No help available for this option"
        else:
            self.help_string = help_string
        self.fallback_validator = fallback_validator
        self.def_value = self.fallback_validator.def_value
        self.project_option_selector = project_option_selector
        self._valid_options = []

    def __call__(self, value):
        if self.project is None:
            return self.fallback_validator(value)
        return value in self.valid_options

    @property
    def valid_options(self):
        for option in self.project_option_selector(self.project):
            if option not in self._valid_options:
                self._valid_options.append(option)
        self._valid_options.sort()
        return self._valid_options

    def ui(self, parent, label, feature, feature_key, pop_out=False):
        if pop_out:
            return PopOutUI(parent, label, self, feature, feature_key)
        if self.project is None:
            return self.fallback_validator.ui(
                parent, label, feature, feature_key, pop_out=False)
        return UpdateOptionUI(parent, label, self, feature, feature_key)


class IsBoolean(OptionListValidator):
    """Callable object that returns true if value is valid Boolean

    Since all Python objects can be evaluated as a Boolean, this always
    returns true. Included to provide convenient methods for inputting Boolean
    options"""

    def __init__(self):
        super(IsBoolean, self).__init__(True, False)
        self.def_value = True

    def __call__(self, value):
        return True


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
                (self.help_string,  "and >= {}".format(
                    self.min_value)))
            self.def_value = self.min_value
        else:
            self.def_value = 0
        if self.max_value is not None:
            self.help_string = " ".join(
                (self.help_string,  "and <= {}".format(
                    self.max_value)))

    def __call__(self, value):
        try:
            value = float(value)
            if ((self.min_value is None or value >= self.min_value) and
                    (self.max_value is None or value <= self.max_value)):
                return True

        except TypeError:
            return False

    def coerce(self, value):
        try:
            if value == int(value):
                return value
        except ValueError:
            pass
        return float(value)


class IsNumericIterable(Validator):
    """Callable object that returns true if value is a numeric iterable

    :param required_length: Optionally sets required length for iterable. If
    this attribute is set to None, length is not checked."""

    def __init__(self, required_length=None, min_value=None, max_value=None):
        self.required_length = required_length
        if self.required_length is not None:
            self.help_sting = \
                "Value must be a sequence of {} numeric values".format(
                    self.required_length)
        else:
            self.help_string = "Value must be a sequence of numeric values"
        self.base_validator = IsNumeric(
            min_value=min_value, max_value=max_value)

    def __call__(self, iterable):
        try:
            for value in iterable:
                if not self.base_validator(value):
                    return False  # Non-numeric
            return (self.required_length is None or len(iterable) ==
                    self.required_length)
        except TypeError:
            return False  # Non-iterable

    @property
    def def_value(self):
        if self.required_length is not None:
            return [
                self.base_validator.def_value for i in
                range(self.required_length)
            ]
        return []

    def ui(self, parent, label, feature, feature_key, pop_out=False):
        if pop_out:
            return PopOutUI(parent, label, self, feature, feature_key)
        return IterableUI(parent, label, self, feature, feature_key)

    def coerce(self, iterable):
        return [self.base_validator.coerce(value) for value in iterable]


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


class FeatureValidator(Validator):
    """Check if value is a W3DFeature of specified type"""

    def __init__(self, correct_class, help_string=None):
        self.correct_class = correct_class
        if help_string is None:
            self.help_string = "Value must be of type {}".format(
                self.correct_class)
        else:
            self.help_string = help_string

    def __call__(self, value):
        return isinstance(value, self.correct_class)

    def coerce(self, value):
        return self.correct_class(**value)

    @property
    def def_value(self):
        return self.correct_class()

    def ui(self, parent, label, feature, feature_key, pop_out=False):
        if pop_out:
            return PopOutUI(parent, label, self, feature, feature_key)
        return FeatureUI(parent, label, self, feature, feature_key)


class MultiFeatureValidator(Validator):
    """Check if value is a W3DFeature of several specified types
    """

    def __init__(self, class_list, help_string=None):
        self.class_list = class_list
        self.valid_menu_items = [
            class_.__name__ for class_ in self.class_list]
        self.base_validators = [
            FeatureValidator(class_) for class_ in self.class_list]
        if help_string is None:
            self.help_string = "Value must be one of {}".format(
                ", ".join(self.valid_menu_items))
        else:
            self.help_string = help_string

    def __call__(self, value):
        for validator in self.base_validators:
            if validator(value):
                return True
        return False

    def coerce(self, value):
        for validator in self.base_validators:
            try:
                return validator.coerce(value)
            except:
                pass

    @property
    def def_value(self):
        return self.class_list[0]()

    def ui(self, parent, label, feature, feature_key, pop_out=False):
        if pop_out:
            return PopOutUI(parent, label, self, feature, feature_key)
        return MultiFeatureUI(parent, label, self, feature, feature_key)


class FeatureListValidator(Validator):
    """Check if value is an iterable of W3DFeatures of a particular type"""

    def __init__(self, correct_class, help_string=None):
        self.correct_class = correct_class
        if help_string is None:
            self.help_string = "Value must be an iterable of elements of type "
            "{}".format(
                self.correct_class)
        else:
            self.help_string = help_string
        self.base_validator = FeatureValidator(self.correct_class)

    def __call__(self, iterable):
        for item in iterable:
            if not self.base_validator(item):
                return False
        return True

    @property
    def def_value(self):
        return []

    def ui(self, parent, label, feature, feature_key, pop_out=False):
        if pop_out:
            return PopOutUI(parent, label, self, feature, feature_key)
        return FeatureListUI(parent, label, self, feature, feature_key)


class MultiFeatureListValidator(Validator):
    """Check if value is an iterable of W3DFeatures of several specified
    types"""

    def __init__(self, class_list, help_string=None, item_label="Item"):
        self.class_list = class_list
        self.valid_menu_items = [
            class_.__name__ for class_ in self.class_list]
        self.base_validator = MultiFeatureValidator(self.class_list)
        self.item_label = item_label
        if help_string is None:
            self.help_string = "Value must be an iterable of elements of one"
            "of the following types {}".format(
                ", ".join(self.valid_menu_items))
        else:
            self.help_string = help_string

    def __call__(self, iterable):
        for item in iterable:
            if not self.base_validator(item):
                return False
        return True

    def coerce(self, iterable):
        return [self.base_validator.coerce(item) for item in iterable]

    @property
    def def_value(self):
        return []

    def ui(self, parent, label, feature, feature_key, pop_out=False):
        if pop_out:
            return PopOutUI(parent, label, self, feature, feature_key)
        return MultiFeatureListUI(
            parent, label, self, feature, feature_key,
            item_label=self.item_label)


class ValidFeatureDict(Validator):
    """Check if input is dictionary with lists of W3DFeatures as values

    :param class_list: A list of classes which are acceptable as values in this
    dictionary
    :param str key_label: A label indicating what the keys of this dictionary
    are"""

    def __init__(
            self, class_list, key_validator=AlwaysValid(), key_label=None,
            help_string=None, value_label="Item"):
        if help_string is None:
            self.help_string = "Must be a dictionary with lists of"
            " W3DFeatures as values"
        else:
            self.help_string = help_string
        self.key_validator = key_validator
        self.key_label = key_label
        self.value_label = value_label
        self.value_validator = MultiFeatureListValidator(
            class_list, item_label=self.value_label)

    @property
    def def_value(self):
        return defaultdict(list)

    def __call__(self, dictionary):
        for key, value in dictionary.items():
            if (
                    not self.key_validator(key) or
                    not self.value_validator(value)):
                return False
        return True

    def coerce(self, dictionary):
        new_dict = self.def_value
        for key, value in dictionary.items():
            new_dict[
                self.key_validator.coerce(key)] = self.value_validator.coerce(
                value)
        return new_dict

    def ui(self, parent, label, feature, feature_key, pop_out=False):
        if pop_out:
            return PopOutUI(parent, label, self, feature, feature_key)
        return FeatureDictUI(
            parent, label, self, feature, feature_key,
            item_label=self.value_label)
