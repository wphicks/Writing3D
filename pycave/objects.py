"""Tools for working with displayable objects in Cave projects
"""
import os
import xml.etree.ElementTree as ET
from collections import defaultdict
import math
from .errors import BadCaveXML, InvalidArgument
from .xml_tools import find_xml_text, text2bool, text2tuple, bool2text
from .features import CaveFeature
from .actions import CaveAction
from .placement import CavePlacement
from .validators import OptionListValidator, IsNumeric,  AlwaysValid,\
    IsNumericIterable
import warnings
try:
    import bpy
except ImportError:
    warnings.warn(
        "Module bpy not found. Loading pycave.objects as standalone")


def generate_material_from_image(filename):
    """Generate Blender material from image for texturing"""
    material_name = bpy.path.display_name_from_filepath(filename)
    material = bpy.data.materials.new(name=material_name)
    texture_slot = material.texture_slots.add()
    texture_name = '_'.join(
        (os.path.splitext(os.path.basename(filename))[0],
         "image_texture")
    )
    #TODO: Get image directory
    image_texture = bpy.data.textures.new(name=texture_name, type="IMAGE")
    image_texture.image = bpy.data.images.load(filename)
    # NOTE: The above already raises a sensible RuntimeError if file is not
    # found
    image_texture.image.use_alpha = True
    texture_slot.texture = image_texture
    texture_slot.texture_coords = 'UV'

    #material.alpha = 0.0
    #material.specular_alpha = 0.0
    #texture_slot.use_map_alpha
    #material.use_transparency = True

    return material


