#!/usr/bin/env python3
import sys

if sys.version_info[0] != 3:
    raw_input("ERROR: Must be run with Python 3.x. Press enter to exit.")
    raise RuntimeError("Incorrect Python version")

import os
import warnings
import fileinput
import platform
import shutil
import tarfile
import zipfile
import site
from urllib.request import urlopen
from distutils.core import setup
from distutils.core import Command
import distutils.command.install



def find_subdirectory(name, path):
    """Recursively search for directory of given name in path"""
    for root, dirs, files in os.walk(path):
        if name in dirs:
            return os.path.join(root, name)
    return None


def find_executable(name, path):
    """Recursively search for executable of given name in path"""
    for root, dirs, files in os.walk(path):
        if name in files:
            filename = os.path.join(root, name)
            if os.access(filename, os.X_OK):
                return filename
    return None


def _path_to_list(path):
    head, tail = os.path.split(path)
    if head and head != path:
        split_head = _path_to_list(head)
        split_head.append(tail)
        return split_head
    return [head or tail]


def path_to_list(path):
    """Split path into list of elements"""
    path = os.path.normpath(path)
    return _path_to_list(path)


class InstallError(Exception):
    """Exception thrown if install fatally fails"""
    def __init__(self, message):
        super(InvalidArgument, self).__init__(message)


