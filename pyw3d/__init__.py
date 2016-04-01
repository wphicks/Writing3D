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

"""A module for working with W3D Writing projects
"""
BLENDER_EXEC = "blender"  # BLENDEREXECSUBTAG
BLENDER_PLAY = "blenderplayer"  # BLENDERPLAYERSUBTAG

from . import project
from . import features
from . import objects
from . import timeline
from . import placement
from . import errors
from . import validators
from . import xml_tools
from . import ui
from . import structs
from . import path
from . import activators
from . import triggers
from . import actions
from . import groups

from .features import W3DFeature
from .project import W3DProject
from .objects import W3DObject, W3DLink, W3DContent, W3DText, W3DImage, \
    W3DStereoImage, W3DModel, W3DLight, W3DPSys
from .timeline import W3DTimeline
from .placement import W3DPlacement, W3DRotation
from .triggers import W3DTrigger, HeadTrackTrigger, HeadPositionTrigger, \
    LookAtPoint, LookAtDirection, LookAtObject, MovementTrigger, EventBox
from .actions import W3DAction, ObjectAction, GroupAction, SoundAction, \
    MoveVRAction, TimelineAction, EventTriggerAction, W3DResetAction
from .groups import W3DGroup
from .sounds import W3DSound
from .w3d_export_tools import export_to_blender