class CaveLink(CaveFeature):
    """Store data on a clickable link

    :param bool enabled: Is link enabled?
    :param bool remain_enabled: Should link remain enabled after activation?
    :param tuple enabled_color: RGB color when link is enabled
    :param tuple selected_color: RGB color when link is selected
    :param actions: Dictionary mapping number of clicks to CaveActions
    (negative for any click)
    :param int reset: Number of clicks after which to reset link (negative
    value to never reset)"""

    argument_validators = {
        "enabled": AlwaysValid(help_string="Either true or false"),
        "remain_enabled": AlwaysValid(help_string="Either true or false"),
        "enabled_color": IsNumericIterable(required_length=3),
        "selected_color": IsNumericIterable(required_length=3),
        "actions": AlwaysValid(
            help_string="Must be a dictionary mapping integers to lists of "
            "CaveActions"
            ),
        "reset": IsNumeric()
        }

    default_arguments = {
        "enabled": True,
        "remain_enabled": True,
        "enabled_color": (0, 128, 255),
        "selected_color": (255, 0, 0),
        "reset": -1
        }

    def __init__(self, *args, **kwargs):
        super(CaveLink, self).__init__(*args, **kwargs)
        if "actions" not in self:
            self["actions"] = defaultdict(list),
        self.num_clicks = 0

    def toXML(self, object_root):
        """Store CaveLink as LinkRoot node within Object node

        :param :py:class:xml.etree.ElementTree.Element object_root
        """
        linkroot_node = ET.SubElement(object_root, "LinkRoot")
        link_node = ET.SubElement(linkroot_node, "Link")

        node = ET.SubElement(link_node, "Enabled")
        node.text = bool2text(self["enabled"])
        node = ET.SubElement(link_node, "RemainEnabled")
        node.text = bool2text(self["remain_enabled"])
        node = ET.SubElement(link_node, "EnabledColor")
        node.text = "{},{},{}".format(*self["enabled_color"])
        node = ET.SubElement(link_node, "SelectedColor")
        node.text = "{},{},{}".format(*self["selected_color"])

        for clicks, action_list in self["actions"]:
            for current_action in action_list:
                actions_node = ET.SubElement(link_node, "Actions")
                current_action.toXML(actions_node)
                clicks_node = ET.SubElement(actions_node, "Clicks")
                if clicks < 0:
                    ET.SubElement(clicks_node, "Any")
                else:
                    ET.SubElement(
                        clicks_node,
                        "NumClicks",
                        attrib={
                            "num_clicks": str(clicks),
                            "reset": bool2text(self["reset"] == clicks)
                            }
                        )

        return linkroot_node

    @classmethod
    def fromXML(link_class, link_root):
        """Create CaveLink from LinkRoot node

        :param :py:class:xml.etree.ElementTree.Element link_root
        """
        link = link_class()
        link_node = link_root.find("Link")
        if link_node is None:
            raise BadCaveXML("LinkRoot element has no Link subelement")
        link["enabled"] = text2bool(find_xml_text(link_node, "Enabled"))
        link["remain_enabled"] = text2bool(
            find_xml_text(link_node, "RemainEnabled"))
        node = link_node.find("EnabledColor")
        if node is not None:
            link["enabled_color"] = text2tuple(node.text)
        node = link_node.find("SelectedColor")
        if node is not None:
            link["selected_color"] = text2tuple(node.text)
        for actions_node in link_node.findall("Actions"):
            num_clicks = -1
            for child in actions_node:
                if child.tag == "Clicks":
                    num_clicks_node = child.find("NumClicks")
                    if num_clicks_node is not None:
                        try:
                            num_clicks = num_clicks_node.attrib["num_clicks"]
                        except KeyError:
                            raise BadCaveXML(
                                "num_clicks attribute not set in NumClicks"
                                "node")
                        try:
                            if text2bool(num_clicks_node.attrib["reset"]):
                                if (num_clicks < link["reset"]
                                        or link["reset"] == -1):
                                    link["reset"] = num_clicks
                        except KeyError:
                            pass
                else:
                    link["actions"][num_clicks].append(
                        CaveAction.fromXML(child))

        return link


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
        object_root = ET.SubElement(
            all_objects_root, "Object", attrib={"name": self["name"]})
        node = ET.SubElement(object_root, "Visible")
        node.text = bool2text(self["visible"])
        node = ET.SubElement(object_root, "Color")
        node.text = "{},{},{}".format(*self["color"])
        node = ET.SubElement(object_root, "Lighting")
        node.text = bool2text(self["lighting"])
        node = ET.SubElement(object_root, "ClickThrough")
        node.text = bool2text(self["click_through"])
        node = ET.SubElement(object_root, "AroundSelfAxis")
        node.text = bool2text(self["around_own_axis"])
        node = ET.SubElement(object_root, "Scale")
        node.text = str(self["scale"] / self["content"].blender_scaling)
        if self["sound"] is not None:
            node = ET.SubElement(
                object_root, "SoundRef", attrib={"name": self["sound"]})
            node.text = self["sound"]
        self["placement"].toXML(object_root)
        if self["link"] is not None:
            self["link"].toXML(object_root)
        self["content"].toXML(object_root)

        return object_root

    @classmethod
    def fromXML(object_class, object_root):
        """Create CaveObject from Object node

        :param :py:class:xml.etree.ElementTree.Element object_root
        """
        new_object = object_class()
        try:
            new_object["name"] = object_root.attrib["name"]
        except KeyError:
            raise BadCaveXML("All Object nodes must have a name attribute set")
        node = object_root.find("Visible")
        if node is not None:
            new_object["visible"] = text2bool(node.text)
        node = object_root.find("Color")
        if node is not None:
            new_object["color"] = text2tuple(node.text, evaluator=int)
        node = object_root.find("Lighting")
        if node is not None:
            new_object["lighting"] = text2bool(node.text)
        node = object_root.find("ClickThrough")
        if node is not None:
            new_object["click_through"] = text2bool(node.text)
        node = object_root.find("AroundSelfAxis")
        if node is not None:
            new_object["around_own_axis"] = text2bool(node.text)
        node = object_root.find("Scale")
        if node is not None:
            new_object["scale"] = float(node.text)
        node = object_root.find("SoundRef")
        if node is not None:
            try:
                new_object["sound"] = node.attrib["name"]
            except KeyError:
                raise BadCaveXML("SoundRef node must have name attribute set")
        node = object_root.find("Placement")
        if node is not None:
            new_object["placement"] = CavePlacement.fromXML(node)
        node = object_root.find("Content")
        if node is not None:
            new_object["content"] = CaveContent.fromXML(node)
            new_object["scale"] = (
                new_object["scale"] * new_object["content"].blender_scaling)
        return new_object

    def apply_material(self, blender_object):
        """Apply properties of object to material for Blender object"""
        if blender_object.active_material is None:
            blender_object.active_material = bpy.data.materials.new(
                "{}_material".format(self["name"]))
            if blender_object.active_material is None:
                # Object cannot have active material
                return blender_object
        blender_object.active_material.diffuse_color = [
            channel/255.0 for channel in self["color"]]
        blender_object.active_material.specular_color = (
            blender_object.active_material.diffuse_color)
        blender_object.active_material.use_shadeless = not self["lighting"]
        blender_object.active_material.use_transparency = True
        blender_object.active_material.use_nodes = False
        return blender_object

    def blend(self):
        """Create representation of CaveObject in Blender"""
        blender_object = self["content"].blend()
        blender_object.name = "_".join(("object", self["name"]))
        blender_object.hide_render = not self["visible"]
        blender_object.scale = [self["scale"], ] * 3
        if "depth" in self["content"]:
            # Make extrusion independent of scale
            blender_object.scale[2] = 1

        self["placement"].place(blender_object)
        #TODO: Apply link
        if self["click_through"]:
            pass
            #TODO
        blender_object.game.physics_type = 'DYNAMIC'
        blender_object.game.use_ghost = True

        self.apply_material(blender_object)
        blender_object.layers = [layer == 0 for layer in range(20)]

        #TODO: Add around_own_axis
        #TODO: Add sound

        return blender_object

    def write_blender_logic(self):
        """Write Python logic for this object to associated script"""
        try:
            return self.blender_trigger.write_to_script()
        except AttributeError:
            warnings.warn(
                "blend() method must be called before write_blender_logic()")
            return None


