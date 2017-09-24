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
import os
import json
import logging
import logging.handlers
import platform
import errno
LOGGER = logging.getLogger("pyw3d")
term_handler = logging.StreamHandler()
term_handler.setFormatter(
    logging.Formatter('%(asctime)-15s %(levelname)8s %(name)s %(message)s')
)
LOGGER.addHandler(term_handler)
LOGGER.setLevel(logging.WARNING)


class W3DConfigError(Exception):
    """Exception thrown when an error is detected in the configuration or
    installation of Writing3D
    """
    def __init__(self, message):
        super().__init__(message)


def executable_from_app(app_path):
    if os.path.splitext(app_path)[1].lower() == '.app':
        executable_name = os.path.splitext(os.path.basename(app_path))[0]
        return os.path.join(app_path, "Contents", "MacOS", executable_name)
    return app_path


W3D_CONFIG_FILENAME = os.path.join(
    os.path.expanduser("~"),
    '.w3d.json'
)
try:
    with open(W3D_CONFIG_FILENAME) as w3d_config_file:
        print("W3D Configuration loaded from {}".format(W3D_CONFIG_FILENAME))
        W3D_CONFIG = json.load(w3d_config_file)
except FileNotFoundError:
    print("No W3D config file found. Creating default...")
    base_path = os.path.dirname(__file__)
    base_path = os.path.abspath(
        os.path.join(base_path, os.path.pardir, os.path.pardir)
    )
    if platform.system() in ("Darwin",):
        W3D_CONFIG = {
            "Blender executable": os.path.join(
                base_path, "blender", "blender.app", "Contents", "MacOS",
                "blender"
            ),
            "Blender player executable": os.path.join(
                base_path, "blender", "blenderplayer.app", "Contents", "MacOS",
                "blenderplayer"
            ),
        }
    elif platform.system() in ("Windows", "cygwin"):
        W3D_CONFIG = {
            "Blender executable": os.path.join(
                base_path, "blender", "blender.exe"
            ),
            "Blender player executable": os.path.join(
                base_path, "blender", "blenderplayer.exe"
            ),
        }
    else:
        W3D_CONFIG = {
            "Blender executable": os.path.join(
                base_path, "blender", "blender"
            ),
            "Blender player executable": os.path.join(
                base_path, "blender", "blenderplayer"
            ),
        }
    with open(W3D_CONFIG_FILENAME, 'w') as w3d_config_file:
        json.dump(W3D_CONFIG, w3d_config_file)

BLENDER_EXEC = W3D_CONFIG["Blender executable"]
if BLENDER_EXEC != executable_from_app(BLENDER_EXEC):
    BLENDER_EXEC = executable_from_app(BLENDER_EXEC)
    W3D_CONFIG["Blender executable"] = BLENDER_EXEC
    with open(W3D_CONFIG_FILENAME, 'w') as w3d_config_file:
        json.dump(W3D_CONFIG, w3d_config_file)
BLENDER_PLAY = W3D_CONFIG["Blender player executable"]

try:
    WORKSPACE = W3D_CONFIG["Workspace"]
except KeyError:
    W3D_CONFIG["Workspace"] = os.path.join(
        os.path.expanduser("~"), "w3d_workspace"
    )
    with open(W3D_CONFIG_FILENAME, 'w') as w3d_config_file:
        json.dump(W3D_CONFIG, w3d_config_file)
    WORKSPACE = W3D_CONFIG["Workspace"]

LOG_DIR = os.path.join(WORKSPACE, "logs")
if not os.path.isdir(LOG_DIR):
    try:
        os.makedirs(LOG_DIR)
    except OSError as exc:
        if not (exc.errno == errno.EEXIST or os.path.isdir(LOG_DIR)):
            raise

LOG_FILE = os.path.join(LOG_DIR, "w3d_log.txt")


logfile_handler = logging.handlers.TimedRotatingFileHandler(
    LOG_FILE, when='midnight', backupCount=7
)
logfile_handler.setFormatter(
    logging.Formatter('%(asctime)-15s %(levelname)8s %(name)s %(message)s')
)
LOGGER.addHandler(logfile_handler)


if (
        BLENDER_EXEC != executable_from_app(BLENDER_EXEC) or
        BLENDER_PLAY != executable_from_app(BLENDER_PLAY)):
    BLENDER_EXEC = executable_from_app(BLENDER_EXEC)
    W3D_CONFIG["Blender executable"] = BLENDER_EXEC
    BLENDER_EXEC = executable_from_app(BLENDER_PLAY)
    W3D_CONFIG["Blender executable"] = BLENDER_PLAY
    with open(W3D_CONFIG_FILENAME, 'w') as w3d_config_file:
        json.dump(W3D_CONFIG, w3d_config_file)

from . import project
from . import features
from . import objects
from . import psys
from . import timeline
from . import placement
from . import errors
from . import validators
from . import xml_tools
from . import structs
from . import path
from . import activators
from . import triggers
from . import actions
from . import groups
from . import w3d_export_tools

from .features import W3DFeature
from .project import W3DProject
from .psys import W3DPAction, W3DPDomain
from .objects import W3DObject, W3DLink, W3DContent, W3DText, W3DImage, \
    W3DStereoImage, W3DModel, W3DLight, W3DShape, W3DPSys
from .psys import W3DPAction, W3DPDomain
from .timeline import W3DTimeline
from .placement import W3DPlacement, W3DRotation, convert_to_blender_axes, \
    convert_to_legacy_axes
from .triggers import W3DTrigger, HeadTrackTrigger, HeadPositionTrigger, \
    LookAtPoint, LookAtDirection, LookAtObject, MovementTrigger, EventBox
from .actions import W3DAction, ObjectAction, GroupAction, SoundAction, \
    MoveVRAction, TimelineAction, EventTriggerAction, W3DResetAction
from .groups import W3DGroup
from .sounds import W3DSound
from .w3d_export_tools import export_to_blender
