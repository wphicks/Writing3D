"""Tools for validating options provided to Cave features"""
# TODO: convert to universal help and help strings


class OptionListValidator(object):
    """Callable object that returns true if value is in given list"""

    def __init__(self, *valid_options):
        self.valid_options = set(valid_options)

    def __call__(self, value):
        return value in self.valid_options

    def help(self):
        return "Value must be one of " + " ,".join(self.valid_options)


class IsNumeric(object):
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

    def help(self):
        return self.help_string


class IsNumericIterable(object):
    """Callable object that returns true if value is a numeric iterable

    :param required_length: Optionally sets required length for iterable. If
    this attribute is set to None, length is not checked."""

    def __init__(self, required_length=None):
        self.required_length = required_length

    def __call__(self, iterable):
        try:
            for value in iterable:
                if not IsNumeric(value):
                    return False  # Non-numeric
            return (self.required_length is None or len(iterable) ==
                    self.required_length)
        except TypeError:
            return False  # Non-iterable

    def help(self):
        if self.required_length is not None:
            return "Value must be a sequence of {} numeric values".format(
                self.required_length)
        return "Value must be a sequence of numeric values"


class CheckType(object):
    """Check if type of object matches one of specified types"""

    def __init__(self, *correct_types):
        self.correct_types = correct_types

    def __call__(self, value):
        raise NotImplementedError
        for type_ in self.correct_types:
            if isinstance(type_, value):
                return True
        return False

    def help(self):
        return "Value must be one of {}".format(str(self.correct_types)[1:-2])


class AlwaysValid(object):
    """Always returns True"""

    def __init__(self,
                 help_string="All Python objects are valid for this option"):
        self.help_string = help_string

    def __call__(self, value):
        return True

    def help(self):
        return self.help_string