class CaveContent(CaveFeature):
    """Represents content of a Cave object"""

    blender_scaling = 1

    @staticmethod
    def fromXML(content_root):
        """Create object of appropriate subclass from Content node

        :param :py:class:xml.etree.ElementTree.Element content_root
        """
        if content_root.find("None") is not None:
            return CaveContent()
        if content_root.find("Text") is not None:
            return CaveText.fromXML(content_root)
        if content_root.find("Image") is not None:
            return CaveImage.fromXML(content_root)
        if content_root.find("StereoImage") is not None:
            return CaveStereoImage.fromXML(content_root)
        if content_root.find("Model") is not None:
            return CaveModel.fromXML(content_root)
        if content_root.find("Light") is not None:
            return CaveLight.fromXML(content_root)
        if content_root.find("ParticleSystem") is not None:
            return CavePSys.fromXML(content_root)
        raise BadCaveXML("No known child node found in Content node")


class CaveText(CaveContent):
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
        "font": AlwaysValid("Filename of font"),
        "depth": IsNumeric()}

    default_arguments = {
        "halign": "center",
        "valign": "center",
        "font": None,
        "depth": 0}

    blender_scaling = 0.2
    blender_depth_scaling = 0.01

    def toXML(self, object_root):
        """Store CaveText as Content node within Object node

        :param :py:class:xml.etree.ElementTree.Element object_root
        """
        content_root = ET.SubElement(object_root, "Content")
        attrib = {
            "horiz-align": self["halign"],
            "vert-align": self["valign"],
            "depth": str(self["depth"]/self.blender_depth_scaling)
        }
        if not self.is_default("font"):
            attrib["font"] = self["font"]
        text_root = ET.SubElement(
            content_root, "Text", attrib=attrib
        )
        text_root.text = self["text"]

        return content_root

    @classmethod
    def fromXML(text_class, content_root):
        """Create CaveText object from Content node

        :param :py:class:xml.etree.ElementTree.Element content_root
        """
        new_text = text_class()
        text_root = content_root.find("Text")
        if text_root is not None:
            if "horiz-align" in text_root.attrib:
                new_text["halign"] = text_root.attrib["horiz-align"]
            if "vert-align" in text_root.attrib:
                new_text["valign"] = text_root.attrib["vert-align"]
            if "font" in text_root.attrib:
                new_text["font"] = text_root.attrib["font"]
            if "depth" in text_root.attrib:
                new_text["depth"] = (
                    float(text_root.attrib["depth"]) *
                    text_class.blender_depth_scaling)
            new_text["text"] = text_root.text
            return new_text
        raise InvalidArgument(
            "Content node must contain Text node to create CaveText object")

    def blend(self):
        """Create representation of CaveText in Blender"""
        bpy.ops.object.text_add(rotation=(math.pi/2, 0, 0))
        bpy.ops.object.transform_apply(rotation=True)
        new_text_object = bpy.context.object
        new_text_object.data.body = self["text"]
        #TODO: Get proper font directory
        if self["font"] is not None:
            new_text_object.data.font = bpy.data.fonts.load(self["font"])
        new_text_object.data.extrude = self["depth"]
        new_text_object.data.fill_mode = "BOTH"
        new_text_object.data.align = self["halign"].upper()
        #TODO: Vertical alignment. This is non-trivial
        new_text_object.select = True
        bpy.ops.object.convert(target='MESH', keep_original=False)
        new_text_object.select = False
        return new_text_object


