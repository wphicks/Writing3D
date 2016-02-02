#!/usr/bin/env python
from setuptools import setup

setup(
    name="Writing3D",
    version="0.0.1",
    author="William Hicks",
    author_email="william_hicks@alumni.brown.edu",
    description="A program for creating literary and artistic VR projects",
    license="GPL",
    keywords="virtual modeling art literature",
    url="https://github.com/wphicks/Writing3D",
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
)
