#!/usr/bin/env python3

import urllib.request
import os
import zipfile
import subprocess
import sys
import pyw3d


def update_dulwich():
    try:
        import dulwich
    except ImportError:
        install_dulwich()


def install_distutils():
    subprocess.call(
        [
            pyw3d.BLENDER_EXEC, "--background", "--python",
            os.path.join(os.path.dirname(__file__), "ez_setup.py")
        ]
    )


def install_pip():
    try:
        import pip
    except ImportError:
        pip_filename, headers = urllib.request.urlretrieve(
            "https://bootstrap.pypa.io/get-pip.py"
        )
        subprocess.call(
            [pyw3d.BLENDER_EXEC, "--background", "--python", pip_filename]
        )


def install_dulwich():
    install_path = os.path.abspath(
        os.path.normpath(
            os.path.join(
                os.path.dirname(__file__),
                os.pardir
            )
        )
    )
    os.chdir(install_path)

    if not os.path.isdir("dulwich-master"):
        dulwich_filename, headers = urllib.request.urlretrieve(
            "https://github.com/jelmer/dulwich/archive/master.zip"
        )
        dulwich_zip = zipfile.ZipFile(dulwich_filename)
        dulwich_zip.extractall()

    subprocess.call(
        [
            pyw3d.BLENDER_EXEC, "--background", "--python",
            os.path.join("dulwich-master", "setup.py"), "--", "--pure", "install"
        ]
    )

update_dulwich()
#try:
#    import dulwich
#except ImportError:
#    raise ImportError("Dulwich could not be found or installed")
