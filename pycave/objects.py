"""Tools for working with displayable objects in Cave projects
"""
from features import CaveFeature
from validators import OptionListValidator, IsNumeric, CheckType, AlwaysValid


class CaveText(CaveFeature):
    """Represents text in the Cave

    :param str text: String of text to be displayed
    :param str halign: Horizontal alignment of text ("left", "right", "center")
    :param str valign: Vertical alignment of text ("top", "center", "bottom")
    :param str font: Name of font to be used
    :param float depth: Depth to extrude each letter
    """
    argument_validators = {
        "text": AlwaysValid("Value should be a string"),
        "halign": OptionListValidator(
            "left", "right", "center"),
        "valign": OptionListValidator(
            "top", "center", "bottom"),
        "font": AlwaysValid("Value should be a string"),
        "depth": IsNumeric()}

    default_arguments = {
        "halign": "center",
        "valign": "center",
        "font": None,
        "depth": 0.0}


class CaveImage(CaveFeature):
    """Represent a flat image in the Cave

    :param str filename: Filename of image to be displayed"""
    argument_validators = {
        "filename": AlwaysValid("Value should be a string")}


class CaveStereoImage(CaveFeature):
    """Represents different images in left and right eye

    :param str left-file: Filename of image to be displayed to left eye
    :param str right-file: Filename of image to be displayed to right eye
    """
    argument_validators = {
        "left_file": AlwaysValid("Value should be a string"),
        "right_file": AlwaysValid("Value should be a string")}


class CaveModel(CaveFeature):
    """Represents a 3d model in the Cave

    :param str filename: Filename of model to be displayed
    :param bool check_collisions: TODO Clarify what this does
    """
    argument_validators = {
        "filename": AlwaysValid("Value should be a string"),
        "check_collisions": AlwaysValid("Value should be a boolean")}


class CaveLight(CaveFeature):
    """Represents a light souce in the Cave

    :param str light_type: Type of source, one of "Point", "Directional",
    "Spot"
    :param bool diffuse: Provide diffuse light?
    :param bool specular: Provide specular light?
    :param tuple attenuation: Tuple of 3 floats specifying constant, linear,
    and
    quadratic attenuation of light source respectively
    :param float angle: Angle in degrees specifying direction of spot light
    source (TODO Clarify how)
    """
    arguments_list = {
        "light_type": OptionListValidator("Point", "Directional", "Spot"),
        "diffuse": AlwaysValid("Value should be a boolean"),
        "specular": AlwaysValid("Value should be a boolean"),
        "attenuation": IsNumericIterable(3)
        "angle": IsNumeric()}
    default_arguments = {
        "diffuse": True,
        "specular": True,
        "attenuation": (1.0, 0.0, 0.0),
        "angle": 30.0}
