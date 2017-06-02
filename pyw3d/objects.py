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

"""Tools for working with displayable objects in W3D projects
"""
import os
import xml.etree.ElementTree as ET
from collections import defaultdict
import math
from .errors import BadW3DXML, InvalidArgument, EBKAC
from .xml_tools import find_xml_text, text2bool, text2tuple, bool2text
from .features import W3DFeature
from .actions import W3DAction, ObjectAction, GroupAction, TimelineAction,\
    SoundAction, EventTriggerAction, MoveVRAction, W3DResetAction
from .placement import W3DPlacement
from .validators import OptionValidator, IsNumeric, ListValidator, IsInteger,\
    ValidPyString, IsBoolean, FeatureValidator, DictValidator,\
    TextValidator, ValidFile, ValidFontFile, ReferenceValidator
from .names import generate_blender_object_name,\
    generate_blender_material_name, generate_blender_sound_name,\
    generate_light_object_name, generate_paction_name, generate_group_name, \
    generate_blender_particle_name, generate_blender_curve_name
from .metaclasses import SubRegisteredClass
from .activators import BlenderClickTrigger
from .sounds import audio_playback_object
import logging
LOGGER = logging.getLogger("pyw3d")
try:
    import bpy
    import mathutils
    from _bpy import ops as ops_module
    BPY_OPS_CALL = ops_module.call
except ImportError:
    LOGGER.debug(
        "Module bpy not found. Loading pyw3d.objects as standalone")


def line_count(string):
    """Count lines in string"""
    return string.count('\n') + 1


def add_text_object(name, text):
    font_curve = bpy.data.curves.new(
        type="FONT", name=generate_blender_curve_name(name)
    )
    new_object = bpy.data.objects.new(name, font_curve)
    new_object.data.body = text
    new_object.data.space_line = 0.6
    return new_object


def apply_euler_rotation(blender_object, x, y, z):
    """Apply euler rotation (radians) to object"""
    blender_object.data.transform(
        mathutils.Euler((x, y, z), 'XYZ').to_matrix().to_4x4()
    )


def find_object_midpoint(blender_object):
    midpoint = mathutils.Vector((0, 0, 0))
    for vert in blender_object.data.vertices:
        midpoint += vert.co
    return (
        midpoint / len(blender_object.data.vertices)
    )


def set_object_center(blender_object, center_vec):
    blender_object.data.transform(
        mathutils.Matrix.Translation(
            blender_object.matrix_world.translation - center_vec
        )
    )


def duplicate_object(original):
    """Duplicate given object"""
    new = original.copy()
    if original.data is not None:
        new.data = original.data.copy()
    new.animation_data_clear()
    bpy.context.scene.objects.link(new)
    return new


def generate_object_from_model(filename):
    """Generate Blender object from model file"""
    try:
        return duplicate_object(
            generate_object_from_model._models[filename]
        )
    except AttributeError:
        generate_object_from_model._models = {}
    except KeyError:
        BPY_OPS_CALL(
            "import_scene.obj", None,
            {'filepath': filename}
        )
        model_pieces = bpy.context.selected_objects
        for piece in model_pieces:
            bpy.context.scene.objects.active = piece
            BPY_OPS_CALL(
                "object.convert", None,
                {'target': 'MESH', 'keep_original': False}
            )
        BPY_OPS_CALL("object.join", None, {})
        new_model = bpy.context.object
        generate_object_from_model._models[filename] = new_model

        return new_model

    return generate_object_from_model(filename)


def generate_material_from_image(filename, double_sided=True):
    """Generate Blender material from image for texturing"""
    try:
        return generate_material_from_image._materials[
            filename][double_sided]
    except AttributeError:
        generate_material_from_image._materials = {}
    except KeyError:
        material_name = bpy.path.display_name_from_filepath(filename)

        material_single = bpy.data.materials.new(
            name="{}{}".format(material_name, 0)
        )
        material_double = bpy.data.materials.new(
            name="{}{}".format(material_name, 1)
        )
        texture_slot_single = material_single.texture_slots.add()
        texture_slot_double = material_double.texture_slots.add()

        texture_name = '_'.join(
            (os.path.splitext(os.path.basename(filename))[0],
             "image_texture")
        )
        image_texture = bpy.data.textures.new(name=texture_name, type="IMAGE")
        image_texture.image = bpy.data.images.load(filename)
        # NOTE: The above already raises a sensible RuntimeError if file is not
        # found
        image_texture.image.use_alpha = True

        texture_slot_single.texture = image_texture
        texture_slot_double.texture = image_texture
        texture_slot_single.texture_coords = 'UV'
        texture_slot_double.texture_coords = 'UV'

        # material.alpha = 0.0
        # material.specular_alpha = 0.0
        # texture_slot.use_map_alpha
        # material.use_transparency = True
        material_single.game_settings.use_backface_culling = True
        material_double.game_settings.use_backface_culling = False

        generate_material_from_image._materials[filename] = (
            material_single, material_double
        )

    return generate_material_from_image(
        filename, double_sided=double_sided)


