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
import xml.etree.ElementTree as ET
from .names import generate_paction_name
from .features import W3DFeature
from .validators import ValidPyString, IsNumeric,\
    IsInteger, FeatureValidator, OptionValidator, ListValidator
from .errors import BadW3DXML
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

    default_arguments = {
        "radius": 1,
        "center": (0, 0, 0),
        "radius-inner": 0
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
                options["type"] = child.tag
                return domain_class(**options)

    def toXML(self, parent_root):
        """Store W3DPDomain as ParticleDomain node within parent node"""
        domain_node = ET.SubElement(parent_root, "ParticleDomain")
        geom_node = ET.SubElement(domain_node, self["type"])
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
        if self["type"] in ("Point", "Plane"):
            return """
    while True:
        yield mathutils.Vector({})
        """.format(self["point"])

        if self["type"] == "Line":
            return """
    line_vec = (
        mathutils.Vector({p2}) - mathutils.Vector({p1})
    )
    while True:
        yield mathutils.Vector({p1}) + random.random()*line_vec
            """.format(p2=self["p2"], p1=self["p1"])

        if self["type"] == "Triangle":
            return """
    p1 = mathutils.Vector({p1})
    p2 = mathutils.Vector({p2})
    p3 = mathutils.Vector({p3})
    while True:
        r1 = random.uniform(0, 1)
        r2 = random.uniform(0, 1)
        yield (
            (1 - math.sqrt(r1)) * p1 +
            (math.sqrt(r1) * (1 - math.sqrt(r2))) * p2 +
            r2 * math.sqrt(r1) * p3
        )""".format(p1=self["p1"], p2=self["p2"], p3=self["p3"])

        if self["type"] == "Rect":
            return """
    point = mathutils.Vector({point})
    u_vec = mathutils.Vector({u_vec})
    v_vec = mathutils.Vector({u_vec})
    while True:
        r1 = random.uniform(0, 1)
        r2 = random.uniform(0, 1)
        yield (
            point + r1 * u_vec + r2 * v_vec
        )""".format(
                point=self["point"], u_vec=self["u-dir"], v_vec=self["v-dir"]
            )

        if self["type"] == "Box":
            return """
    p1 = mathutils.Vector({p1})
    p2 = mathutils.Vector({p2})
    diff = p2 - p1
    while True:
        new_vec = mathutils.Vector(
            [diff[i] * random.uniform(0, 1) for i in range(len(diff))]
        )
        yield (
            p1 + new_vec
        )""".format(p2=self["p2"], p1=self["p1"])

        if self["type"] == "Cylinder":
            return """
    p1 = mathutils.Vector({p1})
    p2 = mathutils.Vector({p2})
    radii = ({radius}, {radius_inner})
    radius_inner = min(radii)
    radius_outer = max(radii)
    axis = p2 - p1
    normal = axis.normalized()

    basis = mathutils.Vector((1, 0, 0))
    if abs(basis.dot(normal)) > 0.999:
        basis = mathutils.Vector((0, 1, 0))

    u = basis - normal.dot(basis) * normal
    u.normalize()
    v = normal.cross(u)
    while True:
        theta = 2 * math.pi * random.uniform(0, 1)
        height = random.uniform(0, 1)
        dist = random.uniform(radius_inner, radius_outer)
        yield (
            p1 + height * axis + dist * math.sin(theta) * u +
            dist * math.cos(theta) * v
        )""".format(
                p1=self["p1"], p2=self["p2"], radius=self["radius"],
                radius_inner=self["radius-inner"]
            )

        if self["type"] == "Cone":
            return """
    p1 = mathutils.Vector({p1})
    p2 = mathutils.Vector({p2})
    radii = ({radius}, {radius_inner})
    radius_inner = min(radii)
    radius_outer = max(radii)
    axis = p2 - p1
    normal = axis.normalized()

    basis = mathutils.Vector((1, 0, 0))
    if abs(basis.dot(normal)) > 0.999:
        basis = mathutils.Vector((0, 1, 0))

    u = basis - normal.dot(basis) * normal
    u.normalize()
    v = normal.cross(u)
    while True:
        theta = 2 * math.pi * random.uniform(0, 1)
        height = random.uniform(0, 1)
        dist = random.uniform(radius_inner, radius_outer) * height
        yield (
            p1 + height * axis + dist * math.sin(theta) * u +
            dist * math.cos(theta) * v
        )""".format(
                p1=self["apex"], p2=self["base-center"], radius=self["radius"],
                radius_inner=self["radius-inner"]
            )

        if self["type"] == "Blob":
            return """
    center = mathutils.Vector({center})
    stdev = {stdev}
    while True:
        yield (
            center + mathutils.Vector([
                random.gauss(0, stdev) for i in range(3)
            ])
        )""".format(center=self["center"], stdev=self["stdev"])

        if self["type"] == "Disc":
            return """
    p1 = mathutils.Vector({p1})
    radii = ({radius}, {radius_inner})
    radius_inner = min(radii)
    radius_outer = max(radii)
    normal = mathutils.Vector({normal}).normalized()

    basis = mathutils.Vector((1, 0, 0))
    if abs(basis.dot(normal)) > 0.999:
        basis = mathutils.Vector((0, 1, 0))

    u = basis - normal.dot(basis) * normal
    u.normalize()
    v = normal.cross(u)
    while True:
        theta = 2 * math.pi * random.uniform(0, 1)
        dist = random.uniform(radius_inner, radius_outer)
        yield (
            p1 + dist * math.sin(theta) * u + dist * math.cos(theta) * v
        )""".format(
                p1=self["center"], normal=self["normal"],
                radius=self["radius"], radius_inner=self["radius-inner"]
            )

        # if self["type"] == "Sphere":
        else:
            return """
    while True:
        radius = random.uniform({radius_inner}, {radius})
        phi = random.uniform(0, 2*math.pi)
        theta = random.uniform(0, math.pi)
        vel_vec = mathutils.Vector(
            (
                radius*math.sin(theta)*math.cos(phi),
                radius*math.sin(theta)*math.sin(phi),
                radius*math.cos(theta)
            )
        )
        yield vel_vec
            """.format(
                radius_inner=self["radius-inner"], radius=self["radius"]
            )


class W3DPAction(W3DFeature):
    """Represents the actions for a particle system
    """

    argument_validators = {
        "name": ValidPyString(),
        "source_domain": FeatureValidator(W3DPDomain),
        "velocity_domain": FeatureValidator(W3DPDomain),
        "rate": IsInteger(min_value=1)
    }

    default_arguments = {
        "rate": 1
    }

    logic_template = """
import bge
import mathutils
import random
import math
import logging
W3D_LOG = logging.getLogger('W3D')
rate = max(int(bge.logic.getLogicTicRate()/{spec_rate}), 1)

def _get_source_vector():
{source_domain_logic}

_source_gen = _get_source_vector()

def get_source_vector():
    W3D_LOG.debug("Getting source vector...")
    return next(_source_gen)

def _get_velocity_vector():
{velocity_domain_logic}

_vel_gen = _get_velocity_vector()

def get_velocity_vector():
    W3D_LOG.debug("Getting velocity vector...")
    return next(_vel_gen)
    """

    @classmethod
    def fromXML(paction_class, paction_root):
        """Create W3DPAction from ParticleActionList root"""
        paction = paction_class()
        paction["name"] = paction_root.attrib["name"]

        source_root = paction_root.find("Source")
        if source_root is None:
            raise BadW3DXML("ParticleActionList must have Source subelement")
        try:
            paction["rate"] = int(source_root.attrib["rate"])
        except KeyError:
            raise BadW3DXML("Source must specify rate attribute")
        source_domain_root = source_root.find("ParticleDomain")
        if source_domain_root is None:
            raise BadW3DXML("Source must have ParticleDomain subelement")
        paction["source_domain"] = W3DPDomain.fromXML(source_domain_root)

        vel_root = paction_root.find("Vel")
        if vel_root is None:
            raise BadW3DXML("ParticleActionList must have Vel subelement")
        vel_domain_root = vel_root.find("ParticleDomain")
        if vel_domain_root is None:
            raise BadW3DXML("Vel must have ParticleDomain subelement")
        paction["velocity_domain"] = W3DPDomain.fromXML(vel_domain_root)
        return paction

    def toXML(self, parent_root):
        """Store W3DPAction as ParticleActionList node within
        ParticleActionRoot node"""
        paction_node = ET.SubElement(parent_root, "ParticleActionList")
        paction_node.attrib["name"] = self["name"]

        source_node = ET.SubElement(paction_node, "Source")
        source_node.attrib["rate"] = str(self["rate"])
        self["source_domain"].toXML(source_node)

        vel_node = ET.SubElement(paction_node, "Vel")
        self["velocity_domain"].toXML(vel_node)

    def generate_logic(self):
        return self.logic_template.format(
            spec_rate=self["rate"],
            source_domain_logic=self["source_domain"].generate_logic(),
            velocity_domain_logic=self["velocity_domain"].generate_logic()
        )

    def blend(self):
        """Create representation of W3DPSys in Blender"""
        paction_name = generate_paction_name(self["name"])
        paction_module = "{}.py".format(paction_name)
        bpy.data.texts.new(paction_module)
        script = bpy.data.texts[paction_module]
        script.write(self.generate_logic())

        return script
