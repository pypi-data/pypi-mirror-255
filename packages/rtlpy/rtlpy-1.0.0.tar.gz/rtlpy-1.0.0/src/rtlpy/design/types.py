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

from __future__ import annotations
from enum import Enum


class AccessType (Enum):
  """Type to represent Memory Access-Types"""

  READ_ONLY = "RO"
  """W: no effect, R: no effect\n
  -- SRAM Implementation: input value signal"""
  READ_WRITE = "RW"
  """W: as-is, R: no effect\n
  -- SRAM Implementation: output value signal"""
  READ_CLEARS = "RC"
  """W: no effect, R: clears all bits\n
  -- SRAM Implementation: input latch set signal, output value signal"""
  READ_SETS = "RS"
  """W: no effect, R: sets all bits\n
  -- SRAM Implementation: input latch clear signal, output value signal"""
  WRITE_READ_CLEARS = "WRC"
  """W: as-is, R: clears all bits\n
  -- SRAM Implementation: output value signal"""
  WRITE_READ_SETS = "WRS"
  """W: as-is, R: sets all bits\n
  -- SRAM Implementation: output value signal"""
  WRITE_CLEARS = "WC"
  """W: clears all bits, R: no effect\n
  -- SRAM Implementation: input latch set signal, output value signal"""
  WRITE_SETS = "WS"
  """W: sets all bits, R: no effect\n
  -- SRAM Implementation: input latch clear signal, output value signal"""
  WRITE_SETS_READ_CLEARS = "WSRC"
  """W: sets all bits, R: clears all bits\n
  -- SRAM Implementation: output value signal"""
  WRITE_CLEARS_READ_SETS = "WCRS"
  """W: clears all bits, R: sets all bits\n
  -- SRAM Implementation: output value signal"""
  WRITE_ONE_CLEARS = "W1C"
  """W: 1/0 clears/no effect on matching bit, R: no effect\n
  -- SRAM Implementation: input latch set signal, output value signal"""
  WRITE_ONE_SETS = "W1S"
  """W: 1/0 sets/no effect on matching bit, R: no effect\n
  -- SRAM Implementation: input latch clear signal, output value signal"""
  WRITE_ONE_TOGGLES = "W1T"
  """W: 1/0 toggles/no effect on matching bit, R: no effect\n
  -- SRAM Implementation: output value signal"""
  WRITE_ZERO_CLEARS = "W0C"
  """W: 1/0 no effect on/clears matching bit, R: no effect\n
  -- SRAM Implementation: input latch set signal, output value signal"""
  WRITE_ZERO_SETS = "W0S"
  """W: 1/0 no effect on/sets matching bit, R: no effect\n
  -- SRAM Implementation: input latch clear signal, output value signal"""
  WRITE_ZERO_TOGGLES = "W0T"
  """W: 1/0 no effect on/toggles matching bit, R: no effect\n
  -- SRAM Implementation: output value signal"""
  WRITE_ONE_SETS_READ_CLEARS = "W1SRC"
  """W: 1/0 sets/no effect on matching bit, R: clears all bits\n
  -- SRAM Implementation: output value signal"""
  WRITE_ONE_CLEARS_READ_SETS = "W1CRS"
  """W: 1/0 clears/no effect on matching bit, R: sets all bits\n
  -- SRAM Implementation: output value signal"""
  WRITE_ZERO_SETS_READ_CLEARS = "W0SRC"
  """W: 1/0 no effect on/sets matching bit, R: clears all bits\n
  -- SRAM Implementation: output value signal"""
  WRITE_ZERO_CLEARS_READ_SETS = "W0CRS"
  """W: 1/0 no effect on/clears matching bit, R: sets all bits\n
  -- SRAM Implementation: output value signal"""
  WRITE_ONLY = "WO"
  """W: as-is, R: error\n
  -- SRAM Implementation: output value signal"""
  WRITE_ONLY_CLEARS = "WOC"
  """W: clears all bits, R: error\n
  -- SRAM Implementation: input latch set signal, output value signal"""
  WRITE_ONLY_SETS = "WOS"
  """W: sets all bits, R: error\n
  -- SRAM Implementation: input latch clear signal, output value signal"""
  WRITE_ONE = "W1"
  """W: first one after HARD reset is as-is, other W have no effects, R: no effect\n
  -- SRAM Implementation: output value signal"""
  WRITE_ONLY_ONE = "WO1"
  """W: first one after HARD reset is as-is, other W have no effects, R: error\n
  -- SRAM Implementation: output value signal"""

  @classmethod
  def from_string(cls, label: str) -> AccessType:
    format_label = label.replace(" ", "_").upper()

    for access in cls:
      if (format_label == access.name):
        return access
      elif (format_label == access.value):
        return access
    raise KeyError(label)

  @classmethod
  def is_readable(cls, access: AccessType) -> bool:
    """Returns true if the access type is considered "readable".
    An access type is considered "readable" iff a read transaction does not result in an error

    Args:
        access (AccessType): The access type to check

    Returns:
        bool: True if readable, else false
    """
    if access in [cls.WRITE_ONLY, cls.WRITE_ONLY_CLEARS, cls.WRITE_ONLY_SETS, cls.WRITE_ONLY_ONE]:
      return False
    return True

  @classmethod
  def is_writable(cls, access: AccessType) -> bool:
    """Returns true if the access type is considered "writable".
    An access type is considered "writable" iff a write transaction has an impact on state

    Args:
        accces (AccessType): The access type to check

    Returns:
        bool: True if writable, else False
    """
    if access in [cls.READ_ONLY, cls.READ_CLEARS, cls.READ_SETS]:
      return False
    return True


class PortDirection(Enum):
  """Type to represent Port Direction Types"""

  OUTPUT = "OUT"
  INPUT = "IN"
  INOUT = "INOUT"

  @classmethod
  def from_string(cls, label: str) -> PortDirection:
    format_label = label.replace(" ", "_").upper()
    for access in cls:
      if (format_label == access.name):
        return access
      elif (format_label == access.value):
        return access
    raise KeyError(label)


class SignalType(Enum):
  """Type to represent signal type"""

  WIRE = "WIRE"
  REG = "REG"
  LOGIC = "LOGIC"
  REAL = "REAL"
  WREAL = "WREAL"
  WREAL4 = "WREAL4STATE"
  UWIRE = "UWIRE"

  @classmethod
  def from_string(cls, label: str) -> SignalType:
    format_label = label.replace(" ", "_").upper()
    for access in cls:
      if (format_label == access.name):
        return access
      elif (format_label == access.value):
        return access
    raise KeyError(label)


class ParamType(Enum):
  """Type to represent a parameter type"""

  NONE = "NONE"
  INTEGER = "INT"
  STRING = "STRING"

  @classmethod
  def from_string(cls, label: str) -> ParamType:
    format_label = label.replace(" ", "_").upper()
    for access in cls:
      if (format_label == access.name):
        return access
      elif (format_label == access.value):
        return access
    raise KeyError(label)
