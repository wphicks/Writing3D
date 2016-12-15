#!/usr/bin/env python
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

"""Tools for creating particle systems in W3D Projects
"""
import logging
from .names import generate_blender_object_name, generate_blender_psys_name
from .features import W3DFeature
from .validators import ValidPyString, ReferenceValidator, IsNumeric, IsInteger
LOGGER = logging.getLogger("pyw3d")
try:
    import bpy
except ImportError:
    LOGGER.info(
        "Module bpy not found. Loading pyw3d.psys as standalone")


class W3DPDomain(W3DFeature):
    """Represents a velocity or source domain for a particle system

    Domains are used to specify two things for a particle system: Where
    particles originate in space (the "source domain") and where they are
    headed upon creation (the "velocity domain"). The source domain is
    relatively easy to understand. Once a region is specified, particles will
    appear anywhere in that region.

    The velocity domain is somewhat trickier, so consider a few examples. If
    the velocity domain is a single point- say (0, 1, -3), then all generated
    particles will start with the same velocity. In this case, that means that
    all particles will initially move in the positive y-direction and negative
    z-direction.

    Next consider a spherical velocity domain with radius 3. Now, all particles
    will start with a speed between 0 and 3 but will move outward in any radial
    direction.  Finally, consider a cylinder with radius 1 and height 3. Now,
    all particles will move outward in a cylindrical pattern, but will tend to
    move more quickly along the axis of the cylinder than they will radially
    outward away from that axis.
    """

    argument_validators = {
        "type": OptionValidator(
            "Point", "Line", "Triangle", "Plane", "Rect", "Box", "Sphere",
            "Cylinder", "Cone", "Blob", "Disc"
        ),
        # TODO: What follows is a dirty kludge to get this project ready for
        # next semester. This should be replaced by separate subclasses for
        # each of the domain types.
        "point": ListValidator(IsNumeric(), required_length=3),
        "p1": ListValidator(IsNumeric(), required_length=3),
        "p2": ListValidator(IsNumeric(), required_length=3),
        "p3": ListValidator(IsNumeric(), required_length=3),
        "normal": ListValidator(IsNumeric(), required_length=3),
        "u-dir": ListValidator(IsNumeric(), required_length=3),
        "v-dir": ListValidator(IsNumeric(), required_length=3),
        "center": ListValidator(IsNumeric(), required_length=3),
        "radius": IsNumeric(min_value=0),
        "radius-inner": IsNumeric(min_value=0),
        "base-center": ListValidator(IsNumeric(), required_length=3),
        "apex": ListValidator(IsNumeric(), required_length=3),
        "stdev": IsNumeric(min_value=0),
    }

    @classmethod
    def fromXML(domain_class, domain_root):
        """Create W3DPDomain from ParticleDomain root"""
        for child in domain_root:
            if (
                    child.tag in
                    domain_class.argument_validators[
                        "type"].valid_options):
                options = {
                    key: domain_class.argument_validators[key].coerce(value)
                    for key, value in child.attrib.items()
                }
                return domain_class(child.tag, **options)

    def toXML(self, parent_root):
        """Store W3DPDomain as ParticleDomain node within parent node"""
        domain_node = ET.SubElement(parent_root, "ParticleDomain")
        geom_node = ET.SubElement(domain_class, self["type"])
        for key in self:
            if key != "type":
                try:
                    geom_node.attrib[key] = "({})".format(
                        ",".join(str(val) for val in self[key])
                    )
                except TypeError:
                    geom_node.attrib[key] = str(self[key])
        return domain_node

    def generate_logic(self):
        if self["type"] == "Point":
            return "return {}".format(self["point"])


class W3DPSys(W3DFeature):
    """Represents a particle system in virtual space

    Particle systems are specified primarily by two objects: the source object
    and particle object. The source object specifies the region in which
    particles for the particle system are created. The particle object
    specifies what these particles look like. Thus, if one wanted to create a
    particle system with copies of an image exploding outward from a W-shaped
    region, one could specify a W3DText object as the source and a W3DImage
    object as the particle.

    :param str name: The name of this particle system
    :param str source_name: The name of the source object for this particle
    system
    :param str particle_name: The name of the object to use as the particle
    model for this system
    """

    argument_validators = {
        "name": ValidPyString(),
        "source": FeatureValidator(W3DPDomain),
        "particle_group": ReferenceValidator(
            ValidPyString(),
            ["group"],
            help_string="Must be the name of an object group"
        ),
        "number": IsInteger(min_value=1),
        "velocity": IsNumeric(min_value=0)
    }
    default_arguments = {
        "number": 100,
        "velocity": 1
    }

    def generate_logic(self):
        pass

    def blend(self):
        """Create representation of W3DPSys in Blender"""
        source_object_name = generate_blender_object_name(
            self["source_name"])
        part_object_name = generate_blender_object_name(
            self["particle_name"])
        psys_name = generate_blender_psys_name(self["name"])

        bpy.context.scene.objects.active = bpy.data.objects[
            source_object_name
        ]
        bpy.ops.object.particle_system_add()
        psys = bpy.data.particles[-1]
        psys.name = psys_name
        psys.count = self["number"]
        psys.render_type = "OBJECT"
        psys.dupli_object = bpy.data.objects[part_object_name]
        psys.particle_size = 1
        psys.normal_factor = self["velocity"]
