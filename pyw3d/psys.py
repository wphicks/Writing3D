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
from .names import generate_group_name, generate_paction_name
from .features import W3DFeature
from .validators import ValidPyString, ReferenceValidator, IsNumeric,\
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
        if self["type"] == "Point":
            return "    return {}".format(self["point"])
        if self["type"] == "Line":
            return """
    line_vec = (
        mathutils.Vector({}) - mathutils.Vector({})
    )
    while True:
        yield random.random()*line_vec
            """.format(self["p2"], self["p1"])


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
    }

    logic_template = """
import bge
rate = max(int(bge.logic.getLogicTicRate()/{spec_rate}), 1)

def get_source_vector():
{source_domain_logic}

def get_velocity_vector():
{velocity_domain_logic}
    """

    @classmethod
    def fromXML(paction_class, paction_root):
        """Create W3DPAction from ParticleActionList root"""
        paction = paction_class()
        paction["name"] = paction_root["name"]

        source_root = paction_root.find("Source")
        if source_root is None:
            raise BadW3DXML("ParticleActionList must have Source subelement")
        try:
            paction["rate"] = int(source_root["rate"])
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
        paction_node["name"] = self["name"]

        source_node = ET.SubElement(paction_node, "Source")
        source_node["rate"] = str(self["rate"])
        self["source_domain"].toXML(source_node)

        vel_node = ET.SubElement(paction_node, "Vel")
        self["velocity_domain"].toXML(vel_node)

    def generate_logic(self):
        return self.template.format(
            spec_rate=self["rate"],
            source_domain_logic=self["source_domain"].generate_logic(),
            velocity_domain_logic=self["velocity_domain"].generate_logic()
        )

    def blend(self):
        """Create representation of W3DPSys in Blender"""
        paction_name = generate_paction_name(self["name"])
        bpy.data.texts.new(paction_name)
        script = bpy.data.texts[paction_name]
        script.write(self.generate_logic())

        return script


class W3DPSys(W3DFeature):
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
from group_defs import *
import bge
from {particle_actions} import get_source_vector, get_velocity_vector, rate


def get_particle_template():
    return random.choice({group_name})


def activate_particles(cont):
    scene = bge.logic.getCurrentScene()
    own = cont.owner
    try:
        particle_count = own["particle_count"]
    except KeyError:
        own["particle_count"] = 0
        own["particle_tick"] = 0

    max_age = bge.logic.getLogicTicRate()*{max_age}

    if (
            own["particle_tick"] % rate == 0 and
            particle_count < {max_particles}):
        new_particle = scene.addObject(
            get_particle_template(),
            own.name,
            {max_age}
        )
        own["particle_count"] += 1
        new_particle.color = own.color
        new_particle.setLinearVelocity(get_velocity_vector())
        new_particle.worldPosition = own.worldPosition + get_source_vector()

    own["particle_tick"] += 1

    if (
            {max_age} and own["particle_tick"] % {max_age} == 0):
        own["particle_count"] += -1
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
            max_age=self["max_age"]
        )

    def blend(self):
        """Create representation of W3DPSys in Blender"""
        bpy.ops.object.add(
            type="EMPTY",
            layers=[layer == 0 for layer in range(20)]
        )
        psys_object = bpy.context.scene.objects.active

        bpy.ops.logic.sensor_add(
            type="PROPERTY",
            object=psys_object.name,
            name="visible_sensor"
        )
        psys_object.game.sensors[-1].name = "visible_sensor"
        visible_sensor = psys_object.game.sensors["visible_sensor"]
        visible_sensor.property = "visible"
        visible_sensor.value = True
        visible_sensor.use_pulse_true_level = True

        psys_name = "psys0"
        psys_index = 0
        while psys_name in bpy.data.texts:
            psys_name = "psys{}".format(psys_index)

        bpy.data.texts.new(psys_name)
        script = bpy.data.texts[psys_name]

        bpy.ops.logic.controller_add(
            type='PYTHON',
            object=psys_name,
            name="activate_particles"
        )
        controller = psys_object.game.controllers["activate_particles"]
        controller.mode = "MODULE"
        controller.module = "{}.activate_particles".format(psys_name)
        controller.link(visible_sensor)

        script.write(self.generate_logic())

        return psys_object
