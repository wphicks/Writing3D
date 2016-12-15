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

"""Tools for validating options provided to W3D features"""

import re
import os
import logging
LOGGER = logging.getLogger("pyw3d")
from .path import ProjectPath, UnsetValueError


PY_ID_REGEX = re.compile(r"^[A-Za-z0-9_]+$")


class Validator(object):
    """Callable object for validating input

    :param W3DProject project: The project this validator is being used for.
        If specified, this allows for consistency checks between related
        elements of the project."""

    def __init__(self):
        self.help_string = "No help available for this option"
        # def_value is an attribute used to provide some guidance on a
        # reasonable value to default to when first creating an instance of
        # this option for editing
        self.def_value = ""

    def __call__(self, value):
        return False

    def __repr__(self):
        return self.__class__.__name__

    def coerce(self, value):
        """Attempt to coerce input to a valid value for this validator"""
        return value

    def help(self):
        """Provide information on valid options for this validator"""
        return self.help_string


class TextValidator(Validator):
    """Callable object for checking if value is valid text"""

    def __init__(self):
        self.help_string = "Must be text"
        self.def_value = ""

    def __call__(self, value):
        return True

    def __repr__(self):
        return "{}()".format(super().__repr__())

    def coerce(self, value):
        new_value = str(value)
        return new_value


class ValidPyString(Validator):
    """Callable object for checking if string can be used as part of a Python
    variable name"""

    def __init__(self):
        self.help_string = "Name must be unique and contain only alphanumeric"
        " characters or underscore"
        self.def_value = ""

    def __call__(self, value):
        return bool(PY_ID_REGEX.match(str(value))) or not len(str(value))

    def __repr__(self):
        return "{}()".format(super().__repr__())

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

    def __repr__(self):
        return "{}()".format(super().__repr__())

    def coerce(self, value):
        # TODO: Think about something clever with os.path here
        return str(value)


class OptionValidator(Validator):
    """Callable object that returns true if value is in given list of options
    """

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

    def __repr__(self):
        return "{}{}".format(super().__repr__(), tuple(self.valid_menu_items))

    def coerce(self, value):
        if value in self.valid_options:
            return value
        return self.valid_options[
            self.valid_menu_items.index(str(value))]


class ListValidator(Validator):
    """Used to validate an option which takes a list of values

    :param base_validators: Either a single Validator or list of Validators
        which will be used to validate each value in list. If a list of
        validators is provided and there are more values than validators, the
        validation process will "wrap around" to the beginning of the list of
        values.
    :param str item_label: A label denoting what each item in the list is
    :param int required_length: If the list of values must be of a particular
        length, this parameter should be set to an integer. Otherwise, this
        should be None."""

    def __init__(
            self, base_validators, item_label="Item", help_string=None,
            required_length=None):
        try:
            self.base_validators = list(base_validators)
        except TypeError:
            self.base_validators = [base_validators]
        self.item_label = item_label
        if help_string is None:
            self.help_string = "No help available for this option"
        else:
            self.help_string = help_string
        self.required_length = required_length

    def get_base_validator(self, index):
        """Get the validator associated with the given index

        :param int index: The validator index"""
        return self.base_validators[index % len(self.base_validators)]

    def coerce(self, value):
        if self(value):
            return value

        try:
            value = value.strip()
            value = value.strip("[]()")
            all_values = value.split(",")
            return [
                self.get_base_validator(i).coerce(value) for i, value in
                enumerate(all_values)]
        except:
            return value

    @property
    def def_value(self):
        if self.required_length is not None:
            return [
                self.get_base_validator(i).def_value for i in
                range(self.required_length)]
        return []

    def __repr__(self):
        return "{}<{}|{}>".format(
            super().__repr__(), str(*self.base_validators),
            self.required_length
        )

    def __call__(self, iterable):
        for i in range(len(iterable)):
            if not self.get_base_validator(i)(iterable[i]):
                return False
        return True


class SortedListValidator(ListValidator):
    """Check if input is sorted iterable"""

    def __call__(self, iterable):
        for i in range(len(iterable)):
            if not self.get_base_validator(i)(iterable[i]):
                return False
            if i > 0 and iterable[i] > iterable[i - 1]:
                return False
        return True


