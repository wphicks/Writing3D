#!/usr/bin/env python
import os
import platform
import urllib.request
import zipfile
import tarfile
import bpy

REQUIRED_VERSION = (2, 79, 0)

DOWNLOAD_URLS = {
    "Linux": "https://mirror.clarkson.edu/blender/release/Blender2.79/"
             "blender-2.79-linux-glibc219-x86_64.tar.bz2",
    "Mac": "https://mirror.clarkson.edu/blender/release/Blender2.79/"
           "blender-2.79-macOS-10.6.tar.gz",
    "Windows": "https://mirror.clarkson.edu/blender/release/Blender2.79/"
               "blender-2.79-windows64.zip"
}

INSTALL_PATH = os.path.abspath(
    os.path.normpath(
        os.path.join(
            os.path.dirname(__file__),
            os.pardir
        )
    )
)


def get_platform():
    if platform.system() in ("Darwin",):
        return "Mac"
    elif platform.system() in ("Windows", "cygwin"):
        return "Windows"
    else:
        return "Linux"


def update_blender():
    if REQUIRED_VERSION < bpy.app.version:
        return
    print("Updating Blender...")
    cur_platform = get_platform()
    install_filename, headers = urllib.request.urlretrieve(
        DOWNLOAD_URLS[cur_platform]
    )
    print("Download complete")
    if cur_platform == "Windows":
        zipfile.ZipFile(install_filename).extractall(path=INSTALL_PATH)
    elif cur_platform == "Mac":
        with tarfile.open(install_filename, "r:gz") as archive:
            archive.extractall(path=INSTALL_PATH)
    else:
        with tarfile.open(install_filename, "r:bz2") as archive:
            archive.extractall(path=INSTALL_PATH)


if __name__ == "__main__":
    update_blender()
