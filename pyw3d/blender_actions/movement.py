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

"""Tools for moving a Blender object in virtual space"""
import math
import logging
from pyw3d.names import generate_relative_to_name
try:
    import mathutils
except ImportError:
    logging.debug(
        "Module mathutils not found. Loading pyw3d.blender_actions.movement as"
        " standalone")


def matrix_from_axis_angle(axis, angle):
    """Return rows of rotation matrix given axis-angle representation"""
    row1 = (
        axis[0]**2 * (1 - math.cos(angle)) + math.cos(angle),
        (
            axis[0] * axis[1] * (1 - math.cos(angle)) -
            axis[2] * math.sin(angle)
        ),
        (
            axis[0] * axis[2] * (1 - math.cos(angle)) +
            axis[1] * math.sin(angle)
        ),
    )
    row2 = (
        (
            axis[0] * axis[1] * (1 - math.cos(angle)) +
            axis[2] * math.sin(angle)
        ),
        axis[1]**2 * (1 - math.cos(angle)) + math.cos(angle),
        (
            axis[1] * axis[2] * (1 - math.cos(angle)) -
            axis[0] * math.sin(angle)
        ),
    )
    row3 = (
        (
            axis[0] * axis[2] * (1 - math.cos(angle)) -
            axis[1] * math.sin(angle)
        ),
        (
            axis[1] * axis[2] * (1 - math.cos(angle)) +
            axis[0] * math.sin(angle)
        ),
        axis[2]**2 * (1 - math.cos(angle)) + math.cos(angle),
    )
    return (row1, row2, row3)


