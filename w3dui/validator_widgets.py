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

"""Information on correspondences between validator and widget classes"""

from .base import ProjectInput, W3DValidatorInput
from .text import ProjectTextBlock, ProjectStringInput, ProjectFileInput, \
    ValidatedTextBlock, ValidatedStringInput, ValidatedFileInput
from .options import ProjectOptionInput, ReferenceInput, OptionInput
from .collections import ListInput, FixedListInput, SortedListInput, DictInput
from .numeric import ProjectNumericInput, ProjectIntInput, \
    ValidatedNumericInput, ValidatedIntInput
from .feature import FeatureInput


P_VAL_UI_DICT = {
    "Validator": ProjectInput,
    "TextValidator": ProjectTextBlock,
    "ValidPyString": ProjectStringInput,
    "ValidFile": ProjectFileInput,
    "OptionValidator": ProjectOptionInput,
    "ListValidator": ListInput,
    "SortedListValidator": SortedListInput,
    "ReferenceValidator": ReferenceInput,
    "IsBoolean": ProjectOptionInput,
    "IsNumeric": ProjectNumericInput,
    "IsInteger": ProjectIntInput,
    "FeatureValidator": FeatureInput,
    "DictValidator": DictInput,
    "FixedListAlt": FixedListInput
}

VAL_UI_DICT = {
    "Validator": W3DValidatorInput,
    "TextValidator": ValidatedTextBlock,
    "ValidPyString": ValidatedStringInput,
    "ValidFile": ValidatedFileInput,
    "OptionValidator": OptionInput,
    "IsBoolean": OptionInput,
    "IsNumeric": ValidatedNumericInput,
    "IsInteger": ValidatedIntInput,
}
