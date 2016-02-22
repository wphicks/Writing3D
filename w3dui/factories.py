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

"""Factories for creating modified versions of TK input widgets"""

from .base import InputUI, W3DValidatorInput


def ValidatedWidget(
        base_widget, replacements={}):
    """Create a version of a base input widget with W3D-style validation

    :param class base_widget: A widget inheriting from InputUI
    :param dict replacements: A dictionary mapping classes to validated
    replacement classes"""
    if InputUI not in replacements:
        replacements[InputUI] = W3DValidatorInput
    old_base_classes = base_widget.__bases__
    new_base_classes = tuple(
        [
            (base, replacements[base])[base in replacements] for base in
            old_base_classes
        ]
    )
    return type(
        "".join(("Validated", base_widget.__name__)),
        new_base_classes,
        dict(base_widget.__dict__)
    )
