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
