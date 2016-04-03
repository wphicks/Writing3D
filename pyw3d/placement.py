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

"""Tools for working with placement of objects within W3D"""
import xml.etree.ElementTree as ET
import math
from .features import W3DFeature
from .validators import OptionValidator, ListValidator, IsNumeric, \
    FeatureValidator
from .errors import BadW3DXML, ConsistencyError
from .xml_tools import text2tuple
import warnings
try:
    import bpy
    import mathutils
except ImportError:
    warnings.warn(
        "Module bpy not found. Loading pyw3d.objects as standalone")


def convert_to_blender_axes(vector):
    """Convert from legacy axis orientation and scale to Blender

    In Blender, positive z-axis points up"""
    if vector is None:
        return None
    return list((vector[0]*0.3048, -vector[2]*0.3048, vector[1]*0.3048))


def convert_to_legacy_axes(vector):
    """Convert from Blender axis orientation and scale to legacy

    In Blender, positive z-axis points up"""
    if vector is None:
        return None
    return list((vector[0]/0.3048, vector[2]/0.3048, -vector[1]/0.3048))


def matrix_from_look(look_direction, up_direction=None):
    """Create rotation_matrix from look-at direction"""
    if up_direction is None:  # Gracefully handle no mathutils module
        up_direction = mathutils.Vector((0, 1, 0))
    rotation_matrix = mathutils.Matrix.Rotation(0, 4, (0, 0, 1))
    frame_y = look_direction
    frame_x = frame_y.cross(up_direction)
    frame_z = frame_x.cross(frame_y)
    rotation_matrix = mathutils.Matrix().to_3x3()
    rotation_matrix.col[0] = frame_x
    rotation_matrix.col[1] = frame_y
    rotation_matrix.col[2] = frame_z
    return rotation_matrix


class W3DRotation(W3DFeature):
    """Stores data on rotation of objects within W3D"""
    ui_order = [
        "rotation_mode", "rotation_vector", "up_vector", "rotation_angle"]
    argument_validators = {
        "rotation_mode": OptionValidator(
            "None", "Axis", "LookAt", "Normal"),
        "rotation_vector": ListValidator(IsNumeric(), required_length=3),
        "up_vector": ListValidator(IsNumeric(), required_length=3),
        "rotation_angle": IsNumeric()}
    default_arguments = {
        "rotation_mode": "None",
        "rotation_vector": None,
        "up_vector": convert_to_blender_axes((0, 1, 0)),
        "rotation_angle": 0}

    def toXML(self, parent_root):
        if not self.is_default("rotation_mode"):
            rot_root = ET.SubElement(parent_root, self["rotation_mode"])
            if self["rotation_vector"] is not None:
                if self["rotation_mode"] == "LookAt":
                    vec_attrib = "target"
                else:
                    vec_attrib = "rotation"
                rot_root.attrib[vec_attrib] = str(tuple(convert_to_legacy_axes(
                    self["rotation_vector"])))
            rot_root.attrib["angle"] = str(self["rotation_angle"])
            return rot_root
        elif not (self.is_default("rotation_vector") and
                  self.is_default("rotation_angle")):
            raise BadW3DXML(
                "Attempting to set rotation vector or angle without setting"
                " rotation mode")

    @classmethod
    def fromXML(rot_class, rot_root):
        rotation = rot_class()
        rotation["rotation_mode"] = rot_root.tag
        try:
            rotation_vector = rot_root.attrib["rotation"]
            rotation["rotation_vector"] = convert_to_blender_axes(
                text2tuple(rotation_vector, evaluator=float))
        except KeyError:
            try:
                rotation_vector = rot_root.attrib["target"]
                rotation["rotation_vector"] = convert_to_blender_axes(
                    text2tuple(rotation_vector, evaluator=float))
            except KeyError:  # No rotation vector specified
                pass
        try:
            rotation_angle = rot_root.attrib["angle"]
            try:
                rotation["rotation_angle"] = float(rotation_angle)
            except TypeError:
                raise BadW3DXML("Rotation angle must be specified as a float")
        except KeyError:  # No rotation vector specified
            pass
        return rotation

    def get_rotation_matrix(self, blender_object):
        rotation_matrix = mathutils.Matrix.Rotation(0, 4, (0, 0, 1))
        if self["rotation_mode"] == "Axis":
            rotation_matrix = mathutils.Matrix.Rotation(
                math.radians(self["rotation_angle"]),
                4,  # Size of rotation matrix (4x4)
                self["rotation_vector"]
            )
        elif self["rotation_mode"] == "LookAt":
            if self["rotation_vector"] is None:
                raise ConsistencyError(
                    "LookAt rotation *must* specify rotation_vector"
                )
            look_direction = (
                blender_object.location -
                mathutils.Vector(self["rotation_vector"])
            ).normalized()

            up_direction = mathutils.Vector(self["up_vector"]).normalized()
            rotation_matrix = matrix_from_look(look_direction, up_direction)

        elif self["rotation_mode"] == "Normal":
            current_normal = mathutils.Vector((1, 0, 0))
            current_normal.rotate(blender_object.rotation_euler)
            # NOTE: Not absolutely sure that the above is sufficient to deal
            # with previously rotated objects, but the behavior here is a
            # little ambiguous anyway
            difference = mathutils.Vector(
                self["rotation_vector"]).rotation_difference(current_normal)
            rotation_matrix = difference.to_matrix()

        return rotation_matrix

    def rotate(self, blender_object):
        """Rotate Blender object to specified orientation
        """
        blender_object.rotation_euler.rotate(self.get_rotation_matrix(
            blender_object))
        return blender_object


