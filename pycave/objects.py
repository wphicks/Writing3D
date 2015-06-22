"""Tools for working with displayable objects in Cave projects
"""
from features import CaveFeature
from validators import OptionListValidator, IsNumeric,  AlwaysValid,\
    IsNumericIterable


class CaveLink(CaveFeature):
    """Store data on a clickable link

    :param bool enabled: Is link enabled?
    :param bool remain_enabled: Should link remain enabled after activation?
    :param tuple enabled_color: RGB color when link is enabled
    :param tuple selected_color: RGB color when link is selected
    :param actions: Dictionary mapping number of clicks to CaveActions
    :param int reset: Number of clicks after which to reset link (negative
    value to never reset)"""

    argument_validators = {
        "enabled": AlwaysValid(help_string="Either true or false"),
        "remain_enabled": AlwaysValid(help_string="Either true or false"),
        "enabled_color": IsNumericIterable(required_length=3),
        "selected_color": IsNumericIterable(required_length=3),
        "actions": AlwaysValid(
            help_string="Must be a dictionary mapping integers to CaveActions"
            ),
        "reset": IsNumeric()
        }

    default_arguments = {
        "enabled": True,
        "remain_enabled": True,
        "enabled_color": (0, 128, 255),
        "selected_color": (255, 0, 0),
        "actions": {},
        "reset": -1
        }

    def __init__(self, *args, **kwargs):
        super(CaveLink, self).__init__(*args, **kwargs)
        self.num_clicks = 0

    def toXML(self, object_root):
        """Store CaveLink as LinkRoot node within Object node

        :param :py:class:xml.etree.ElementTree.Element object_root
        """
        CaveFeature.toXML(self, object_root)  # TODO: Replace this

    @classmethod
    def fromXML(link_root):
        """Create CaveLink from LinkRoot node

        :param :py:class:xml.etree.ElementTree.Element object_root
        """
        return CaveFeature.fromXML(link_root)  # TODO: Replace this


class CaveObject(CaveFeature):
    """Store data on single Cave object

    :param str name: The name of the object
    :param CavePlacement placement: Position and orientation of object
    :param CaveLink link: Clickable link for object
    :param tuple color: Three floats representing RGB color of object
    :param bool visible: Is object visible?
    :param bool lighting: Does object respond to scene lighting?
    :param float scale: Scaling factor for size of object
    :param bool click_through: Should clicks also pass through object?
    :param bool around_own_axis: TODO clarify
    :param str sound: Name of sound element associated with this object
    :param content: Content of object; one of CaveText, CaveImage,
    CaveStereoImage, CaveModel, CaveLight, CavePSys
    """
    # TODO: Far more sensible to have Text, Image, etc. subclass this and add
    # to the argument dictionaries. toXML and fromXML could even be decorators
    # which take care of the "Object" node packaging

    argument_validators = {
        "name": AlwaysValid(
            help_string="Unique name for this object"),
        "placement": AlwaysValid(
            help_string="CavePlacement specifying position and orientation"),
        "link": AlwaysValid(
            help_string="CaveLink associated with object"),
        "color": IsNumericIterable(required_length=3),
        "visible": AlwaysValid("Either true or false"),
        "lighting": AlwaysValid("Either true or false"),
        "scale": IsNumeric(min_value=0),
        "click_through": AlwaysValid("Either true or false"),
        "around_own_axis": AlwaysValid("Either true or false"),
        "sound": AlwaysValid("Name of sound attached to this object"),
        "content": AlwaysValid("Content of object")}

    default_arguments = {
        "link": None,
        "color": (255, 255, 255),
        "visible": True,
        "lighting": False,
        "scale": 1,
        "click_through": False,
        "around_own_axis": False,
        "sound": None
        }

    def toXML(self, all_objects_root):
        """Store CaveObject as Object node within ObjectRoot node

        :param :py:class:xml.etree.ElementTree.Element all_objects_root
        """
        CaveFeature.toXML(self, all_objects_root)  # TODO: Replace this

    @classmethod
    def fromXML(object_root):
        """Create CaveObject from Object node

        :param :py:class:xml.etree.ElementTree.Element object_root
        """
        return CaveFeature.fromXML(object_root)  # TODO: Replace this

    def blend(self):
        """Create representation of CaveObject in Blender"""
        raise NotImplementedError  # TODO


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

    def toXML(self, object_root):
        """Store CaveText as Content node within Object node

        :param :py:class:xml.etree.ElementTree.Element object_root
        """
        CaveFeature.toXML(self, object_root)  # TODO: Replace this

    @classmethod
    def fromXML(content_root):
        """Create CaveText object from Content node

        :param :py:class:xml.etree.ElementTree.Element content_root
        """
        return CaveFeature.fromXML(content_root)  # TODO: Replace this

    def blend(self):
        """Create representation of CaveText in Blender"""
        raise NotImplementedError  # TODO