class W3DLink(W3DFeature):
    """Store data on a clickable link

    :param bool enabled: Is link enabled?
    :param bool remain_enabled: Should link remain enabled after activation?
    :param tuple enabled_color: RGB color when link is enabled
    :param tuple selected_color: RGB color when link is selected
    :param actions: Dictionary mapping number of clicks to W3DActions
        (negative for any click)
    :param int reset: Number of clicks after which to reset link (negative
        value to never reset)"""

    ui_order = [
        "enabled", "remain_enabled", "selected_color", "reset", "actions"]

    argument_validators = {
        "enabled": IsBoolean(),
        "remain_enabled": IsBoolean(),
        "enabled_color": ListValidator(
            IsInteger(min_value=0, max_value=255), required_length=3),
        "selected_color": ListValidator(
            IsInteger(min_value=0, max_value=255), required_length=3),
        "actions": DictValidator(
            IsInteger(), ListValidator(FeatureValidator(W3DAction)),
            help_string="Must be a dictionary mapping integers to lists of "
            "W3DActions"
        ),
        "reset": IsInteger()
    }

    default_arguments = {
        "enabled": True,
        "remain_enabled": True,
        "enabled_color": (0, 128, 255),
        "selected_color": (255, 0, 0),
        "reset": -1
    }

    def __init__(self, *args, **kwargs):
        super(W3DLink, self).__init__(*args, **kwargs)
        if "actions" not in self:
            self["actions"] = defaultdict(list)
        self.num_clicks = 0

    def toXML(self, object_root):
        """Store W3DLink as LinkRoot node within Object node

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

        for clicks, action_list in self["actions"].items():
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
        """Create W3DLink from LinkRoot node

        :param :py:class:xml.etree.ElementTree.Element link_root
        """
        link = link_class()
        link_node = link_root.find("Link")
        if link_node is None:
            raise BadW3DXML("LinkRoot element has no Link subelement")
        link["enabled"] = text2bool(find_xml_text(link_node, "Enabled"))
        link["remain_enabled"] = text2bool(
            find_xml_text(link_node, "RemainEnabled"))
        node = link_node.find("EnabledColor")
        if node is not None:
            link["enabled_color"] = text2tuple(node.text, evaluator=int)
        node = link_node.find("SelectedColor")
        if node is not None:
            link["selected_color"] = text2tuple(node.text, evaluator=int)
        for actions_node in link_node.findall("Actions"):
            num_clicks = -1
            clicks_node = actions_node.find("Clicks")
            if clicks_node is not None:
                num_clicks_node = clicks_node.find("NumClicks")
                if num_clicks_node is not None:
                    try:
                        num_clicks = int(
                            num_clicks_node.attrib["num_clicks"]
                        )
                    except (KeyError, ValueError):
                        raise BadW3DXML(
                            "num_clicks attribute not set to an integer in"
                            "NumClicks node"
                        )
                    try:
                        if text2bool(num_clicks_node.attrib["reset"]):
                            if (
                                    num_clicks < link["reset"] or
                                    link["reset"] == -1):
                                link["reset"] = num_clicks
                    except KeyError:
                        pass
            for child in actions_node:
                if child.tag != "Clicks":
                    link["actions"][num_clicks].append(
                        W3DAction.fromXML(child))

        return link

    def blend(self, object_name):
        """Create Blender object to implement W3DLink

        :param str object_name: The name of the object to which link is
        assigned"""
        self.activator = BlenderClickTrigger(
            object_name, self["actions"], object_name,
            enable_immediately=self["enabled"],
            remain_enabled=self["remain_enabled"],
            select_color=self["selected_color"],
            enable_color=self["enabled_color"],
            reset_clicks=self['reset']
        )
        self.activator.create_blender_objects()
        return self.activator.base_object

    def link_blender_logic(self):
        """Link BGE logic bricks for this W3DLink"""
        try:
            self.activator.link_logic_bricks()
        except AttributeError:
            raise EBKAC(
                "blend() must be called before link_blender_logic()")

    def write_blender_logic(self):
        """Write any necessary game engine logic for this W3DTimeline"""
        try:
            self.activator.write_python_logic()
        except AttributeError:
            raise EBKAC(
                "blend() must be called before write_blender_logic()")


class W3DContent(W3DFeature, metaclass=SubRegisteredClass):
    """Represents content of a W3D object"""

    blender_scaling = 1
    ui_order = []

    @staticmethod
    def fromXML(content_root):
        """Create object of appropriate subclass from Content node

        :param :py:class:xml.etree.ElementTree.Element content_root
        """
        if content_root.find("None") is not None:
            return W3DContent()
        if content_root.find("Text") is not None:
            return W3DText.fromXML(content_root)
        if content_root.find("Image") is not None:
            return W3DImage.fromXML(content_root)
        if content_root.find("StereoImage") is not None:
            return W3DStereoImage.fromXML(content_root)
        if content_root.find("Model") is not None:
            return W3DModel.fromXML(content_root)
        if content_root.find("Light") is not None:
            return W3DLight.fromXML(content_root)
        if content_root.find("ParticleSystem") is not None:
            return W3DPSys.fromXML(content_root)
        raise BadW3DXML("No known child node found in Content node")


class W3DShape(W3DContent):
    """ Create a shape object in virtual space

    :param str shape_type: type of shape to be created
    :param int radius: radius of the shape to be added
    :param tuple color: Three floats representing RGB color of object
    :param int depth: height of shape, if shape is cone/cylinder
    """
    ui_order = ["shape_type", "radius", "depth"]
    argument_validators = {
        "shape_type": OptionValidator(
            "Sphere", "Cube", "Cone", "Cylinder", "Monkey"),
        "radius": IsNumeric(),
        "depth": IsNumeric()
    }
    default_arguments = {
        "radius": 1,
        "depth": 2
    }

    def toXML(self, object_root):

        content_root = ET.SubElement(object_root, "Content")
        attrib = {
            "shape_type": self["shape_type"],
            "radius": self["radius"],
            "depth": self["depth"]
        }
        shape_root = ET.SubElement(
            content_root, "Shape")
        shape_root.attrib["radius"] = str(self["radius"])
        shape_root.attrib["shape_type"] = str(self["shape_type"])
        shape_root.attrib["depth"] = str(self["depth"])

    @classmethod
    def fromXML(shape_class, content_root):
        new_shape = shape_class()
        shape_root = content_root.find("Shape")
        numberValidator = IsNumeric()
        optionValidator = OptionValidator(
            "Sphere", "Cube", "Cone", "Cylinder", "Monkey")
        if shape_root is None:
            raise BadW3DXML("Content node has no Shape child node")
        if "radius" in shape_root.attrib:
            new_shape["radius"] = numberValidator.coerce(
                shape_root.attrib["radius"])
        if "shape_type" in shape_root.attrib:
            new_shape["shape_type"] = optionValidator.coerce(
                shape_root.attrib["shape_type"])
        if "depth" in shape_root.attrib:
            new_shape["depth"] = numberValidator.coerce(
                shape_root.attrib["depth"])
        return new_shape

    def blend(self):
        if self["shape_type"] == "Sphere":
            BPY_OPS_CALL(
                "mesh.primitive_uv_sphere_add", None,
                {'size': self["radius"]}
            )
        elif self["shape_type"] == "Cube":
            BPY_OPS_CALL(
                "mesh.primitive_cube_add", None,
                {'radius': self["radius"]}
            )
        elif self["shape_type"] == "Cone":
            BPY_OPS_CALL(
                "mesh.primitive_cone_add", None,
                {'radius1': self["radius"], 'depth': self["depth"]}
            )
        elif self["shape_type"] == "Cylinder":
            BPY_OPS_CALL(
                "mesh.primitive_cylinder_add", None,
                {'radius': self["radius"], 'depth': self["depth"]}
            )
        elif self["shape_type"] == "Monkey":
            BPY_OPS_CALL(
                "mesh.primitive_monkey_add", None,
                {'radius': self["radius"]}
            )

        new_shape_object = bpy.context.object

        return new_shape_object


class W3DText(W3DContent):
    """Represents text in virtual space

    :param str text: String of text to be displayed
    :param str halign: Horizontal alignment of text ("left", "right", "center")
    :param str valign: Vertical alignment of text ("top", "center", "bottom")
    :param str font: Name of font to be used
    :param float depth: Depth to extrude each letter
    """
    ui_order = ["text", "halign", "depth", "font"]
    argument_validators = {
        "text": TextValidator(),
        "halign": OptionValidator(
            "left", "right", "center"),
        "valign": OptionValidator(
            "top", "center", "bottom"),
        "font": ValidFontFile("Filename of font"),
        "depth": IsNumeric()}

    default_arguments = {
        "halign": "center",
        "valign": "center",
        "font": None,
        "depth": 0}

    blender_scaling = 0.169
    blender_depth_scaling = 0.004
    object_count = 0

    ui_order = ["text", "halign", "valign", "font", "depth"]

    _loaded_fonts = {}

    def toXML(self, object_root):
        """Store W3DText as Content node within Object node

        :param :py:class:xml.etree.ElementTree.Element object_root
        """
        content_root = ET.SubElement(object_root, "Content")
        attrib = {
            "horiz-align": self["halign"],
            "vert-align": self["valign"],
            "depth": str(self["depth"] / self.blender_depth_scaling)
        }
        if not self.is_default("font"):
            attrib["font"] = self["font"]
        text_root = ET.SubElement(
            content_root, "Text", attrib=attrib
        )
        text_root = ET.SubElement(text_root, "text")
        text_root.text = self["text"]

        return content_root

    @classmethod
    def fromXML(text_class, content_root):
        """Create W3DText object from Content node

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
            text_root = text_root.find("text")
            if text_root is not None:
                new_text["text"] = text_root.text
            else:
                raise BadW3DXML("Text node must contain text node")
            return new_text
        raise InvalidArgument(
            "Content node must contain Text node to create W3DText object")

    def blend(self):
        """Create representation of W3DText in Blender"""
        type(self).object_count += 1
        text_content = self["text"].strip()
        new_text_object = add_text_object(
            "text_{}".format(type(self).object_count), text_content
        )
        lines = line_count(text_content)
        if (
                self["font"] is not None and self["font"] not in
                self._loaded_fonts):
            if not os.path.isabs(self["font"]):
                font_file = os.path.join(os.getcwd(), self["font"])
                try:
                    new_text_object.data.font = bpy.data.fonts.load(font_file)
                except:
                    try:
                        new_text_object.data.font = bpy.data.fonts.load(
                            os.path.join(os.getcwd(), "fonts", self["font"])
                        )
                    except:
                        raise ConsistencyError(
                            "Font file {} could not be found".format(font_file)
                        )
            else:
                font_file = self["font"]
                try:
                    new_text_object.data.font = bpy.data.fonts.load(font_file)
                except:
                    raise ConsistencyError(
                        "Font file {} could not be found".format(font_file)
                    )
            self._loaded_fonts[self["font"]] = new_text_object.data.font
        elif self["font"] is not None:
            new_text_object.data.font = self._loaded_fonts[self["font"]]
        if self["font"] is not None:
            new_text_object.data.resolution_u = 1
            new_text_object.data.resolution_v = 1
        new_text_object.data.extrude = self["depth"]
        new_text_object.location.y += new_text_object.data.extrude
        new_text_object.data.fill_mode = "BOTH"
        new_text_object.data.align = self["halign"].upper()

        height = new_text_object.dimensions[1]
        if self["valign"] == "top":
            new_text_object.data.offset_y = (
                - 3 * height / 4
            )
        elif self["valign"] == "center":
            new_text_object.data.offset_y = (
                - height / 4 + (lines - 1) * height / 2
            )
        elif self["valign"] == "bottom":
            new_text_object.data.offset_y = (
                height / 4 + 0.85 * height * (lines - 1)
            )

        mesh = new_text_object.to_mesh(bpy.context.scene, False, 'PREVIEW')
        final_object = bpy.data.objects.new(
            "mesh_text_{}".format(type(self).object_count), mesh
        )
        bpy.context.scene.objects.link(final_object)
        apply_euler_rotation(final_object, math.pi / 2, 0, 0)
        return final_object


