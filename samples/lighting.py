#!/usr/bin/env blender
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

import os
from pyw3d import project, objects, placement, actions, export_to_blender

my_project = project.W3DProject(
    call_directory=os.path.dirname(__file__),
    allow_movement=True
)

my_object = objects.W3DObject(
    name="lit",
    color=(255, 255, 255),
    placement=placement.W3DPlacement(
        position=(0, 8, 1),
    ),
    content=objects.W3DText(
        text="This text is lit!"
    ),
    lighting=True
)
my_project["objects"].append(my_object)

my_object = objects.W3DObject(
    name="unlit",
    color=(255, 255, 255),
    placement=placement.W3DPlacement(
        position=(0, 8, -1),
    ),
    content=objects.W3DText(
        text="This text is not."
    ),
    lighting=False
)

my_project["objects"].append(my_object)

my_object = objects.W3DObject(
    name="monkey",
    color=(255, 255, 255),
    placement=placement.W3DPlacement(
        position=(-5, 8, 0),
    ),
    content=objects.W3DShape(
        shape_type="Monkey"
    ),
    lighting=False
)

my_project["objects"].append(my_object)

my_object = objects.W3DObject(
    name="monkey",
    color=(255, 255, 255),
    placement=placement.W3DPlacement(
        position=(5, 8, 0),
    ),
    content=objects.W3DShape(
        shape_type="Monkey"
    ),
    lighting=True
)

my_project["objects"].append(my_object)

my_object = objects.W3DObject(
    name="light",
    color=(0, 255, 0),
    placement=placement.W3DPlacement(
        position=(0, 0, 0),
    ),
    content=objects.W3DLight(
        light_type="Point",
    ),
    lighting=True
)

my_project["objects"].append(my_object)

my_object = objects.W3DObject(
    name="litmodel",
    placement=placement.W3DPlacement(
        position=(-10, 20, 0),
        rotation=placement.W3DRotation(
            rotation_mode="LookAt",
            rotation_vector=(0, 0, 0),
        )
    ),
    content=objects.W3DModel(
        filename="models/bathroom2.obj"
    ),
    lighting=True
)

my_project["objects"].append(my_object)

my_object = objects.W3DObject(
    name="unlitmodel",
    placement=placement.W3DPlacement(
        position=(10, 20, 0),
        rotation=placement.W3DRotation(
            rotation_mode="LookAt",
            rotation_vector=(0, 0, 0),
        )
    ),
    content=objects.W3DModel(
        filename="models/bathroom2.obj"
    ),
    lighting=False
)

my_project["objects"].append(my_object)
my_project["background"] = (140, 0, 140)

my_project["debug"] = True

export_to_blender(my_project, filename="lighting.blend", display=True)