class BlenderInstaller(object):
    """Class for installing Blender if necessary

    :param str install_directory: The directory where Writing3D is being
    installed"""

    blender_version = (2, 76)
    base_url = "http://download.blender.org/release/Blender{}.{}/".format(
        *blender_version)

    def message(self, string):
        """Print string if self.verbose"""
        if self.verbose:
            print(string)

    @property
    def executable_basename(self):
        """The basename of the blender executable"""
        exec_name = "blender"
        if self.platform in ("Windows",):
            exec_name = ".".join((exec_name, "exe"))
        return exec_name

    @property
    def player_basename(self):
        """The basename of the blenderplayer executable"""
        exec_name = "blenderplayer"
        if self.platform in ("Windows",):
            exec_name = ".".join((exec_name, "exe"))
        return exec_name

    @property
    def download_filename(self):
        """The name of the installation archive to download"""
        if self.platform == "Linux":
            return "blender-{}.{}-linux-glibc211-x86_64.tar.bz2".format(
                *self.blender_version)
        if self.platform == "Mac":
            return "blender-{}.{}-OSX_10.6-x86_64.zip".format(
                *self.blender_version)
        if self.platform == "Windows":
            if self._64_bit:
                return "blender-{}.{}-windows64.zip".format(
                    *self.blender_version)
            else:
                return "blender-{}.{}-windows64.zip".format(
                    *self.blender_version)

    @property
    def download_url(self):
        """The url from which to download Blender"""
        return "{}{}".format(self.base_url, self.download_filename)

    @property
    def archive_name(self):
        """The filename of the downloaded install archive"""
        return os.path.join(
            self.install_directory, self.download_filename)

    def _gather_platform_info(self):
        """Gather and store information about current platform"""
        self.message("Gathering system information...")
        self.platform = platform.system()
        if self.platform in ("Darwin",):
            self.platform = "Mac"
        if self.platform not in ("Linux", "Windows", "Mac"):
            self.platform = "Other"
        self.message("Detected platform: {}".format(self.platform))

        self._64_bit = sys.maxsize > 2**32
        self.message("64-bit system: {}".format(self._64_bit))

    def download(self):
        """Download Blender install archive to install directory"""
        self.message(
            "Downloading Blender from {}...".format(self.download_url))
        url_response = urlopen(self.download_url)
        with open(self.archive_name, 'wb') as download_file:
            chunk = url_response.read()
            download_file.write(chunk)

    def check_install(self):
        """Check if given Blender version has already been installed in
        self.install_directory

        Calls configure_blender_paths and returns True if both blender
        executable and blenderplayer executable are found. Sets
        self.blender_directory if install is found.

        Note that this method requires the default directory name for the
        Blender install."""

        # TODO: This should be made more robust by attempting to find the
        # Blender executable and then checking its version, rather than relying
        # on a default directory name.

        self.message("Checking for existing Blender install...")

        for root, dirs, files in os.walk(self.install_directory):
            finds = [dir_.startswith(
                "blender-{}.{}".format(*self.blender_version)) for dir_ in dirs
            ]
            if any(finds):
                for found, dir_ in zip(finds, dirs):
                    if found:
                        self.blender_directory = os.path.abspath(
                            os.path.join(root, dir_)
                        )
                        break
        self.configure_blender_paths()
        if self.blender_exec is not None and self.blender_play is not None:
            self.message("Found Blender install in {}".format(
                self.blender_directory)
            )
            return True
        self.blender_directory = None
        self.message("Blender install not found.")
        return False

    def install(self, force_install=False):
        """Install Blender, downloading if necessary
        
        Sets self.blender_directory to directory into which install archive is
        inflated
        
        :param bool force_install: Force clean installation even if previous
        install or cached installer archive is found"""

        if not force_install and self.check_install():
            return
        if os.path.isfile(self.archive_name) and not force_install:
            self.message("Installing from cached archive...")
        else:
            self.download()
        if self.platform in ("Linux", "Other"):
            with tarfile.open(self.archive_name, "r:bz2") as install_file:
                self.blender_directory = os.path.join(
                    self.install_directory, install_file.next().name)
                install_file.extractall(path=self.install_directory)
        else:
            with zipfile.ZipFile(self.archive_name) as install_file:
                self.blender_directory = os.path.join(
                    self.install_directory, install_file.namelist()[0])
                install_file.extractall(path=self.install_directory)
        self.configure_blender_paths()

    def configure_blender_paths(self):
        """Detects and stores several Blender-related paths

        Specific paths are:
            self.blender_site: the Blender Python site-packages directory,
            self.blender_modules: the Blender Python directory for storing
                addon modules
            self.blender_exec: the Blender executable
            self.blender_play: the blenderplayer executable"""
        self.blender_site = None
        self.blender_modules = None
        if self.blender_directory is None:
            self.message(
                "Cannot configure paths until Blender is installed!")
            return
        self.blender_site = find_subdirectory(
            "site-packages", self.blender_directory)
        self.blender_modules = find_subdirectory(
            "modules", find_subdirectory("addons", self.blender_directory)
        )
        self.blender_exec = find_executable(
            self.executable_basename, self.blender_directory)
        self.blender_play = find_executable(
            self.player_basename, self.blender_directory)

    def __init__(self, install_directory, verbose=False):
        self.verbose = verbose
        self.install_directory = os.path.abspath(install_directory)
        self.message("Installing to {}...".format(self.install_directory))
        self._gather_platform_info()
        self.blender_directory = None
        self.blender_exec = None
        self.blender_play = None