class W3DImage(W3DContent):
    """Represent a flat image in 3D space

    :param str filename: Filename of image to be displayed"""
    ui_order = ["filename"]
    argument_validators = {
        "filename": ValidFile()}

    def toXML(self, object_root):
        """Store W3DImage as Content node within Object node

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
        """Create W3DImage object from Content node

        :param :py:class:xml.etree.ElementTree.Element content_root
        """
        new_image = image_class()
        image_root = content_root.find("Image")
        if image_root is not None:
            try:
                new_image["filename"] = image_root.attrib["filename"]
            except KeyError:
                raise BadW3DXML("Image node must have filename attribute set")
            return new_image
        raise InvalidArgument(
            "Content node must contain Image node to create W3DImage object")

    def blend(self):
        """Create representation of W3DImage in Blender"""
        BPY_OPS_CALL(
            "mesh.primitive_plane_add", None,
            {'radius': 0.1524}
        )
        new_image_object = bpy.context.object
        apply_euler_rotation(new_image_object, math.pi / 2, 0, 0)

        material = generate_material_from_image(self["filename"])
        material.use_nodes = False
        image = material.texture_slots[0].texture.image

        new_image_object.active_material = material

        new_image_object.data.uv_textures.new()
        new_image_object.data.materials.append(material)
        new_image_object.data.uv_textures[0].data[0].image = image
        material.game_settings.alpha_blend = 'ALPHA'

        return new_image_object


class W3DStereoImage(W3DContent):
    """Represents different images in left and right eye

    :param str left_file: Filename of image to be displayed to left eye
    :param str right_file: Filename of image to be displayed to right eye
    """
    ui_order = ["left_file", "right_file"]
    argument_validators = {
        "left_file": ValidFile(help_string="Filename of left-eye image"),
        "right_file": ValidFile(help_string="Filename of right-eye image")}

    def toXML(self, object_root):
        """Store W3DStereoImage as Content node within Object node

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
        """Create W3DStereoImage object from Content node

        :param :py:class:xml.etree.ElementTree.Element content_root
        """
        new_image = image_class()
        image_root = content_root.find("StereoImage")
        if image_root is not None:
            try:
                new_image["left_file"] = image_root.attrib["left-image"]
                new_image["right_file"] = image_root.attrib["right-image"]
            except KeyError:
                raise BadW3DXML(
                    "StereoImage node must have left-image and right-image "
                    "attributes set")
            return new_image
        raise InvalidArgument(
            "Content node must contain StereoImage node to create "
            "W3DStereoImage object")

    def blend(self):
        """Create representation of W3DStereoImage in Blender"""
        raise NotImplementedError  # TODO


