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

"""Non-feature data structures used by Writing3D
"""
from collections import MutableSequence


class SortedList(MutableSequence):
    """A list that is guaranteed to remain sorted

    :param init_list: Initial list of elements (not necessarily sorted)
    :param sort_key: Key function for sorting"""
    def __init__(self, init_list=[], sort_key=None):
        self.sort_key = sort_key
        self._data = init_list[:]
        self.sort()

    def __setitem__(self, index, value):
        self._data.__setitem__(index, value)
        self.sort()

    def __delitem__(self, index):
        del self._data[index]

    def __len__(self):
        return len(self._data)

    def __getitem__(self, index):
        return self._data[index]

    def insert(self, index, new_item):
        self._data.insert(index, new_item)

    def add(self, new_item):
        """Add new_item to list, maintaining proper ordering"""
        for index, item in enumerate(self):
            if self.sort_key is None:
                if new_item < item:
                    self._data.insert(index, new_item)
                    return
            else:
                if self.sort_key(new_item) < self.sort_key(item):
                    self._data.insert(index, new_item)
                    return
        self._data.insert(len(self), new_item)

    def sort(self):
        self._data.sort(key=self.sort_key)

    def append(self, value):
        self.add(value)

    def extend(self, value_list):
        for value in value_list:
            self.add(value)

    def reverse(self):
        raise NotImplementedError("Cannot reverse a SortedList")