class CustomInstall(distutils.command.install.install):
    """Insert custom paths into source before installing

    This class is used to override the build command for setup.py, inserting
    paths to the blender and blenderplayer executables in pyw3d/__init__.py. In
    order to set these paths, modify setup.cfg as needed."""

    user_options = distutils.command.install.install.user_options + [
        ('w3dhome=', None, "home directory for Writing3D")
    ]

    def message(self, string):
        """Print string if self.verbose"""
        if self.verbose:
            print(string)

    def install_blender(self):
        """Install Blender if necessary"""
        self.blender_installer = BlenderInstaller(
            self.w3dhome, verbose=self.verbose)
        self.blender_installer.install()

    def copy_pkg_resources(self):
        """Copy the pkg_resources module to Blender module directory
        
        This is necessary to make scripts built into the Writing3D egg
        available to Blender"""
        import pkg_resources
        pkg_file = pkg_resources.__file__

        # For directory installs...
        if not os.path.basename(pkg_file).startswith("pkg_resources"):
            pkg_dir = os.path.dirname(pkg_file) 
            new_dir = os.path.join(
                self.blender_installer.blender_modules,
                os.path.basename(os.path.normpath(pkg_dir))
            )
            self.message("Copying {} to {}...".format(pkg_dir, new_dir))
            shutil.copytree(pkg_dir, new_dir)
        else:
            new_dir = self.blender_installer.blender_modules
            self.message("Copying {} to {}...".format(pkg_file, new_dir))
            shutil.copy(pkg_file, new_dir)

    def insert_paths(self):
        """Insert necessary paths into source"""
        for line in fileinput.input("pyw3d/__init__.py", inplace=1):
            if "BLENDEREXECSUBTAG" in line:
                print(
                    "BLENDER_EXEC = r'{}' # BLENDEREXECSUBTAG".format(
                        self.blender_installer.blender_exec)
                )
            elif "BLENDERPLAYSUBTAG" in line:
                print(
                    "BLENDER_PLAY = r'{}' # BLENDERPLAYERSUBTAG".format(
                        self.blender_installer.blender_play)
                )
            else:
                print(line, end="")

    def _setup_blender_paths(self):
        """Create sitecustomize.py path to make Writing3D available to Blender
        
        :warning: This will add the directory containing the Writing3D install
        to Blender as a site directory. This is not necessarily a good idea,
        since it may also make undesired packages that have been installed to
        the same directory available to Blender. At the moment, this seems to
        be the best solution that 1. Does not require the system Python version
        to match the Blender internal version 2. Does not involve wholesale
        copying of modules to the Blender site-packages directory, which may
        have unintended consequences. If you have a better solution,
        suggestions/ pull requests are very much welcome."""
        try:
            import pyw3d
        except ImportError:
            raise InstallError(
                "pyw3d module did not install successfully! Please contact the"
                " Writing3D maintainer"
            )

        pyw3d_path = path_to_list(pyw3d.__file__)
        package_path = []
        for elem in pyw3d_path:
            if os.path.splitext(elem)[1].lower() == ".egg":
                break
            package_path.append(elem)
        package_path = os.path.abspath(os.path.join(*package_path))

        for line in fileinput.input("sitecustomize.py", inplace=1):
            if "SYSSUBTAG" in line:
                print(
                    "site.addsitedir(r'{}') # SYSSUBTAG".format(
                        package_path)
                )
            else:
                print(line, end="")
        shutil.copy("sitecustomize.py", self.blender_installer.blender_site)

    def initialize_options(self, *args, **kwargs):
        self.w3dhome = None
        super().initialize_options(*args, **kwargs)

    def finalize_options(self, *args, **kwargs):
        if self.w3dhome is None:
            self.message("w3dhome not set. Using default.")
            self.w3dhome = os.path.expanduser(os.path.join("~", "Writing3D"))
        if not os.path.isdir(self.w3dhome):
            self.message("Creating {}".format(self.w3dhome))
            os.makedirs(self.w3dhome)
        self.message("Installing Writing3D interfaces in {}".format(
            self.w3dhome))
        super().finalize_options()

    def run(self, *args, **kwargs):
        self.install_blender()
        #self.copy_pkg_resources()
        self.insert_paths()
        self._setup_blender_paths()

setup(
    name="Writing3D",
    version="0.0.1",
    author="William Hicks",
    author_email="william_hicks@alumni.brown.edu",
    description="A program for creating literary and artistic VR projects",
    license="GPL",
    keywords="virtual modeling art literature",
    url="https://github.com/wphicks/Writing3D",
    scripts=[
        "pyw3d/w3d_export_tools.py", "samples/cwapp.py"],
    packages=[
        "pyw3d", "pyw3d.activators", "pyw3d.blender_actions",
        "pyw3d.w3d_logic", "pyw3d.activators.triggers"
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Artistic Software",
        "License :: OSI Approved :: GNU General Public License v3 or later"
        " (GPLv3+)"
    ],
    cmdclass={
        "install": CustomInstall
    },
)
