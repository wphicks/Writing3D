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

"""Convenience tools for working with W3D xml"""
import re
from .errors import BadW3DXML


def text2tuple(text, evaluator=str):
    """Take a string of the format 1,2, 3,... or (1,2, 3,...) or [1,2, 3,...]
    and return equivalent tuple

    :param func evaluator A function used to evaluate each element within the
    sequence. For instance "float" could be used to read in a tuple of floats.
    Default is "str", yielding a tuple of strings.
    """
    sep_regex = re.compile(r',\s*')
    text = text.strip()
    text = text.strip("[()]")
    data = sep_regex.split(text)
    return tuple([evaluator(datum) for datum in data])


def attrib2bool(root, attrib_name, default=None):
    """Take an xml node and try to evaluate given attribute as true/false

    :param xml.etree.ElementTree.Element root: xml node with given attribute
    :param str attrib_name: Attribute to be evaluated
    :param bool default: Value to be returned if attribute is not found.
    :raises BadW3DXML: if default is not set and attribute is not found or if
    attribute does not have value "true" or "false"
    :raises AttributeError: if root is not a valid ElementTree Element
    """
    attrib_value = root.attrib.get(attrib_name, None)
    if attrib_value is None:
        if default is None:
            raise BadW3DXML("Attribute {} is required for node {}".format(
                attrib_name, root.tag))
        return default
    attrib_value = attrib_value.strip()
    if attrib_value not in ("true", "false"):
        raise BadW3DXML(
            'Attribute {} in node {} must be one of "true", "false"'.format(
                attrib_name, root.tag))
    if attrib_value == "true":
        return True
    return False


def text2bool(text):
    """Take string of the form "true" or "false" and return boolean"""
    text = text.strip()
    if text == "true":
        return True
    if text == "false":
        return False
    raise BadW3DXML("Boolean value not set to true or false")


def bool2text(boolean):
    """Take boolean and return string of the form "true" or "false"
    """
    return str(bool(boolean)).lower()


def find_xml_text(root, search):
    """Find "search" node and return its text content or else None
    """
    search_root = root.find(search)
    try:
        return search_root.text
    except AttributeError:
        return None