class DictValidator(Validator):
    """Used to validate an option which takes a dictionary of values

    :param Validator key_validator: A validator used to validate the keys of
    the dictionary
    :param Validator value_validator: A validator used to validate the values
    of the dictionary"""

    def get_base_validator(self, key):
        """Return validator for dictionary values"""
        return self.value_validator

    def __init__(
            self, key_validator, value_validator, help_string=None):
        self.key_validator = key_validator
        self.value_validator = value_validator
        if help_string is None:
            self.help_string = "No help available for this option"
        else:
            self.help_string = help_string

    @property
    def def_value(self):
        return {}

    def __repr__(self):
        return "{}<{}, {}>".format(
            super().__repr__(), self.key_validator, self.value_validator)

    def __call__(self, dictionary):
        for key, value in dictionary.items():
            if (
                    not self.key_validator(key) or
                    not self.value_validator(value)):
                return False
        return True


class ReferenceValidator(Validator):
    """OptionValidator populated with options specified in a W3DProject

    For example, this validator could be used to select from the objects in a
    particular project
    :param Validator fallback_validator: A fallback validator used in case
    project has not been set for this validator
    :param list reference_path: A list of specifiers used to construct a
    ProjectPath pointing to the element used to populate available options
    """

    def __init__(
            self, fallback_validator, reference_path, project=None,
            help_string=None):
        if help_string is None:
            self.help_string = "No help available for this option"
        else:
            self.help_string = help_string
        self.fallback_validator = fallback_validator
        self.def_value = self.fallback_validator.def_value
        self.ref_path = ProjectPath(project=project, path=reference_path)

    def __repr__(self):
        return "{}<{}, {}>".format(
            super().__repr__(), self.ref_path, self.fallback_validator)

    def __call__(self, value):
        if self.ref_path.project is None:
            LOGGER.info("Cannot check relative reference to {}".format(
                value))
            return self.fallback_validator(value)
        return value in self.valid_options

    def coerce(self, value):
        try:
            if value in self.valid_options:
                return value
            else:
                return self.valid_options[
                    self.valid_menu_items.index(value)]
        except UnsetValueError:
            LOGGER.debug("Cannot check relative reference to {}".format(
                value))
            return self.fallback_validator.coerce(value)

    def set_project(self, project):
        """Set project to given value"""
        self.ref_path.project = project

    @property
    def valid_menu_items(self):
        menu = []
        project_element = self.path.get_element()
        for option in self.valid_options:
            try:
                menu.append(project_element[option]["name"])
            except KeyError:
                menu.append(str(project_element[option]))

    @property
    def valid_options(self):
        _valid_options = []
        for option in self.ref_path.get_element():
            if option not in _valid_options:
                _valid_options.append(option)
        _valid_options.sort()
        return _valid_options


class IsBoolean(OptionValidator):
    """Callable object that returns true if value is valid Boolean

    Since all Python objects can be evaluated as a Boolean, this always
    returns true. Included to provide convenient methods for inputting Boolean
    options"""

    def __init__(self):
        super(IsBoolean, self).__init__(True, False)
        self.def_value = True

    def __repr__(self):
        return "{}()".format(self.__class__.__name__)

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
                (self.help_string, "and >= {}".format(
                    self.min_value)))
            self.def_value = self.min_value
        else:
            self.def_value = 0
        if self.max_value is not None:
            self.help_string = " ".join(
                (self.help_string, "and <= {}".format(
                    self.max_value)))
            if self.def_value > self.max_value:
                self.def_value = self.max_value

    def __repr__(self):
        return "{}<{}, {}>".format(
            super().__repr__(), self.min_value, self.max_value)

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


class IsInteger(IsNumeric):
    """Check if value is an integer"""

    def __call__(self, value):
        if not super(IsInteger, self).__call__(value):
            return False
        return value == int(value)


class FeatureValidator(Validator):
    """Check if value is a W3DFeature of specified type"""

    def __init__(self, correct_class, help_string=None):
        self.correct_class = correct_class
        if help_string is None:
            self.help_string = "Value must be of type {}".format(
                self.correct_class)
        else:
            self.help_string = help_string

    def __repr__(self):
        return "{}<{}>".format(
            super().__repr__(), self.correct_class.__name__)

    def __call__(self, value):
        return isinstance(value, self.correct_class)

    def coerce(self, value):
        return self.correct_class(**value)

    @property
    def def_value(self):
        return self.correct_class()
