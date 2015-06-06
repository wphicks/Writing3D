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
