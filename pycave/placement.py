"""Tools for working with placement of objects within Cave"""
import xml.etree.ElementTree as ET
from features import CaveFeature
from validators import OptionListValidator, IsNumericIterable, IsNumeric, \
    CheckType
from errors import BadCaveXML
from xml_tools import text2tuple


class CaveRotation(CaveFeature):
    """Stores data on rotation of objects within Cave"""
    argument_validators = {
        "rotation_mode": OptionListValidator(
            "None", "Axis", "LookAt", "Normal"),
        "rotation_vector": IsNumericIterable(3),
        "rotation_angle": IsNumeric()}
    default_arguments = {
        "rotation_mode": None,
        "rotation_vector": None,
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
    def fromXML(rot_root):
        rotation = CaveRotation()
        rotation["rotation_mode"] = rot_root.tag
        try:
            rotation_vector = rot_root.attrib["rotation"]
            rotation["rotation_vector"] = text2tuple(rotation_vector)
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
        "rotation": CheckType(CaveRotation)}
    default_arguments = {
        "relative_to": "Center",
        "position": (0, 0, 0),
        "rotation": CaveRotation()}

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
    def fromXML(place_root):
        placement = CavePlacement()
        rel_root = place_root.find("RelativeTo")
        if rel_root is not None:
            placement["relative_to"] = rel_root.text.strip()
        pos_root = place_root.find("Position")
        if pos_root is not None:
            placement["position"] = text2tuple(pos_root.text.strip())
        for rotation_mode in ["Axis", "LookAt", "Normal"]:
            rot_root = place_root.find(rotation_mode)
            if rot_root is not None:
                placement["rotation"] = CaveRotation.fromXML(rot_root)
                return placement
        return placement
