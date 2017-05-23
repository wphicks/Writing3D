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

import logging
import xml.etree.ElementTree as ET
from .features import W3DFeature
from .validators import ValidPyString, ListValidator, ReferenceValidator
from .errors import BadW3DXML, ConsistencyError
from .names import generate_group_name, \
    generate_blender_object_name
try:
    import bpy
except ImportError:
    logging.debug(
        "Module bpy not found. Loading pyw3d.actions as standalone")


class W3DGroup(W3DFeature):
    """Organize W3DObjects (or other W3DGroups) into groups

    :param str name: Name of this group
    :param list objects: List of names of objects in this group
    :param list groups: List of names of groups in this group
    """

    argument_validators = {
        "name": ValidPyString(),
        "objects": ListValidator(
            ReferenceValidator(
                ValidPyString(),
                ["objects"],
                help_string="Must be the name of an object"),
            item_label="Object",
            help_string="A list of names of objects"),
        "groups": ListValidator(
            ReferenceValidator(
                ValidPyString(),
                ["groups"],
                help_string="Must be the name of a group"),
            item_label="Group",
            help_string="A list of names of groups")
    }

    default_arguments = {
    }

    ui_order = ["name", "objects", "groups"]

    def __init__(self, *args, **kwargs):
        super(W3DGroup, self).__init__(*args, **kwargs)
        #TODO: It should be possible to initialize with values
        if "objects" not in self:
            self["objects"] = []
        if "groups" not in self:
            self["groups"] = []

    def toXML(self, group_root):
        """Store W3DGroup as Group node within GroupRoot node)

        :param :py:class:xml.etree.ElementTree.Element object_root
        """
        try:
            group_node = ET.SubElement(
                group_root, "Group", attrib={"name": self["name"]})
        except KeyError:
            raise ConsistencyError("W3DGroup must have name attribute set")
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
            raise BadW3DXML("Group node has no name attrib")
        for child in group_node.getchildren():
            if child.tag == "Objects":
                try:
                    group["objects"].append(
                        group.argument_validators[
                            "objects"].get_base_validator(0).coerce(
                                child.attrib["name"]
                        )
                    )
                except KeyError:
                    raise BadW3DXML("Objects node has no name attrib")
            if child.tag == "Groups":
                try:
                    group["groups"].append(
                        group.argument_validators[
                            "groups"].get_base_validator(0).coerce(
                                child.attrib["name"]
                        )
                    )
                except KeyError:
                    raise BadW3DXML("Groups node has no name attrib")
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
