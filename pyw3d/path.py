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

"""Classes for specifying options within W3DProject structure"""


class PathError(Exception):
    """Exception thrown when ProjectPath is used incorrectly"""
    def __init__(self, message):
        super(PathError, self).__init__(message)


class UnsetValueError(Exception):
    """Exception thrown when referencing object that has not been created"""
    def __init__(self, message):
        super(PathError, self).__init__(message)


class ProjectPath(object):
    """Specifies a location within W3DProject tree"""

    def insert_index_element(self, index, value):
        """Insert element in list and update indices in path"""
        self.get_element().insert(index, value)
        for i in range(index+1, len(self.get_element())):
            try:
                self.get_element()[i].project_path.set_specifier(i+1)
            except AttributeError:
                pass

    def remove_index_element(self, index):
        """Removes an element from a list within W3DProject tree"""
        del self.get_element()[index]
        for i in range(index, len(self.get_element())):
            try:
                self.get_element()[i].project_path.set_specifier(i-1)
            except AttributeError:
                pass

    def create_child_path(self, specifier):
        """Create a new path with given specifier appended"""
        new_path = [spec for spec in self.path]
        new_path.append(specifier)
        return ProjectPath(self.project, new_path)

    def get_element_parent(self):
        """Get the parent of the element specified by this path"""
        if not len(self.path):
            raise PathError("Element has no parent")
        element = self.project
        if element is None:
            raise UnsetValueError(
                "Project not set for this path")
        for i in range(len(self.path)-1):
            element = element[self.path[i]]
        return element

    def del_element(self):
        """Delete the element specified by this path"""
        parent = self.get_element_parent()
        del parent[self.path[-1]]

    def set_element(self, value):
        """Set the element specified by this path to given value"""
        parent = self.get_element_parent()
        parent[self.path[-1]] = value

    def get_element(self):
        """Return the value of the option specified by this path

        :raises UnsetValueError: If option value has not been created and has
        no default"""
        element = self.project
        if element is None:
            raise UnsetValueError(
                "Project not set for this path")
        for spec in self.path:
            try:
                element = element[spec]
            except (KeyError, IndexError):
                raise UnsetValueError(
                    "Element {} not yet set and has no default".format(spec)
                )
        return element

    def get_specifier(self):
        """Return the last element in path"""
        return self.path[-1]

    def set_specifier(self, new_specifier):
        """Set the last element in path to given value"""
        self.path[-1] = new_specifier

    def get_project(self):
        """Return the project this path is a part of"""
        return self.project

    def set_project(self, project):
        """Set path project to given value"""
        self.project = project

    def __init__(self, project=None, path=[]):
        self.project = project
        self.path = [spec for spec in path]
