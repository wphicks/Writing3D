"""Convenience tools for working with Cave xml"""
import re
from errors import BadCaveXML, BadXMLChain
import xml.etree.ElementTree as ET


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


def text2bool(text):
    """Take string of the form "true" or "false" and return boolean"""
    text = text.strip()
    if text == "true":
        return True
    if text == "false":
        return False
    raise BadCaveXML("Boolean value not set to true or false")


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


class XMLChain(object):
    """Find features in an XML tree or add them to a tree

    :param list chain: A list of two-element tuples specifying where to find
    the relevant feature. E.g.: [("node", "Parent_Node_Name"), ("node",
        "Child_Node_Name"), ("attribute", "Child_Attribute_Name")] Acceptable
        tags for the first element in these tuples are "node", "attribute", and
        "text" for finding XML nodes, attributes of those nodes, and text
        within those node respectively. Note that "attribute" and "text" should
        only appear in the last element of the chain.
    :param evaluator: An function used to process the last element in the
    chain.  E.g. float might be used to convert a numeric attribute to a Python
    float rather than a string.
    :param encoder: A function used to convert a Python object back into a
    string that can be stored in an XML tree. E.g. str might be used to convert
    a float back into a string.
    :param optional: Indicates whether the feature being retrieved MUST be set
    for properly formatted Cave XML
    """

    def __init__(self, chain, evaluator=str, encoder=str, optional=False):
        self._chain = chain
        self.evaluator = evaluator
        self.encoder = encoder
        self.optional = optional

    def _lookahead(self):
        """Convenience iterator used to label last item in chain"""
        chain_iter = iter(self._chain)
        last_item = chain_iter.next()
        for link in self._chain:
            yield last_item[0], last_item[1], False
            last_item = link
        yield last_item[0], last_item[1], True

    def get(self, node):
        for type_, tag, end_indicator in self.lookahead():
            if type_ == "node":
                node = node.find(tag)
            elif type_ == "attribute":
                if not end_indicator:
                    raise BadXMLChain(
                        "attribute tag must come at end of chain")
                try:
                    return self.evaluator(node.attrib[tag])
                except KeyError:
                    raise BadCaveXML(
                        "Attribute {} not found in node {}".format(
                            tag, node.tag)
                        )
            elif type_ == "text":
                if not end_indicator:
                    raise BadXMLChain(
                        "text tag must come at end of chain")
                return self.evaluator(node.text)
            else:
                raise BadXMLChain(
                    'Unrecognized tag in chain (Must be one of "node",'
                    '"attribute", "text")')
            if node is None and not end_indicator:
                raise BadCaveXML(
                    "Node {} not found where expected".format(tag)
                    )

    def put(self, node, value):
        for type_, tag, end_indicator in self.lookahead():
            if type_ == "node":
                next_node = node.find(tag)
                if next_node is None:
                    next_node = ET.SubElement(node, tag)
                node = next_node
            elif type_ == "attribute":
                if not end_indicator:
                    raise BadXMLChain(
                        "attribute tag must come at end of chain")
                node.attrib[tag] = self.encoder(value)
            elif type_ == "text":
                if not end_indicator:
                    raise BadXMLChain(
                        "text tag must come at end of chain")
                node.text = self.encoder(value)
            else:
                raise BadXMLChain(
                    'Unrecognized tag in chain (Must be one of "node",'
                    '"attribute", "text")')
        return node
