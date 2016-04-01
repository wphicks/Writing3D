#!/usr/bin/env python
import warnings
try:
    from setuptools import setup
    warnings.warn("setuptools not found. Using distutils for install")
except ImportError:
    from distutils import setup

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
        'w3d_writer.py', "pyw3d/w3d_export_tools.py"],
    packages=[
        "pyw3d", "pyw3d.activators", "pyw3d.blender_actions",
        "pyw3d.w3d_logic", "pyw3d.activators.triggers", "w3dui"
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Artistic Software",
        "License :: OSI Approved :: GNU General Public License v3 or later"
        " (GPLv3+)"
    ],
)
