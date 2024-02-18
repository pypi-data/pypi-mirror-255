##########################################################################
# Python library to help with the automatic creation of RTL              #
# Copyright (C) 2022, RISCY-Lib Contributors                                    #
#                                                                        #
# This program is free software: you can redistribute it and/or modify   #
# it under the terms of the GNU General Public License as published by   #
# the Free Software Foundation, either version 3 of the License, or      #
# (at your option) any later version.                                    #
#                                                                        #
# This program is distributed in the hope that it will be useful,        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of         #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
# GNU General Public License for more details.                           #
#                                                                        #
# You should have received a copy of the GNU General Public License      #
# along with this program.  If not, see <https://www.gnu.org/licenses/>. #
##########################################################################

import pytest
from rtlpy import utils


@pytest.mark.parametrize("val,expected", [
  ("test",              True),
  ("hello_world",       True),
  ("allrisc1024",       True),
  ("CAPS_SHOULD_WORK",  True),
  ("What About Spaces", False),
  ("Question_marks?",   False)
])
def test_valid_name(val, expected):
  assert utils.valid_name(val) is expected


@pytest.mark.parametrize("val,expected", [
  (10, 10),
  (0x69, 0x69),
  ("0x71", 0x71),
  ("x420", 0x420),
  ("8'h90", 0x90),
  ("7'd11", 11),
  ("'o72", int("72", base=8)),
  ("6'b101010", 42)
])
def test_val2int(val, expected):
  assert utils.val2int(val) == expected


@pytest.mark.parametrize("val,expected", [
  ("2 3\n15 16", ["2  3", "15 16"]),
  (["input wire test", "output reg val"], ["input  wire test", "output reg  val"])
])
def test_tabular_format(val, expected):
  assert utils.tabular_format(val) == expected
