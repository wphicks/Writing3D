"""Convenience tools for working with Cave xml"""
import re
from errors import BadCaveXML


def text2tuple(string, evaluator=str):
    """Take a string of the format (1,2, 3,...) and return equivalent tuple

    :param func evaluator A function used to evaluate each element within the
    tuple. For instance "float" could be used to read in a tuple of floats.
    Default is "str", yielding a tuple of strings.
    """
    sep_regex = re.compile(r',\s*')
    string = string.strip()[1:-1]
    data = sep_regex.split(string)
    return tuple([evaluator(datum) for datum in data])


def attrib2bool(root, attrib_name, default=None):
    """Take an xml node and try to evaluate given attribute as true/false

    :param xml.etree.ElementTree.Element root: xml node with given attribute
    :param str attrib_name: Attribute to be evaluated
    :param bool default: Value to be returned if attribute is not found.
    :raises BadCaveXML: if default is not set and attribute is not found or if
    attribute does not have value "true" or "false"
    :raises AttributeError: if root is not a valid ElementTree Element
    """
    attrib_value = root.attrib.get(attrib_name, None)
    if attrib_value is None:
        if default is None:
            raise BadCaveXML("Attribute {} is required for node {}".format(
                attrib_name, root.tag))
        return default
    attrib_value = attrib_value.strip()
    if attrib_value not in ("true", "false"):
        raise BadCaveXML(
            'Attribute {} in node {} must be one of "true", "false"'.format(
                attrib_name, root.tag))
    if attrib_value == "true":
        return True
    return False


def find_xml_text(root, search):
    """Find "search" node and return its text content or else None
    """
    search_root = root.find(search)
    try:
        return search_root.text
    except AttributeError:
        return None
