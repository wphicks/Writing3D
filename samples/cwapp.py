#!/usr/bin/env python3
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

"""An example showing how to use Writing3D as a replacement for the legacy
cwapp software

To run this script, use the following command::

    python3 cwapp.py desktopfull run.xml

where run.xml is a copy of your project in archival XML format.

It is possible to use this script as a drop-in replacement for cwapp with
CWEditor. In the "Run" menu of CWEditor, select "Configure Paths". Then, simply
browse to find this script in the resulting dialog.

You may also need to make this script executable on your platform. On
Unix-based systems, this can be done from terminal via::

    $ chmod u+x cwapp.py

"""

import argparse
import os
from pyw3d import project, export_to_blender

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "config", choices=["desktop", "desktopfull"], help="run configuration")
    parser.add_argument("project_file")
    args = parser.parse_args()

    # It's as simple as loading the project...
    my_project = project.W3DProject.fromXML_file(args.project_file)
    blend_filename = ".".join(
        os.path.splitext(args.project_file)[0],
        "blend"
    )
    # ...and exporting it!
    export_to_blender(
        my_project, filename=blend_filename, display=True,
        fullscreen=(args.config == "desktopfull")
    )
