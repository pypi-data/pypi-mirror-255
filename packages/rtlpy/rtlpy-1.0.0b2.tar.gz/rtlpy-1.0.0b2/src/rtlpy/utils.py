##########################################################################
# Python library to help with the automatic creation of RTL              #
# Copyright (C) 2022, RISCY-Lib Contributors                              #
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

from __future__ import annotations

import re
from typing import Any


def valid_name(name: str) -> bool:
  """Checks the name is valid for use in RTL.
  (i.e. contains only letters, numbers, and underscores)

  Args:
      name (str): The string to check

  Returns:
      bool: True if the name is valid, False otherwise
  """
  pattern = re.compile(r'[^A-z0-9_]')
  return not bool(pattern.search(name))


def name_validator(self: Any, attribute: Any, val: Any) -> None:
  if not valid_name(val):
    raise ValueError(f"Invalid Name Value {val}")


def val2int(val: Any) -> int:
  """Converts a value to an integer.
  If the value is a string then it converts it from 0x/x format or
  SystemVerilog formats to integers.
  Otherwise the function just returns int(val)

  Args:
      val (Any): The value to convert to the int

  Returns:
      int: The integer from the value
  """
  if not isinstance(val, str):
    return int(val)

  val = val.lower()

  if val[0:2] == "0x":
    return int(val[2:], base=16)
  if val[0] == "x":
    return int(val[1:], base=16)

  if "'h" in val:
    return int(val[val.find("'h")+2:], base=16)
  if "'d" in val:
    return int(val[val.find("'d")+2:], base=10)
  if "'o" in val:
    return int(val[val.find("'o")+2:], base=8)
  if "'b" in val:
    return int(val[val.find("'b")+2:], base=2)

  return int(val)


def tabular_format(lines: list[str] | str) -> list[str]:
  """Converts the provided lines or string to a tabularly formatted string.
  This is a string where the start of each word is aligned

  Args:
      lines (list[str] | str): List of strings where each string is a line,
          or a string which contains the full unformatted table

  Returns:
      list[str]: The tabularly formatted string. Each string does not have leading
          or trailing whitespace or newline characters
  """
  if isinstance(lines, str):
    lines = lines.split("\n")

  table = []
  for line in lines:
    table.append(line.split())

  col_len = [0] * max([len(row) for row in table])
  for row in table:
    for idx, cell in enumerate(row):
      col_len[idx] = max(col_len[idx], len(cell))

  ret_val = []
  for row in table:
    line = ""
    for idx, cell in enumerate(row):
      line += f"{cell: <{col_len[idx]}} "
    ret_val.append(line.strip())

  return ret_val
