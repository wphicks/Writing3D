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


# TODO: Handle moves relative to walls
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
            "W3D_LOG.debug('Starting movement in {}'.format(own.name))"
        ]
        # First take care of object rotation...
        if self.placement["rotation"]["rotation_mode"] != "None":

            vector = mathutils.Vector(
                self.placement["rotation"]["rotation_vector"])
            vector.normalize()
            if self.move_relative:
                if self.placement[
                        "rotation"]["rotation_mode"] == "Axis":
                    axis = mathutils.Vector(
                        self.placement["rotation"]["rotation_vector"])
                    axis.normalize()
                    angle = math.radians(
                        self.placement["rotation"]["rotation_angle"])
                    script_text.append(
                        "rotation = mathutils.Quaternion({}, {})".format(
                            tuple(vector), -angle))
                elif self.placement[
                        "rotation"]["rotation_mode"] == "Normal":
                    # TODO: Is this the legacy behavior?
                    script_text.extend([
                        "current_normal = mathutils.Vector((1, 0, 0))",
                        "rotation = mathutils.Vector(",
                        "    {}).rotation_difference(".format(
                            tuple(vector)),
                        "    current_normal)"]
                    )
                elif self.placement[
                        "rotation"]["rotation_mode"] == "LookAt":
                    script_text.extend([
                        "look_direction = (",
                        "    blender_object.position +",
                        "    mathutils.Vector({}) -".format(
                            self.placement["position"]),
                        "    mathutils.Vector({})).normalized()".format(
                            self.placement["rotation"]["rotation_vector"]),
                        "up_direction = mathutils.Vector(",
                        "    {}).normalized()".format(
                            self.placement["rotation"]["up_vector"]),
                        "rotation_matrix = mathutils.Matrix.Rotation("
                        "0, 4, (0, 0, 1))",
                        "frame_y = look_direction",
                        "frame_x = frame_y.cross(up_direction)",
                        "frame_z = frame_x.cross(frame_y)",
                        "rotation_matrix = mathutils.Matrix().to_3x3()",
                        "rotation_matrix.col[0] = frame_x",
                        "rotation_matrix.col[1] = frame_y",
                        "rotation_matrix.col[2] = frame_z",
                        "rotation = rotation_matrix.to_quaternion()"]
                    )
            else:  # Not move relative
                script_text.append(
                    "orientation ="
                    "blender_object.orientation.to_quaternion()")

                if self.placement[
                        "rotation"]["rotation_mode"] == "Axis":
                    angle = math.radians(
                        self.placement["rotation"]["rotation_angle"])
                    script_text.extend([
                        "target_orientation = mathutils.Quaternion(",
                        "    {}, {})".format(tuple(vector), -angle),
                        "rotation = (",
                        "    target_orientation.rotation_difference(",
                        "        orientation))"]
                    )

                elif self.placement[
                        "rotation"]["rotation_mode"] == "Normal":
                    script_text.extend([
                        "current_normal = mathutils.Vector((1, 0, 0))",
                        "current_normal.rotate(",
                        "    blender_object.orientation)",
                        "rotation = mathutils.Vector(",
                        "    {}).rotation_difference(".format(
                            tuple(vector)),
                        "    current_normal)"]
                    )

                elif self.placement[
                        "rotation"]["rotation_mode"] == "LookAt":
                    script_text.extend([
                        "look_direction = (",
                        "    mathutils.Vector({}) -".format(
                            self.placement["position"]),
                        "    mathutils.Vector({})).normalized()".format(
                            self.placement["rotation"]["rotation_vector"]),
                        "up_direction = mathutils.Vector(",
                        "    {}).normalized()".format(
                            self.placement["rotation"]["up_vector"]),
                        "rotation_matrix = mathutils.Matrix.Rotation("
                        "0, 4, (0, 0, 1))",
                        "frame_y = look_direction",
                        "frame_x = frame_y.cross(up_direction)",
                        "frame_z = frame_x.cross(frame_y)",
                        "rotation_matrix = mathutils.Matrix().to_3x3()",
                        "rotation_matrix.col[0] = frame_x",
                        "rotation_matrix.col[1] = frame_y",
                        "rotation_matrix.col[2] = frame_z",
                        "rotation = rotation_matrix.to_quaternion()"]
                    )

            script_text.extend([
                "blender_object['angV'] = (",
                "    rotation.angle /",
                "    {}".format(
                    ("({}*bge.logic.getLogicTicRate()) *".format(
                        self.duration), 1)[
                        self.duration == 0]),
                "    rotation.axis)"]
            )
        # ...and now take care of object position
        if "position" in self.placement:
            if self.move_relative:
                script_text.extend([
                    "blender_object['linV'] = [",
                    "    coord/{} for coord in {}]".format(
                        ("({}*bge.logic.getLogicTicRate())".format(
                            self.duration), 1)[self.duration == 0],
                        self.placement["position"]
                    )]
                )
            else:
                if self.placement["relative_to"] == "Center":
                    script_text.append(
                        "target_pos = {}".format(
                            list(self.placement["position"])
                        )
                    )
                else:
                    script_text.extend([
                        "relative_to = scene.objects['{}']".format(
                            generate_relative_to_name(
                                self.placement["relative_to"]
                            )
                        ),
                        "target_pos = [",
                        "    relative_to.position[i] + {}[i] for i in ".format(
                            list(self.placement["position"])),
                        "    range(len(relative_to.position))",
                        "]"
                    ])
                script_text.extend([
                    "delta_pos = [target_pos[i] - blender_object.position[i]",
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
        if self.placement["rotation"]["rotation_mode"] != "None":
            script_text.append(
                "delta_rot = blender_object['angV']"
            )
            script_text.append(
                "blender_object.applyRotation(delta_rot)")

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
        script_text = [
            "W3D_LOG.debug('Ending movement in {}'.format(own.name))"
        ]
        if not self.duration:
            if self.placement["rotation"]["rotation_mode"] != "None":
                script_text.append(
                    "delta_rot = blender_object['angV']"
                )
                script_text.append(
                    "blender_object.applyRotation(delta_rot)")

            if "position" in self.placement:
                script_text.extend([
                    "blender_object.position = [",
                    "    blender_object.position[i] +",
                    "    blender_object['linV'][i]",
                    "    for i in range(len(blender_object.position))]"]
                )

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
