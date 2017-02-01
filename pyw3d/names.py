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

"""Generate universal names for objects in Blender"""


def generate_blender_timeline_name(string):
    """Generate name used for Blender timeline"""
    return "timeline_{}".format(string)


def generate_blender_object_name(string):
    """Generate name used for Blender object"""
    return "object_{}".format(string)


def generate_blender_sound_name(string):
    """Generate name used for Blender sound"""
    return "sound_{}".format(string)


def generate_blender_material_name(string):
    """Generate name used for Blender material"""
    return "material_{}".format(string)


def generate_blender_psys_name(string):
    """Generate name used for Blender particle system"""
    return "psys_{}".format(string)


def generate_paction_name(string):
    """Generate name used for Blender particle system actions"""
    return "paction_{}".format(string)


def generate_trigger_name(string):
    """Generate name used for Blender trigger"""
    return "trigger_{}".format(string)


def generate_link_name(string):
    """Generate name used for Blender trigger"""
    return "link_{}".format(string)


def generate_enabled_name(string):
    """Generate name for enabled properties"""
    return "{}_enabled".format(string)


def generate_group_name(string):
    """Generate name used for Blender group"""
    return "group_{}".format(string)


def generate_relative_to_name(string):
    """Generate name used for relative_to objects"""
    return "relative_to_{}".format(string)


def generate_light_object_name(string):
    """Generate name used for light objects"""
    return "light_object_{}".format(string)


def generate_blender_particle_name(string):
    """Generate name used for particle copies of objects"""
    return "particle_{}".format(string)