class W3DModel(W3DContent):
    """Represents a 3d model in virtual space

    :param str filename: Filename of model to be displayed
    :param bool check_collisions: TODO Clarify what this does
    """
    # TODO: Does not seem to play nice with GLSL shader. FIX THIS.
    ui_order = ["filename"]
    argument_validators = {
        "filename": ValidFile(),
        "check_collisions": IsBoolean()}

    default_arguments = {
        "check_collisions": False
    }

    def toXML(self, object_root):
        """Store W3DModel as Content node within Object node

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
        """Create W3DModel object from Content node

        :param :py:class:xml.etree.ElementTree.Element content_root
        """
        new_model = model_class()
        model_root = content_root.find("Model")
        if model_root is not None:
            try:
                new_model["filename"] = model_root.attrib["filename"]
            except KeyError:
                raise BadW3DXML(
                    "StereoImage node must have filename attribute set")
            if "check-collisions" in model_root.attrib:
                new_model["check_collisions"] = text2bool(
                    model_root.attrib["check-collisions"])
            return new_model
        raise InvalidArgument(
            "Content node must contain Model node to create "
            "W3DModel object")

    def blend(self):
        """Create representation of W3DModel in Blender"""
        return generate_object_from_model(self["filename"])


class W3DLight(W3DContent):
    """Represents a light source in virtual space

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
    ui_order = ["light_type", "diffuse", "specular", "angle", "attenuation"]
    argument_validators = {
        "light_type": OptionValidator("Point", "Directional", "Spot"),
        "diffuse": IsBoolean(),
        "specular": IsBoolean(),
        "attenuation": ListValidator(
            IsNumeric(), required_length=3),
        "angle": IsNumeric()}

    default_arguments = {
        "diffuse": True,
        "specular": True,
        "attenuation": (1, 0, 0),
        "angle": 30}

    def toXML(self, object_root):
        """Store W3DLight as Content node within Object node

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
        """Create W3DLight object from Content node

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
                    new_light["attenuation"][index] = float(
                        light_root.attrib[factor])
            for light_type in W3DLight.argument_validators[
                    "light_type"].valid_options:
                type_root = light_root.find(light_type)
                if type_root is not None:
                    new_light["light_type"] = light_type
                    if "angle" in type_root.attrib:
                        new_light["angle"] = float(type_root.attrib["angle"])
                    break
            return new_light
        raise InvalidArgument(
            "Content node must contain Light node to create W3DLight object")

    def blend(self):
        """Create representation of W3DLight in Blender"""
        # TODO: Check default direction of lights in legacy
        light_type_conversion = {
            "Point": "POINT", "Directional": "SUN", "Spot": "SPOT"
        }
        BPY_OPS_CALL(
            "object.lamp_add", None,
            {
                'type': light_type_conversion[self["light_type"]],
                'rotation': (-math.pi / 2, 0, 0)
            }
        )
        new_light_object = bpy.context.object
        new_light_object.data.use_diffuse = self["diffuse"]
        new_light_object.data.use_specular = self["specular"]
        new_light_object.data.energy = (
            new_light_object.data.energy / self["attenuation"][0]
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


class W3DObject(W3DFeature):
    """Store data on single W3D object

    :param str name: The name of the object
    :param W3DPlacement placement: Position and orientation of object
    :param W3DLink link: Clickable link for object
    :param tuple color: Three floats representing RGB color of object
    :param bool double_sided: Is object visible from both sides?
    :param bool visible: Is object visible?
    :param bool lighting: Does object respond to scene lighting?
    :param float scale: Scaling factor for size of object
    :param bool click_through: Should clicks also pass through object?
    :param bool around_own_axis: TODO clarify
    :param str sound: Name of sound element associated with this object
    :param content: Content of object; one of W3DText, W3DImage,
    W3DStereoImage, W3DModel, W3DLight, W3DPSys
    """

    ui_order = [
        "name", "placement", "scale", "visible", "lighting", "color",
        "click_through", "around_own_axis", "content"
    ]
    # TODO: Add sound
    argument_validators = {
        "name": ValidPyString(),
        "placement": FeatureValidator(
            W3DPlacement,
            help_string="Orientation and position of object"),
        "link": FeatureValidator(
            W3DLink,
            help_string="Clickable link associated with object"),
        "color": ListValidator(
            IsInteger(min_value=0, max_value=255), required_length=3),
        "double_sided": IsBoolean(),
        "visible": IsBoolean(),
        "lighting": IsBoolean(),
        "scale": IsNumeric(min_value=0),
        "click_through": IsBoolean(),
        "around_own_axis": IsBoolean(),
        "sound": TextValidator(),  # TODO: FIX THIS
        "content": FeatureValidator(W3DContent)}

    default_arguments = {
        "link": None,
        "color": (255, 255, 255),
        "visible": True,
        "lighting": False,
        "scale": 1,
        "click_through": False,
        "around_own_axis": False,
        "sound": None,
        "double_sided": True
    }

    def __init__(self, *args, **kwargs):
        super(W3DObject, self).__init__(*args, **kwargs)
        self.ui_order = [
            "name", "visible", "color", "lighting", "scale", "click_through",
            "around_own_axis", "sound", "placement", "link", "content"
        ]
        if "placement" not in self:
            self["placement"] = W3DPlacement()

    def toXML(self, all_objects_root):
        """Store W3DObject as Object node within ObjectRoot node

        :param :py:class:xml.etree.ElementTree.Element all_objects_root
        """
        object_root = ET.SubElement(
            all_objects_root, "Object", attrib={"name": self["name"]})
        node = ET.SubElement(object_root, "Visible")
        node.text = bool2text(self["visible"])
        if not self.is_default("double_sided"):
            node = ET.SubElement(object_root, "DoubleSided")
            node.text = bool2text(self["double_sided"])
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
        """Create W3DObject from Object node

        :param :py:class:xml.etree.ElementTree.Element object_root
        """
        new_object = object_class()
        try:
            new_object["name"] = object_root.attrib["name"]
        except KeyError:
            raise BadW3DXML("All Object nodes must have a name attribute set")
        node = object_root.find("Visible")
        if node is not None:
            new_object["visible"] = text2bool(node.text)
        node = object_root.find("DoubleSided")
        if node is not None:
            new_object["double_sided"] = text2bool(node.text)
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
                raise BadW3DXML("SoundRef node must have name attribute set")
        node = object_root.find("Placement")
        if node is not None:
            new_object["placement"] = W3DPlacement.fromXML(node)
        node = object_root.find("LinkRoot")
        if node is not None:
            new_object["link"] = W3DLink.fromXML(node)
        node = object_root.find("Content")
        if node is not None:
            new_object["content"] = W3DContent.fromXML(node)
            new_object["scale"] = (
                new_object["scale"] * new_object["content"].blender_scaling)
        return new_object

    def apply_material(self, blender_object):
        """Apply properties of object to material for Blender object"""
        if not len(blender_object.material_slots):
            blender_object.active_material = bpy.data.materials.new(
                generate_blender_material_name(self["name"]))
            if blender_object.active_material is not None:
                blender_object.active_material.game_settings.\
                    use_backface_culling = (
                        not self["double_sided"]
                    )
        else:
            for slot in blender_object.material_slots:
                slot.material = slot.material.copy()

        for slot in blender_object.material_slots:
            material = slot.material
            material.use_shadeless = not self["lighting"]
        #    material.use_transparency = True
        #    material.use_nodes = False
            material.use_object_color = True
        color = [channel / 255.0 for channel in self["color"]]
        color.append(int(self["visible"]))
        blender_object.color = color
        return blender_object

    def apply_lamp_color(self, new_light_object):
        color = [channel / 255.0 for channel in self["color"]]
        bpy.data.lamps[new_light_object.name].color = color
        return new_light_object

    def blend(self):
        """Create representation of W3DObject in Blender"""
        blender_object = self["content"].blend()
        blender_object.name = generate_blender_object_name(self["name"])
        blender_object.hide_render = not self["visible"]
        blender_object.scale = [self["scale"], ] * 3
        self["placement"].place(blender_object)
        LOGGER.debug("Object: {}".format(blender_object.name))
        LOGGER.debug("Position: {}".format(blender_object.location))
        for object_ in bpy.context.selectable_objects:
            object_.select = False
        blender_object.select = True
        bpy.context.scene.objects.active = blender_object

        blender_object.select = True
        bpy.context.scene.objects.active = blender_object

        BPY_OPS_CALL(
            "object.game_property_new", None,
            {'type': 'BOOL', 'name': 'visible_tag'}
        )
        blender_object.game.properties["visible_tag"].value = self["visible"]
        BPY_OPS_CALL(
            "object.game_property_new", None,
            {'type': 'BOOL', 'name': 'click_through'}
        )
        blender_object.game.properties[
            "click_through"].value = self["click_through"]

        blender_object.game.physics_type = 'DYNAMIC'
        blender_object.game.use_ghost = True

        if (
                bpy.data.lamps[-1] is not None and not
                bpy.data.lamps[-1].name.startswith("light_object_")):
            blender_lamp = bpy.data.lamps[-1]
            blender_lamp.name = generate_light_object_name(self["name"])
            self.apply_lamp_color(blender_lamp)

        self.apply_material(blender_object)
        blender_object.layers = [layer == 0 for layer in range(20)]

        if self["around_own_axis"]:
            set_object_center(
                blender_object, find_object_midpoint(blender_object)
            )

        # TODO: It is *ridiculous* to duplicate every single object to get
        # particle copies. This should be handled smartly in psys.py
        particle_name = generate_blender_particle_name(blender_object.name)
        particle_copy = duplicate_object(blender_object)
        particle_copy.name = particle_name
        particle_copy.hide_render = False
        particle_copy.color[3] = 1
        bpy.data.objects[particle_name].layers = [
            layer == 5 for layer in range(20)
        ]
        bpy.data.objects[particle_name].game.physics_type = 'DYNAMIC'

        if self["link"] is not None:
            self["link"].blend(generate_blender_object_name(self["name"]))

        if self["sound"] is not None:
            sound_name = generate_blender_sound_name(self["sound"])
            sound_actuator_name = generate_blender_sound_name(self["name"])
            BPY_OPS_CALL(
                "logic.actuator_add", None,
                {
                    'type': 'SOUND',
                    'object': blender_object.name,
                    'name': sound_actuator_name
                }
            )
            try:
                actuator = blender_object.game.actuators[sound_actuator_name]
                central_actuator = audio_playback_object().game.actuators[
                    sound_name]
            except KeyError:
                LOGGER.warn(
                    "Sound {} not found for object {}".format(
                        self["sound"], self["name"]
                    )
                )
                return blender_object
            actuator.sound = central_actuator.sound
            actuator.use_sound_3d = central_actuator.use_sound_3d
            actuator.mode = central_actuator.mode
            actuator.pitch = central_actuator.pitch
            actuator.volume = central_actuator.volume

        return blender_object

    def write_blender_logic(self):
        """Write Python logic for this object to associated script"""
        try:
            return self.blender_trigger.write_to_script()
        except AttributeError:
            LOGGER.debug(
                "blend() method must be called before write_blender_logic()")
            return None


class W3DPSys(W3DContent):
    """Represents a particle system in virtual space

    :param str particle_group: The name of the group of objects to use as
    particles in this system
    """

    argument_validators = {
        "particle_group": ReferenceValidator(
            ValidPyString(),
            ["group"],
            help_string="Must be the name of an object group"
        ),
        "particle_actions": ValidPyString(),
        "max_particles": IsInteger(min_value=1),
        "max_age": IsInteger(min_value=0),
        "speed": IsNumeric(min_value=0)
    }
    default_arguments = {
        "max_particles": 100,
        "max_age": 1,
        "speed": 1.0
    }
    logic_template = """
import mathutils
import random
from angles import *
from group_defs import *
import bge
from w3d_settings import *
from {particle_actions} import get_source_vector, get_velocity_vector, rate


def get_particle_template():
    return "particle_{{}}".format(random.choice({group_name}))


def activate_particles(cont):
    scene = bge.logic.getCurrentScene()
    own = cont.owner
    try:
        particle_count = own["particle_count"]
    except KeyError:
        own["particle_count"] = 0
        own["particle_tick"] = 0
        particle_count = 0
        activate_particles.particle_list =[]

    max_age = bge.logic.getLogicTicRate()*{max_age}

    if (
            own["particle_tick"] % rate == 0 and
            particle_count < {max_particles}):
        new_particle = scene.addObject(
            get_particle_template(),
            own.name,
            int({max_age}*bge.logic.getLogicTicRate())
        )
        activate_particles.particle_list.append(new_particle)
        own["particle_count"] += 1
        new_particle.visible = True
        new_particle.setLinearVelocity({speed}*get_velocity_vector())
        new_particle.worldPosition = (
            own.worldPosition + get_source_vector()
        )
        W3D_LOG.debug("System position: {{}}".format(
            own.worldPosition)
        )
        W3D_LOG.debug("Particle position: {{}}".format(
            new_particle.worldPosition)
        )

    own["particle_tick"] += 1

    activate_particles.particle_list = [
        particle for particle in activate_particles.particle_list if
        particle.life > 0.1
    ]
    own["particle_count"] = len(activate_particles.particle_list)
    for particle in activate_particles.particle_list:
        particle.color[3] = own.color[3]
    """

    @classmethod
    def fromXML(psys_class, psys_root):
        """Create W3DPSys from ParticleSystem root"""
        psys = psys_class()
        try:
            psys["particle_group"] = psys_root["particle-group"]
        except KeyError:
            raise BadW3DXML("ParticleSystem must specify particle-group")
        try:
            psys["particle_actions"] = psys_root["actions-name"]
        except KeyError:
            raise BadW3DXML("ParticleSystem must specify actions-name")
        try:
            psys["max_particles"] = psys_root["max-particles"]
        except KeyError:
            pass
        try:
            psys["speed"] = psys_root["speed"]
        except KeyError:
            pass
        return psys

    def toXML(self, parent_root):
        """Store W3DPSys as ParticleSystem node within Content node"""
        psys_node = ET.SubElement(parent_root, "ParticleSystem")
        psys_node["particle-group"] = self["particle_group"]
        psys_node["actions-name"] = self["particle_actions"]
        if not self.is_default("max_particles"):
            psys_node["max-particles"] = self["max_particles"]
        if not self.is_default("speed"):
            psys_node["speed"] = self["speed"]
        return psys_node

    def generate_logic(self):
        return self.logic_template.format(
            particle_actions=generate_paction_name(self["particle_actions"]),
            group_name=generate_group_name(self["particle_group"]),
            max_particles=self["max_particles"],
            max_age=self["max_age"],
            speed=self["speed"]
        )

    def blend(self):
        """Create representation of W3DPSys in Blender"""
        psys_name = "psys0"
        psys_index = 0
        psys_module = "{}.py".format(psys_name)
        while psys_module in bpy.data.texts:
            psys_name = "psys{}".format(psys_index)
            psys_module = "{}.py".format(psys_name)
            psys_index += 1

        bpy.data.texts.new(psys_module)
        script = bpy.data.texts[psys_module]

        psys_object = bpy.data.objects.new(psys_name, None)
        bpy.context.scene.objects.link(psys_object)

        bpy.context.scene.objects.active = psys_object

        BPY_OPS_CALL(
            "logic.sensor_add", None,
            {
                'type': 'PROPERTY', 'object': psys_object.name,
                'name': 'visible_sensor'
            }
        )
        psys_object.game.sensors[-1].name = "visible_sensor"
        visible_sensor = psys_object.game.sensors["visible_sensor"]
        visible_sensor.property = "visible_tag"
        visible_sensor.value = "True"
        visible_sensor.use_pulse_true_level = True

        bpy.context.scene.objects.active = psys_object
        BPY_OPS_CALL(
            "logic.controller_add", None,
            {
                'type': 'PYTHON', 'object': psys_object.name,
                'name': 'activate_particles'
            }
        )
        psys_object.game.controllers[-1].name = "activate_particles"
        controller = psys_object.game.controllers["activate_particles"]
        controller.mode = "MODULE"
        controller.module = "{}.activate_particles".format(psys_name)
        controller.link(visible_sensor)

        script.write(self.generate_logic())

        LOGGER.debug("Particle system created")

        return psys_object