class MoveAction(object):
    """Generate Python logic for how object should move when action first
    starts, as it continues, and when it ends

    :param placement: A W3DPlacement object specifying movement
    :param bool move_relative: Whether motion is specified relative to current
    location
    :param float duration: Time for action to complete in seconds
    :param int offset: A number of tabs (4 spaces) to add before Python logic
    strings"""

    @property
    def start_string(self):
        script_text = [
            "pos_vector = mathutils.Vector({})".format(
                self.placement["position"]),
            "relative_object = scene.objects['{}']".format(
                generate_relative_to_name(
                    self.placement['relative_to']
                )
            ),
        ]
        if self.move_relative:
            script_text.extend([
                "initial_orientation ="
                " blender_object.orientation.to_quaternion()",
                "target_orientation = initial_orientation"
            ])
        else:
            script_text.extend([
                "initial_orientation ="
                " relative_object.orientation.to_quaternion()",
                "target_orientation = initial_orientation",
            ])
        script_text.extend([
            "data['active_actions'][current_index]['target_orientation'] ="
            " target_orientation",
            "data['active_actions'][current_index]['initial_orientation'] ="
            " initial_orientation",
            "pos_vector.rotate(relative_object.orientation.to_quaternion()"
            ".rotation_difference(scene.objects['VRCENTER']"
            ".orientation.to_quaternion()))",
        ])

        # First take care of object rotation...
        if self.placement["rotation"]["rotation_mode"] != "None":

            vector = mathutils.Vector(
                self.placement["rotation"]["rotation_vector"])
            vector.normalize()
            if self.placement.is_default("position"):
                position_script = \
                    "data['active_actions'][current_index].get("\
                    "'target_pos', blender_object.position)"
            else:
                position_script = "pos_vector"
            angle = math.radians(
                self.placement["rotation"]["rotation_angle"])

            if self.move_relative:
                if self.placement[
                        "rotation"]["rotation_mode"] == "Axis":
                    script_text.extend([
                        "target_orientation = target_from_axis("
                        "{}, {}, initial_orientation="
                        "initial_orientation)".format(
                            tuple(vector), angle
                        ),
                    ])
                elif self.placement[
                        "rotation"]["rotation_mode"] == "Normal":
                    script_text.extend([
                        "target_orientation = target_from_normal("
                        "{}, {})".format(
                            tuple(vector), angle
                        ),
                    ])
                elif self.placement[
                        "rotation"]["rotation_mode"] == "LookAt":
                    script_text.extend([
                        "target_orientation = target_from_look("
                        "{}, {}, {})".format(
                            self.placement["rotation"]["rotation_vector"],
                            self.placement["rotation"]["up_vector"],
                            position_script
                        )
                    ])
            else:  # Not move relative
                script_text.append(
                    "orientation ="
                    "blender_object.orientation.to_quaternion()")

                if self.placement[
                        "rotation"]["rotation_mode"] == "Axis":
                    angle = math.radians(
                        self.placement["rotation"]["rotation_angle"]
                    )
                    script_text.extend([
                        "target_orientation = target_from_axis({}, {},"
                        " initial_orientation=initial_orientation)".format(
                            tuple(vector), angle
                        ),
                    ])

                elif self.placement[
                        "rotation"]["rotation_mode"] == "Normal":
                    script_text.extend([
                        "target_orientation = target_from_normal("
                        "{}, {},"
                        "initial_orientation=initial_orientation)".format(
                            tuple(vector), angle
                        ),
                    ])

                elif self.placement[
                        "rotation"]["rotation_mode"] == "LookAt":
                    script_text.extend([
                        "target_orientation = target_from_look("
                        "{}, {}, {}, "
                        "initial_orientation=initial_orientation)".format(
                            self.placement["rotation"]["rotation_vector"],
                            self.placement["rotation"]["up_vector"],
                            position_script
                        )
                    ])

            script_text.extend([
                "data['active_actions'][current_index]['target_orientation'] ="
                " target_orientation",
            ])
        # ...and now take care of object position
        if "position" in self.placement:
            script_text.extend([
                "W3D_LOG.debug("
                "'Starting position of {}: {}'.format("
                "blender_object.name, blender_object.position))",
            ])
            if (
                    self.move_relative and
                    self.placement['relative_to'] == 'Center'):
                script_text.extend([
                    "blender_object['linV'] = [",
                    "    coord/{} for coord in pos_vector]".format(
                        ("({}*bge.logic.getLogicTicRate())".format(
                            self.duration), 1)[self.duration == 0],
                    ),
                    "data['active_actions'][current_index]['target_pos'] = [",
                    "    blender_object.position[i] + pos_vector[i]",
                    "    for i in range(len(blender_object.position))]"
                ])
            else:
                script_text.extend([
                    "data['active_actions']["
                    "current_index]['target_pos']= [",
                    "    relative_object.position[i] + "
                    "pos_vector[i] for i in ",
                    "    range(len(relative_object.position))",
                    "]",
                    "delta_pos = [",
                    "    data['active_actions']["
                    "current_index]['target_pos'][i]"
                    " - blender_object.position[i]",
                    "    for i in range(len(blender_object.position))]",
                    "blender_object['linV'] = [",
                    "    coord/{} for coord in delta_pos]".format(
                        ("({}*bge.logic.getLogicTicRate())".format(
                            self.duration), 1)[self.duration == 0])]
                )
        try:
            script_text[0] = "{}{}".format(
                "    " * self.offset, script_text[0])
        except IndexError:
            return ""
        return "\n{}".format("    " * self.offset).join(script_text)

    @property
    def continue_string(self):
        script_text = []
        script_text.extend([
            "orientation = blender_object.orientation.to_quaternion()",
            "new_orientation = "
            "data['active_actions'][current_index]["
            "'initial_orientation'].slerp("
            "data['active_actions'][current_index]['target_orientation'],"
            " (1 - remaining_time/{duration}))".format(
                duration=self.duration),
            "blender_object.orientation = new_orientation"
        ])

        if "position" in self.placement:
            script_text.extend([
                "blender_object.position = [",
                "    blender_object.position[i] + blender_object['linV'][i]",
                "    for i in range(len(blender_object.position))]"]
            )

        try:
            script_text[0] = "{}{}".format(
                "    " * self.offset, script_text[0])
        except IndexError:
            return ""
        return "\n{}".format("    " * self.offset).join(script_text)

    @property
    def end_string(self):
        script_text = []
        script_text.extend([
            "blender_object.orientation ="
            " data['complete_actions'][current_index]["
            "'target_orientation']",
        ])

        if "position" in self.placement:
            script_text.extend([
                "blender_object.position = data['complete_actions']["
                "current_index]['target_pos']",
            ])

        try:
            script_text[0] = "{}{}".format(
                "    " * self.offset, script_text[0])
        except IndexError:
            return "{}pass".format("    " * self.offset)
        return "\n{}".format("    " * self.offset).join(script_text)

    def __init__(self, placement, duration, move_relative=False, offset=0):
        self.placement = placement
        self.duration = duration
        self.move_relative = move_relative
        self.offset = offset