class CaveImage(CaveContent):
    """Represent a flat image in the Cave

    :param str filename: Filename of image to be displayed"""
    argument_validators = {
        "filename": AlwaysValid("Value should be a string")}

    def toXML(self, object_root):
        """Store CaveImage as Content node within Object node

        :param :py:class:xml.etree.ElementTree.Element object_root
        """
        content_root = ET.SubElement(object_root, "Content")
        ET.SubElement(
            content_root, "Image", attrib={
                "filename": self["filename"]
                }
            )
        return content_root

    @classmethod
    def fromXML(image_class, content_root):
        """Create CaveImage object from Content node

        :param :py:class:xml.etree.ElementTree.Element content_root
        """
        new_image = image_class()
        image_root = content_root.find("Image")
        if image_root is not None:
            try:
                new_image["filename"] = image_root.attrib["filename"]
            except KeyError:
                raise BadCaveXML("Image node must have filename attribute set")
            return new_image
        raise InvalidArgument(
            "Content node must contain Image node to create CaveImage object")

    def blend(self):
        """Create representation of CaveImage in Blender"""
        bpy.ops.mesh.primitive_plane_add(rotation=(math.pi/2, 0, 0))
        bpy.ops.object.transform_apply(rotation=True)
        new_image_object = bpy.context.object

        material = generate_material_from_image(self["filename"])
        material.use_nodes = False
        image = material.texture_slots[0].texture.image

        new_image_object.active_material = material

        new_image_object.dimensions = image.size[0], image.size[1], 0
        new_image_object.data.uv_textures.new()
        new_image_object.data.materials.append(material)
        new_image_object.data.uv_textures[0].data[0].image = image
        material.game_settings.use_backface_culling = False
        material.game_settings.alpha_blend = 'ALPHA'

        return new_image_object


