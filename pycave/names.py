"""Generate universal names for objects in Blender"""


def generate_blender_timeline_name(string):
    """Generate name used for Blender timeline"""
    return "timeline_{}".format(string)


def generate_blender_object_name(string):
    """Generate name used for Blender object"""
    return "object_{}".format(string)


def generate_blender_material_name(string):
    """Generate name used for Blender material"""
    return "material_{}".format(string)
