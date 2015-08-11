"""Tools for working with placement of objects within Cave"""
import xml.etree.ElementTree as ET
import math
from .features import CaveFeature
from .validators import OptionListValidator, IsNumericIterable, IsNumeric, \
    AlwaysValid
from .errors import BadCaveXML
from .xml_tools import text2tuple
import warnings
try:
    import bpy
    import mathutils
except ImportError:
    warnings.warn(
        "Module bpy not found. Loading pycave.objects as standalone")


def convert_to_blender_axes(vector):
    """Convert from legacy axis orientation and scale to Blender

    In Blender, positive z-axis points up"""
    return tuple((vector[0]*0.3048, -vector[2]*0.3048, vector[1]*0.3048))


def convert_to_legacy_axes(vector):
    """Convert from Blender axis orientation and scale to legacy

    In Blender, positive z-axis points up"""
    return tuple((vector[0]/0.3048, vector[2]/0.3048, -vector[1]/0.3048))


class CaveRotation(CaveFeature):
    """Stores data on rotation of objects within Cave"""
    argument_validators = {
        "rotation_mode": OptionListValidator(
            "None", "Axis", "LookAt", "Normal"),
        "rotation_vector": IsNumericIterable(3),
        "up_vector": IsNumericIterable(3),
        "rotation_angle": IsNumeric()}
    default_arguments = {
        "rotation_mode": "None",
        "rotation_vector": None,
        "up_vector": convert_to_blender_axes((0, 1, 0)),
        "rotation_angle": 0.0}

    def toXML(self, parent_root):
        if not self.is_default("rotation_mode"):
            rot_root = ET.SubElement(parent_root, self["rotation_mode"])
            rot_root.attrib["rotation"] = str(tuple(self["rotation_vector"]))
            rot_root.attrib["angle"] = str(self["rotation_angle"])
        elif not (self.is_default("rotation_vector") and
                  self.is_default("rotation_angle")):
            raise BadCaveXML(
                "Attempting to set rotation vector or angle without setting"
                " rotation mode")

    @classmethod
    def fromXML(rot_class, rot_root):
        rotation = rot_class()
        rotation["rotation_mode"] = rot_root.tag
        try:
            rotation_vector = rot_root.attrib["rotation"]
            rotation["rotation_vector"] = convert_to_blender_axes(
                text2tuple(rotation_vector))
        except KeyError:  # No rotation vector specified
            pass
        try:
            rotation_angle = rot_root.attrib["angle"]
            try:
                rotation["rotation_angle"] = float(rotation_angle)
            except TypeError:
                raise BadCaveXML("Rotation angle must be specified as a float")
        except KeyError:  # No rotation vector specified
            pass

    def get_rotation_matrix(self, blender_object):
        rotation_matrix = mathutils.Matrix.Rotation(0, 4, (0, 0, 1))
        if self["rotation_mode"] == "Axis":
            rotation_matrix = mathutils.Matrix.Rotation(
                math.radians(self["rotation_angle"]),
                4,  # Size of rotation matrix (4x4)
                self["rotation_vector"]
            )
        elif self["rotation_mode"] == "LookAt":
            look_direction = (
                blender_object.location -
                mathutils.Vector(self["rotation_vector"])
            ).normalized()

            up_direction = mathutils.Vector(self["up_vector"]).normalized()

            frame_y = look_direction
            frame_x = frame_y.cross(up_direction)
            frame_z = frame_x.cross(frame_y)
            rotation_matrix = mathutils.Matrix().to_3x3()
            rotation_matrix.col[0] = frame_x
            rotation_matrix.col[1] = frame_y
            rotation_matrix.col[2] = frame_z
        elif self["rotation_mode"] == "Normal":
            # direction = mathutils.Vector(self["rotation_vector"])
            pass
        return rotation_matrix

    def rotate(self, blender_object):
        """Rotate Blender object to specified orientation
        """
        blender_object.rotation_euler.rotate(self.get_rotation_matrix(
            blender_object))
        return blender_object


class CavePlacement(CaveFeature):
    """Stores data on placement of objects within Cave

    Specifies both position and rotation of Cave objects
    :param str relative_to: Position specified relative to what? One of Center,
    FloorWall, LeftWall, RightWall or FloorWall
    :param tuple position: Tuple of three numbers specifying x, y, z position
    :param py:class:CaveRotation rotation: py:class:CaveRotation object
    specifying rotation
    """
    argument_validators = {
        "relative_to": OptionListValidator(
            "Center", "FrontWall", "LeftWall", "RightWall", "FloorWall"),
        "position": IsNumericIterable(3),
        "rotation": AlwaysValid("A CaveRotation")}
    default_arguments = {
        "relative_to": "Center",
        "position": (0, 0, 0),
        "rotation": CaveRotation()}
    relative_to_objects = {}
    """Dictionary mapping names of relative_to options to Blender
    representations

    In default CaveWriting, these are simply the four walls, but this can be
    overridden to provide additional functionality"""

    def toXML(self, parent_root):
        place_root = ET.SubElement(parent_root, "Placement")
        if not self.is_default("relative_to"):
            rel_root = ET.SubElement(place_root, "RelativeTo")
            rel_root.text = self["relative_to"]
        if not self.is_default("position"):
            pos_root = ET.SubElement(place_root, "Position")
            pos_root.text = str(tuple(self["position"]))
        if not self.is_default("rotation"):
            self["rotation"].toXML(place_root)

    @classmethod
    def fromXML(place_class, place_root):
        placement = place_class()
        rel_root = place_root.find("RelativeTo")
        if rel_root is not None:
            placement["relative_to"] = rel_root.text.strip()
        pos_root = place_root.find("Position")
        if pos_root is not None:
            placement["position"] = convert_to_legacy_axes(
                text2tuple(pos_root.text.strip()))
        for rotation_mode in ["Axis", "LookAt", "Normal"]:
            rot_root = place_root.find(rotation_mode)
            if rot_root is not None:
                placement["rotation"] = CaveRotation.fromXML(rot_root)
                return placement
        return placement

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