class CaveImage(CaveFeature):
    """Represent a flat image in the Cave

    :param str filename: Filename of image to be displayed"""
    argument_validators = {
        "filename": AlwaysValid("Value should be a string")}

    def toXML(self, object_root):
        """Store CaveImage as Content node within Object node

        :param :py:class:xml.etree.ElementTree.Element object_root
        """
        CaveFeature.toXML(self, object_root)  # TODO: Replace this

    @classmethod
    def fromXML(content_root):
        """Create CaveImage object from Content node

        :param :py:class:xml.etree.ElementTree.Element content_root
        """
        return CaveFeature.fromXML(content_root)  # TODO: Replace this

    def blend(self):
        """Create representation of CaveImage in Blender"""
        raise NotImplementedError  # TODO


class CaveStereoImage(CaveFeature):
    """Represents different images in left and right eye

    :param str left-file: Filename of image to be displayed to left eye
    :param str right-file: Filename of image to be displayed to right eye
    """
    argument_validators = {
        "left_file": AlwaysValid("Value should be a string"),
        "right_file": AlwaysValid("Value should be a string")}

    def toXML(self, object_root):
        """Store CaveStereoImage as Content node within Object node

        :param :py:class:xml.etree.ElementTree.Element object_root
        """
        CaveFeature.toXML(self, object_root)  # TODO: Replace this

    @classmethod
    def fromXML(content_root):
        """Create CaveStereoImage object from Content node

        :param :py:class:xml.etree.ElementTree.Element content_root
        """
        return CaveFeature.fromXML(content_root)  # TODO: Replace this

    def blend(self):
        """Create representation of CaveStereoImage in Blender"""
        raise NotImplementedError  # TODO


class CaveModel(CaveFeature):
    """Represents a 3d model in the Cave

    :param str filename: Filename of model to be displayed
    :param bool check_collisions: TODO Clarify what this does
    """
    argument_validators = {
        "filename": AlwaysValid("Value should be a string"),
        "check_collisions": AlwaysValid("Value should be a boolean")}

    def toXML(self, object_root):
        """Store CaveModel as Content node within Object node

        :param :py:class:xml.etree.ElementTree.Element object_root
        """
        CaveFeature.toXML(self, object_root)  # TODO: Replace this

    @classmethod
    def fromXML(content_root):
        """Create CaveModel object from Content node

        :param :py:class:xml.etree.ElementTree.Element content_root
        """
        return CaveFeature.fromXML(content_root)  # TODO: Replace this

    def blend(self):
        """Create representation of CaveModel in Blender"""
        raise NotImplementedError  # TODO


class CaveLight(CaveFeature):
    """Represents a light source in the Cave

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
        "attenuation": IsNumericIterable(3),
        "angle": IsNumeric()}
    default_arguments = {
        "diffuse": True,
        "specular": True,
        "attenuation": (1.0, 0.0, 0.0),
        "angle": 30.0}

    def toXML(self, object_root):
        """Store CaveLight as Content node within Object node

        :param :py:class:xml.etree.ElementTree.Element object_root
        """
        CaveFeature.toXML(self, object_root)  # TODO: Replace this

    @classmethod
    def fromXML(content_root):
        """Create CaveLight object from Content node

        :param :py:class:xml.etree.ElementTree.Element content_root
        """
        return CaveFeature.fromXML(content_root)  # TODO: Replace this

    def blend(self):
        """Create representation of CaveLight in Blender"""
        raise NotImplementedError  # TODO


class CavePSys(CaveFeature):
    """Represents a particle system in the Cave

    NOT YET IMPLEMENTED AT ALL"""
    # TODO: everything
