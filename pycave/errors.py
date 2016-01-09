"""Exceptions raised when working with Cave projects"""


class BadCaveXML(Exception):
    """Exception thrown for attempting to use malformed Cave XML"""
    def __init__(self, message):
        super(BadCaveXML, self).__init__(message)


class InvalidArgument(Exception):
    """Exception thrown for invalid argument to a Cave feature

    Examples could include an option not defined in the XML schema or a bad
    value passed for such an option."""
    def __init__(self, message):
        super(InvalidArgument, self).__init__(message)


class ConsistencyError(Exception):
    """Exception thrown for use of a Cave feature with options set incorrectly

    Examples could include not specifying a required attribute or specifying a
    value that does not make sense in the context of the entire project. More
    concretely, if an ObjectAction does not specify what object it is changing,
    a ConsistencyError will be thrown before that action can be written to XML
    or displayed in the Cave."""
    def __init__(self, message):
        super(InvalidArgument, self).__init__(message)


class EBKAC(Exception):
    """Exception thrown when methods are called in a logically nonsensical
    order or given obviously nonsensical input

    E.g. Setting a property on an object before creating that object.
    This error should never be raised for improper input of a value for a Cave
    feature (i.e. in a GUI project creator) but only when someone is using the
    underlying methods of that feature in a dangerous and irrational way.
    """
    def __init__(self, message):
        super(EBKAC, self).__init__(message)
