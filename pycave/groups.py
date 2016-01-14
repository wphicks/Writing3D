import warnings
import xml.etree.ElementTree as ET
from .features import CaveFeature
from .validators import AlwaysValid
from .errors import BadCaveXML, ConsistencyError
from .names import generate_group_name, \
    generate_blender_object_name
try:
    import bpy
except ImportError:
    warnings.warn(
        "Module bpy not found. Loading pycave.actions as standalone")


class CaveGroup(CaveFeature):
    """Organize CaveObjects (or other CaveGroups) into groups

    :param str name: Name of this group
    :param list objects: List of names of objects in this group
    :param list groups: List of names of groups in this group
    """

    argument_validators = {
        "name": AlwaysValid(help_string="Name of this group"),
        "objects": AlwaysValid(help_string="A list of names of objects"),
        "groups": AlwaysValid(help_string="A list of names of groups"),
    }

    default_arguments = {
    }

    def __init__(self, *args, **kwargs):
        super(CaveGroup, self).__init__(*args, **kwargs)
        #TODO: It should be possible to initialize with values
        if "objects" not in self:
            self["objects"] = []
        if "groups" not in self:
            self["groups"] = []

    def toXML(self, group_root):
        """Store CaveGroup as Group node within GroupRoot node)

        :param :py:class:xml.etree.ElementTree.Element object_root
        """
        try:
            group_node = ET.SubElement(
                group_root, "Group", attrib={"name": self["name"]})
        except KeyError:
            raise ConsistencyError("CaveGroup must have name attribute set")
        for object_name in self["objects"]:
            ET.SubElement(
                group_node, "Objects", attrib={"name": object_name})
        for group_name in self["groups"]:
            ET.SubElement(
                group_node, "Groups", attrib={"name": group_name})

    @classmethod
    def fromXML(group_class, group_node):
        group = group_class()
        try:
            group["name"] = group_node.attrib["name"]
        except KeyError:
            raise BadCaveXML("Group node has no name attrib")
        for child in group_node.getchildren():
            if child.tag == "Objects":
                try:
                    group["objects"].append(child.attrib["name"])
                except KeyError:
                    raise BadCaveXML("Objects node has no name attrib")
            if child.tag == "Groups":
                try:
                    group["groups"].append(child.attrib["name"])
                except KeyError:
                    raise BadCaveXML("Groups node has no name attrib")
        return group

    def blend_objects(self):
        """Store data on objects in group in Blender script"""
        group_name = generate_group_name(self["name"])
        script = bpy.data.texts["group_defs.py"]
        object_names = [
            generate_blender_object_name(object_) for object_ in
            self["objects"]
        ]
        script.write("\n{} = {}".format(
            group_name, object_names))
        return script

    def blend_groups(self):
        """Store data on groups in group in Blender script"""
        group_name = generate_group_name(self["name"])
        script = bpy.data.texts["group_defs.py"]
        script_text = [""]
        for group in self["groups"]:
            script_text.append(
                "{}.extend({})".format(
                    group_name, generate_group_name(group))
            )
        script.write("\n".join(script_text))
