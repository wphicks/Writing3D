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

"""Metaclasses for use with W3D features
"""


class SubRegisteredClass(type):
    """Metaclass for keeping track of subclasses"""

    def __init__(cls, name, bases, attributes):
        if not hasattr(cls, "_subclass_registry"):
            cls._subclass_registry = {}
        else:
            cls._subclass_registry[name] = cls
        super(SubRegisteredClass, cls).__init__(name, bases, attributes)