class CaveStereoImage(CaveContent):
    """Represents different images in left and right eye

    :param str left-file: Filename of image to be displayed to left eye
    :param str right-file: Filename of image to be displayed to right eye
    """
    argument_validators = {
        "left_file": AlwaysValid("Filename of left-eye image"),
        "right_file": AlwaysValid("Filename of right-eye image")}

    def toXML(self, object_root):
        """Store CaveStereoImage as Content node within Object node

        :param :py:class:xml.etree.ElementTree.Element object_root
        """
        content_root = ET.SubElement(object_root, "Content")
        ET.SubElement(
            content_root, "StereoImage", attrib={
                "left_file": self["left-image"],
                "right_file": self["right-image"]
                }
            )
        return content_root

    @classmethod
    def fromXML(image_class, content_root):
        """Create CaveStereoImage object from Content node

        :param :py:class:xml.etree.ElementTree.Element content_root
        """
        new_image = image_class()
        image_root = content_root.find("StereoImage")
        if image_root is not None:
            try:
                new_image["left_file"] = image_root.attrib["left-image"]
                new_image["right_file"] = image_root.attrib["right-image"]
            except KeyError:
                raise BadCaveXML(
                    "StereoImage node must have left-image and right-image "
                    "attributes set")
            return new_image
        raise InvalidArgument(
            "Content node must contain StereoImage node to create "
            "CaveStereoImage object")

    def blend(self):
        """Create representation of CaveStereoImage in Blender"""
        raise NotImplementedError  # TODO


class CaveModel(CaveContent):
    """Represents a 3d model in the Cave

    :param str filename: Filename of model to be displayed
    :param bool check_collisions: TODO Clarify what this does
    """
    argument_validators = {
        "filename": AlwaysValid("Value should be a string"),
        "check_collisions": AlwaysValid("Value should be a boolean")}

    default_arguments = {
        "check_collisions": False
        }

    def toXML(self, object_root):
        """Store CaveModel as Content node within Object node

        :param :py:class:xml.etree.ElementTree.Element object_root
        """
        content_root = ET.SubElement(object_root, "Content")
        ET.SubElement(
            content_root, "Model", attrib={
                "filename": self["filename"],
                "check-collisions": bool2text(self["check_collisions"])
                }
            )
        return content_root

    @classmethod
    def fromXML(model_class, content_root):
        """Create CaveModel object from Content node

        :param :py:class:xml.etree.ElementTree.Element content_root
        """
        new_model = model_class()
        model_root = content_root.find("Model")
        if model_root is not None:
            try:
                new_model["filename"] = model_root.attrib["filename"]
            except KeyError:
                raise BadCaveXML(
                    "StereoImage node must have filename attribute set")
            if "check-collisions" in model_root.attrib:
                new_model["check_collisions"] = text2bool(
                    model_root.attrib["check-collisions"])
            return new_model
        raise InvalidArgument(
            "Content node must contain Model node to create "
            "CaveModel object")

    def blend(self):
        """Create representation of CaveModel in Blender"""
        #TODO: Get proper directory
        bpy.ops.import_scene.obj(filepath=self["filename"])
        model_pieces = bpy.context.selected_objects
        for piece in model_pieces:
            bpy.context.scene.objects.active = piece
            bpy.ops.object.convert(target='MESH', keep_original=False)
        bpy.ops.object.join()
        new_model = bpy.context.object
        return new_model