class W3DPlacement(W3DFeature):
    """Stores data on placement of objects within W3D

    Specifies both position and rotation of W3D objects
    :param str relative_to: Position specified relative to what? One of Center,
    FloorWall, LeftWall, RightWall or FloorWall
    :param tuple position: Tuple of three numbers specifying x, y, z position
    :param py:class:W3DRotation rotation: py:class:W3DRotation object
    specifying rotation
    """
    ui_order = ["position", "relative_to", "rotation"]
    argument_validators = {
        "relative_to": OptionValidator(
            "Center", "FrontWall", "LeftWall", "RightWall", "FloorWall"),
        "position": ListValidator(
            IsNumeric(), required_length=3),
        "rotation": FeatureValidator(W3DRotation)}
    default_arguments = {
        "relative_to": "Center",
        "position": (0, 0, 0),
        }
    relative_to_objects = {}
    """Dictionary mapping names of relative_to options to Blender
    representations

    In default W3DWriting, these are simply the four walls, but this can be
    overridden to provide additional functionality"""

    def __init__(self, *args, **kwargs):
        super(W3DPlacement, self).__init__(*args, **kwargs)
        if "rotation" not in self:
            self["rotation"] = W3DRotation()

    def toXML(self, parent_root):
        place_root = ET.SubElement(parent_root, "Placement")
        rel_root = ET.SubElement(place_root, "RelativeTo")
        rel_root.text = self["relative_to"]
        if not self.is_default("position"):
            pos_root = ET.SubElement(place_root, "Position")
            pos_root.text = str(tuple(
                convert_to_legacy_axes(self["position"])))
        if not self.is_default("rotation"):
            self["rotation"].toXML(place_root)
        return place_root

    @classmethod
    def fromXML(place_class, place_root):
        placement = place_class()
        rel_root = place_root.find("RelativeTo")
        if rel_root is not None:
            placement["relative_to"] = rel_root.text.strip()
        pos_root = place_root.find("Position")
        if pos_root is not None:
            placement["position"] = convert_to_blender_axes(
                text2tuple(pos_root.text.strip(), evaluator=float))
        for rotation_mode in ["Axis", "LookAt", "Normal"]:
            rot_root = place_root.find(rotation_mode)
            if rot_root is not None:
                placement["rotation"] = W3DRotation.fromXML(rot_root)
                return placement
        return placement

    #TODO: Deal with non-standard wall placements
    def _create_relative_to_objects(
            self,
            wall_positions={
                "FrontWall": convert_to_blender_axes((0, 0, -4)),
                "LeftWall": convert_to_blender_axes((-4, 0, 0)),
                "RightWall": convert_to_blender_axes((4, 0, 0)),
                "FloorWall": convert_to_blender_axes((0, 0, -4))},
            wall_rotations={
                "FrontWall": (0, 0, 0),
                "LeftWall": (0, 0, math.pi/2),
                "RightWall": (0, 0, -math.pi/2),
                "FloorWall": (-math.pi/2, 0, 0)}
            ):
        """Create Blender objects corresponding to relative_to options if
        necessary"""
        if len(self.relative_to_objects) != len(
                self.argument_validators["relative_to"].valid_options) - 1:
            for wall_name, position in wall_positions.items():
                bpy.ops.object.add(
                    type="EMPTY",
                    location=position,
                    rotation=wall_rotations[wall_name],
                    layers=[layer == 3 for layer in range(1, 21)]
                )
                self.relative_to_objects[wall_name] = bpy.context.object
                self.relative_to_objects[wall_name].name = wall_name

        return self.relative_to_objects

    def place(self, blender_object):
        """Place Blender object in specified position and orientation
        """
        self._create_relative_to_objects()
        if self["relative_to"] != "Center":
            blender_object.parent = self.relative_to_objects[
                self["relative_to"]]
        blender_object.layers = [layer == 1 for layer in range(1, 21)]

        blender_object.location = self["position"]
        self["rotation"].rotate(blender_object)
        return blender_object
