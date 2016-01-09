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


def generate_trigger_name(string):
    """Generate name used for Blender trigger"""
    return "trigger_{}".format(string)


def generate_enabled_name(string):
    """Generate name for enabled properties"""
    return "{}_enabled".format(string)


def generate_group_name(string):
    """Generate name used for Blender group"""
    return "group_{}".format(string)


def generate_link_name(string):
    """Generate name used for Blender link"""
    return "link_{}".format(string)