class CaveLight(CaveContent):
    """Represents a light source in the Cave

    :param str light_type: Type of source, one of "Point", "Directional",
    "Spot"
    :param bool diffuse: Provide diffuse light?
    :param bool specular: Provide specular light?
    :param tuple attenuation: Tuple of 3 floats specifying constant, linear,
    and
    quadratic attenuation of light source respectively
    :param float angle: Angle in degrees specifying spread of spot light
    source
    """
    argument_validators = {
        "light_type": OptionListValidator("Point", "Directional", "Spot"),
        "diffuse": AlwaysValid("Value should be a boolean"),
        "specular": AlwaysValid("Value should be a boolean"),
        "attenuation": IsNumericIterable(3),
        "angle": IsNumeric()}
    default_arguments = {
        "diffuse": True,
        "specular": True,
        "attenuation": (1, 0, 0),
        "angle": 30}

    def toXML(self, object_root):
        """Store CaveLight as Content node within Object node

        :param :py:class:xml.etree.ElementTree.Element object_root
        """
        content_root = ET.SubElement(object_root, "Content")
        light_root = ET.SubElement(
            content_root, "Light")
        if not self.is_default("diffuse"):
            light_root.attrib["diffuse"] = bool2text(self["diffuse"])
        if not self.is_default("specular"):
            light_root.attrib["specular"] = bool2text(self["specular"])
        if not self.is_default("attenuation"):
            light_root.attrib["const_atten"] = str(self["attenuation"][0])
            light_root.attrib["lin_atten"] = str(self["attenuation"][1])
            light_root.attrib["quad_atten"] = str(self["attenuation"][2])
        if self["light_type"] == "Point":
            ET.SubElement(light_root, "Point")
        if self["light_type"] == "Directional":
            ET.SubElement(light_root, "Directional")
        if self["light_type"] == "Spot":
            ET.SubElement(light_root, "Spot", attrib={
                "angle": str(self["angle"])})

    @classmethod
    def fromXML(light_class, content_root):
        """Create CaveLight object from Content node

        :param :py:class:xml.etree.ElementTree.Element content_root
        """
        new_light = light_class()
        light_root = content_root.find("Light")
        if light_root is not None:
            if "diffuse" in light_root.attrib:
                new_light["diffuse"] = text2bool(light_root.attrib["diffuse"])
            if "specular" in light_root.attrib:
                new_light["specular"] = text2bool(
                    light_root.attrib["specular"])
            new_light["attenuation"] = list(new_light["attenuation"])
            for index, factor in enumerate(("const_atten", "lin_atten",
                                            "quad_atten")):
                if factor in light_root.attrib:
                    new_light["attenuation"][index] = text2bool(
                        light_root.attrib[factor])
            new_light["attenuation"] = tuple(new_light["attenuation"])
            for light_type in CaveLight.argument_validators[
                    "light_type"].valid_options:
                type_root = light_root.find(light_type)
                if type_root is not None:
                    new_light["light_type"] = light_type
                    if "angle" in type_root.attrib:
                        new_light["angle"] = float(type_root.attrib["angle"])
                    break
            return new_light
        raise InvalidArgument(
            "Content node must contain Light node to create CaveLight object")

    def blend(self):
        """Create representation of CaveLight in Blender"""
        #TODO: Check default direction of lights in legacy
        light_type_conversion = {
            "Point": "POINT", "Directional": "SUN", "Spot": "SPOT"
        }
        bpy.ops.object.lamp_add(
            type=light_type_conversion[self["light_type"]],
            rotation=(-math.pi/2, 0, 0)
        )
        # TODO: Why isn't the following working?
        # bpy.ops.object.transform_apply(rotation=True)
        new_light_object = bpy.context.object
        new_light_object.data.use_diffuse = self["diffuse"]
        new_light_object.data.use_specular = self["specular"]
        new_light_object.data.energy = (
            new_light_object.data.energy/self["attenuation"][0]
        )
        if self["light_type"] != "Directional":
            new_light_object.data.falloff_type = "LINEAR_QUADRATIC_WEIGHTED"
            new_light_object.data.linear_attenuation = self["attenuation"][1]
            new_light_object.data.quadratic_attenuation = self[
                "attenuation"][2]
        new_light_object.data.distance = 1
        # NOTE: Blender and OpenGL define attenuation factors differently, and
        # this implementation is in no way equivalent to that in the legacy
        # software. The implementation of constant attenuation is particularly
        # suspect, as is the distance.
        if self["light_type"] == "Spot":
            new_light_object.data.spot_size = math.radians(self["angle"])
        return new_light_object


class CavePSys(CaveContent):
    """Represents a particle system in the Cave

    NOT YET IMPLEMENTED AT ALL"""
    # TODO: everything
