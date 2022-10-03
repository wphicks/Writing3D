#!/usr/bin/env python
import os
import sys
import platform
import urllib.request
import zipfile
import tarfile
import shutil
import bpy
import site

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
            os.pardir, os.pardir
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


def download_blender():
    cur_platform = get_platform()
    install_filename, headers = urllib.request.urlretrieve(
        DOWNLOAD_URLS[cur_platform]
    )
    if cur_platform == "Windows":
        zipfile.ZipFile(install_filename).extractall(path=INSTALL_PATH)
    elif cur_platform == "Mac":
        with tarfile.open(install_filename, "r:gz") as archive:
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner) 
                
            
            safe_extract(archive, path=INSTALL_PATH)
    else:
        with tarfile.open(install_filename, "r:bz2") as archive:
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner) 
                
            
            safe_extract(archive, path=INSTALL_PATH)


def update_blender():
    if REQUIRED_VERSION <= bpy.app.version:
        return
    print("Updating Blender...")
    download_blender()
    blend_dir = os.path.join(INSTALL_PATH, "blender")
    old_config = os.path.join(os.path.expanduser("~"), ".w3d.json")
    new_blend_dir = [
        os.path.join(INSTALL_PATH, file_) for file_ in os.listdir(INSTALL_PATH)
        if os.path.isdir(os.path.join(INSTALL_PATH, file_)) and
        file_.startswith("blender-{}.{}".format(*REQUIRED_VERSION[:-1]))
    ][0]
    if os.path.isdir(blend_dir):
        shutil.rmtree(blend_dir)
    if os.path.isfile(old_config):
        shutil.move(old_config, "{}.old".format(old_config))
    shutil.move(new_blend_dir, blend_dir)
    home_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.abspath(os.path.join(home_dir, os.pardir)))


def update_sitepath():
    w3d_path = os.path.abspath(
        os.path.normpath(
            os.path.join(
                os.path.dirname(__file__),
                os.pardir
            )
        )
    )

    all_sites = site.getsitepackages()
    for site_ in all_sites:
        if "site-packages" in os.path.split(site_)[1]:
            with open(os.path.join(site_, "Writing3D.pth"), "w") as pthfile:
                pthfile.write(w3d_path)


if __name__ == "__main__":
    update_blender()
    update_sitepath()
