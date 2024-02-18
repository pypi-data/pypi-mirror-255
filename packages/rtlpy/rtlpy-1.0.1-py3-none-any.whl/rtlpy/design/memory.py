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

from typing import Optional, TypeVar, Type

from abc import ABC, abstractmethod

import logging

import dataclasses
from dataclasses import dataclass

from rtlpy.design import AccessType

import rtlpy.utils as utils


_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


##########################################################################
# Exception Definitions
##########################################################################
class MissingDefinitionException (Exception):
  """The Exception raised when converting using a dictionary that is missing a required field"""
  pass


##########################################################################
# TypeVar Definitions
##########################################################################
AddrBlockT = TypeVar('AddrBlockT', bound='_AddressBlockBase')


##########################################################################
# Component Definitions
##########################################################################
@dataclass
class Field:
  """Class which represents a Field within a Register for a MemoryMap"""

  name: str
  """Field name"""
  size: int = 1
  """Size of the field in bits"""
  access: AccessType = AccessType.READ_ONLY
  """Access Policy of the Field"""
  reset: int = 0
  """The reset value of the field"""
  volatile: bool = False
  """Whether the value of field is volatile"""
  randomizable: bool = True
  """Whether the field can be randomized"""
  reserved: bool = False
  """Whether the field is a reserved field"""

  def valid(self) -> bool:
    """Checks the Field is validly defined

    Returns:
        bool: Returns true if the Field is valid. False otherwise
    """
    ret_val = True

    if not utils.valid_name(self.name):
      _log.error(f"Field ({self.name}) has an invalid name.")
      ret_val = False
    if self.reset.bit_length() > self.size:
      _log.error(f"Field ({self.name}) reset value ({self.reset})" +
                 f" does not fit in field (size: {self.size}).")
      ret_val = False
    if self.randomizable and self.reserved:
      _log.warning(f"Field ({self.name}) cannot be randomizable and reserved.")
      ret_val = False

    return ret_val

  @staticmethod
  def from_dict(definition: dict) -> Field:
    """Converts the dictionary definition into a Field object.
    Requires the following keys: [name]
    Accepts the optional keys: [size, lsb_pos, access, reset, volatile, randomizable]

    Args:
        definition (dict): The definition of the field in dictionary form

    Raises:
        MissingDefinitionException: Raised when a required key is missing from the definition

    Returns:
        Field: The field derived from the definition
    """
    required_keys = ['name']

    for req_key in required_keys:
      if req_key not in definition:
        _log.error(f"Missing {req_key} key from dict during Field conversion")
        raise MissingDefinitionException(f"Missing {req_key} key from dict during Field conversion")

    fld = Field(definition['name'])

    if 'size' in definition:
      fld.size = definition['size']
    if 'access' in definition:
      fld.access = AccessType.from_string(definition['access'])
    if 'reset' in definition:
      fld.reset = definition['reset']
    if 'volatile' in definition:
      fld.volatile = definition['volatile']
    if 'randomizable' in definition:
      fld.randomizable = definition['randomizable']
    if 'reserved' in definition:
      fld.reserved = definition['reserved']

    return fld


@dataclass
class Register:
  """The class which represents a Register in a MemoryMap"""

  name: str
  """The name of the register"""
  coverage: str = "UVM_NO_COVERAGE"
  """The UVM Coverage type to apply in a RAL"""
  dimension: int = 1
  """The dimension of this register (the number of times it repeats in the Map)"""
  fields: dict[int, Field] = dataclasses.field(default_factory=dict)
  """A list of the fields in the register bank"""

  def randomizable(self) -> bool:
    """Determines if the register is randomizable. (Any of the fields are randomizable)

    Returns:
        bool: True if any field is randomizable, False otherwise
    """
    for _, f in self.fields.items():
      if f.randomizable:
        return True

    return False

  def add_field(self, fld: Field, lsb_pos: Optional[int] = None) -> bool:
    """Adds the field at the given lsb position

    Args:
        fld (Field): The field to add
        lsb_pos (int, optional): The lsb_position to insert. Defaults to None.
            When None, the field is inserted at the first valid lsb position

    Returns:
        bool: True if the field was successfully inserted. False otherwise
    """
    if lsb_pos is None:
      if len(self.fields.keys()) == 0:
        self.fields[0] = fld
      else:
        last_field_lsb = max(self.fields.keys())
        lsb_pos = self.fields[last_field_lsb].size + last_field_lsb
        self.fields[lsb_pos] = fld

      return True

    # Check if the field overlaps
    for lsb, f in self.fields.items():
      if lsb_pos in range(lsb, lsb + f.size):
        return False
      if lsb_pos + fld.size - 1 in range(lsb, lsb + f.size - 1):
        return False

    self.fields[lsb_pos] = fld

    return True

  def valid(self) -> bool:
    """Checks the Register is validly defined

    Raises:
        bool: Returns true if the Field is valid. False otherwise
    """
    ret_val = True

    if not utils.valid_name(self.name):
      _log.error(f"Register ({self.name}) has an invalid name.")
      ret_val = False

    if self.dimension < 1:
      _log.error(f"Register ({self.name}) has a dimension less than 1")
      ret_val = False

    return ret_val

  @staticmethod
  def from_dict(definition: dict) -> Register:
    """Converts the dictionary definition into a Register object.
    Requires the following keys: [name]
    Accepts the optional keys: [addr, coverage, fields]

    Args:
        definition (dict): The definition of the Register in dictionary form

    Raises:
        MissingDefinitionException: Raised when a required key is missing from the definition

    Returns:
        Register: The register derived from the definition
    """
    required_keys = ['name']

    for req_key in required_keys:
      if req_key not in definition:
        err = f"Missing {req_key} key from dict during Register conversion"
        _log.error(err)
        raise MissingDefinitionException(err)

    reg = Register(definition['name'])

    if 'dimension' in definition:
      reg.dimension = definition['dimension']

    if 'coverage' in definition:
      reg.coverage = definition['coverage']

    if 'fields' in definition:
      for field in definition['fields']:
        lsb_pos = None if "lsb_pos" not in field else field['lsb_pos']

        reg.add_field(Field.from_dict(field), lsb_pos)

    reg.valid()

    return reg


@dataclass
class _AddressBlockBase(ABC):
  """Abstract Base for implementation details which are shared between address blocks"""

  name: str
  """The name of the Address block"""
  addr_size: int
  """The number of address bits in the block"""
  data_size: int
  """The number of data bits in the block"""
  base_address: int = 0
  """The base address for this address block"""
  dimension: int = 1
  """The dimension of this AddressBlock (the number of times it repeats in the top block)"""
  endianness: str = "little"
  """The endianness of the address space ('little' or 'big')"""
  coverage: str = "UVM_NO_COVERAGE"
  """The UVM built-in coverage for the address block"""
  registers: dict[int, Register] = dataclasses.field(default_factory=dict)
  """A dict of the Registers in the AddressBlock, indexed by offset"""
  sub_blocks: dict[int, AddressBlock] = dataclasses.field(default_factory=dict)
  """A dict of address sub-blocks, indexed by base_address"""

  def randomizable(self) -> bool:
    """Determines if the AddressBlock is randomizable. (Any of the registers
     or sub-blocks are randomizable)

    Returns:
        bool: True if any register or sub-block is randomizable, False otherwise
    """
    for _, r in self.registers.items():
      if r.randomizable():
        return True

    for _, b in self.sub_blocks.items():
      if b.randomizable():
        return True

    return False

  def data_bytes(self) -> int:
    """Determines the size of the data field in bytes

    Returns:
        int: The number of bytes the data field is
    """
    return int(self.data_size / 8)

  @abstractmethod
  def size(self) -> int:
    """Determines the number of bytes which the AddressBlock takes up.
    Assumes all space is full and block interleaving is not permitted

    Returns:
        int: The number of bytes in the address block
    """
    pass

  def valid(self) -> bool:
    """Checks the AddressBlock is validly defined

    Raises:
        bool: Returns true if the Field is valid. False otherwise
    """
    ret_val = True

    if not utils.valid_name(self.name):
      _log.error(f"AddressBlock ({self.name}) has an invalid name.")
      ret_val = False

    return ret_val

  @abstractmethod
  def add_register(self, reg: Register, offset: Optional[int] = None) -> bool:
    """Adds the register at the given offset.
    If the offset is None, then add at first valid position

    Args:
        reg (Register): The register to add
        offset (int, optional): The offset of the register. Defaults to None.
            When None, the field is inserted at the first valid offset position

    Returns:
        bool: True if the register was successfully added
    """
    pass

  @abstractmethod
  def add_subblock(self, blk: AddressBlock, offset: Optional[int] = None) -> bool:
    """Adds the sub-block at the given offset.
    If the offset is None, then add at first valid position

    Args:
        blk (AddressBlock): The sub-block to add
        offset (Optional[int], optional): The offset of the sub-block. Defaults to None.
            When None, the sub-block is inserted at the first valid offset position

    Returns:
        bool: True if the sub-block was successfully added
    """
    pass

  @classmethod
  def _check_required_dict_keys(cls, definition: dict) -> None:
    required_keys = ['name', 'addr_size', 'data_size']

    for req_key in required_keys:
      if req_key not in definition:
        err = f"Missing {req_key} key from dict during {type(cls)} conversion"
        _log.error(err)
        raise MissingDefinitionException(err)

  @classmethod
  def _set_optional_dict_keys(cls, definition: dict, blk: _AddressBlockBase) -> None:
    if 'base_address' in definition:
      blk.base_address = definition['base_address']

    if 'dimension' in definition:
      blk.dimension = definition['dimension']

    if 'endianness' in definition:
      blk.coverage = definition['endianness']

    if 'coverage' in definition:
      blk.coverage = definition['coverage']

  @classmethod
  @abstractmethod
  def _registers_from_dict(cls, definition: dict, blk: _AddressBlockBase) -> None:
    """Performs the register parsing from a dictionary definition for the parent class
    'from_dict' method.

    Args:
        definition (dict): The definition to derive from
        blk (AddressBlock): The parent block to add too
    """
    pass

  @classmethod
  @abstractmethod
  def _sub_blocks_from_dict(cls, definition: dict, blk: _AddressBlockBase) -> None:
    """Performs the sub-block parsing from a dictionary definition for the parent class
    'from_dict' method.

    Args:
        definition (dict): The definition to derive from
        blk (AddressBlock): The parent block to add too
    """
    pass

  @classmethod
  def from_dict(cls: Type[AddrBlockT], definition: dict) -> AddrBlockT:
    """Converts the dictionary definition into an AddressBlock object.
    Requires the following keys: [name, addr_size, data_size]
    Accepts the optional keys:
    [base_address, dimension, endianness, coverage, registers, sub_blocks]

    Args:
        definition (dict): The definition of the Register in dictionary form

    Raises:
        MissingDefinitionException: Raised when a required key is missing from the definition

    Returns:
        AddressBlock: The address block derived from the definition
    """
    cls._check_required_dict_keys(definition)

    blk = cls(definition['name'], definition['addr_size'], definition['data_size'])

    cls._set_optional_dict_keys(definition, blk)

    if 'registers' in definition:
      cls._registers_from_dict(definition, blk)

    if 'sub_blocks' in definition:
      cls._sub_blocks_from_dict(definition, blk)

    blk.valid()

    return blk


@dataclass
class AddressBlock(_AddressBlockBase):
  """An AddressBlock in a MemoryMap which represents a collection of registers"""

  def size(self) -> int:
    high_reg_offset = 0 if len(self.registers) == 0 else max(self.registers.keys())
    high_block_offset = 0 if len(self.sub_blocks) == 0 else max(self.sub_blocks.keys())
    if high_reg_offset > high_block_offset:
      return int(high_reg_offset + (self.registers[high_reg_offset].dimension *
                                    self.data_size / 8))
    else:
      return int(high_block_offset + (self.sub_blocks[high_block_offset].dimension *
                                      self.sub_blocks[high_block_offset].size()))

  def valid(self) -> bool:
    ret_val = super().valid()

    if self.base_address < 0:
      _log.error(f"AddressBlock ({self.name}) has a base address less than 0")
      ret_val = False

    if self.dimension < 1:
      _log.error(f"AddressBlock ({self.name}) has a dimension less than 1")
      ret_val = False

    if self.endianness.lower() not in ['little', 'big']:
      _log.error(f"AddressBlock ({self.name}) has invalid endianness ({self.endianness})")
      ret_val = False

    return ret_val

  def _find_address_space(self, size: int, word_aligned: bool = True) -> int:
    """Finds the first block of address space which has at-least a given number of contiguous
    free bytes.

    Args:
        size (int): The number of bytes the block must have
        word_aligned (bool): If the block must be word aligned (based on the data_size).
          Defaults to True.

    Returns:
        int: The offset of the first block of address space which fits the data.
    """
    addr_space: dict[int, Register | AddressBlock] = {}
    for offset, reg in self.registers.items():
      addr_space[offset] = reg
    for offset, blk in self.sub_blocks.items():
      addr_space[offset] = blk

    last_offset = 0
    for offset in sorted(addr_space.keys()):
      if last_offset + size <= offset:
        return last_offset

      mem_obj = addr_space[offset]
      if isinstance(addr_space[offset], Register):

        last_offset = offset + int(self.data_size / 8)
      elif isinstance(mem_obj, AddressBlock):
        last_offset = offset + mem_obj.size()

    return last_offset

  def _check_address_space(self, size: int, offset: int) -> bool:
    """Checks the given offset in the address space has free space greater than
    or equal to the size provided.

    Args:
        size (int): The size of the address space to check
        offset (int): The offset in the address space to check

    Returns:
        bool: True if the address space is free, False otherwise
    """
    start_addr = offset
    end_addr = offset + size

    # First check the registers for overlap
    for reg_addr in self.registers.keys():
      if len([addr for addr in range(reg_addr, reg_addr + int(self.data_size / 8))
              if addr in range(start_addr, end_addr)]):
        return False

    # Then check the sub-blocks for overlap
    for blk_addr, blk in self.sub_blocks.items():
      if len([addr for addr in range(blk_addr, blk_addr + blk.size())
              if addr in range(start_addr, end_addr)]):
        return False

    return True

  def add_register(self, reg: Register, offset: Optional[int] = None) -> bool:
    if offset is None:
      offset = self._find_address_space(int(self.data_size / 8))
      self.registers[offset] = reg
      return True
    elif self._check_address_space(int(self.data_size / 8), offset):
      self.registers[offset] = reg
      return True

    return False

  def add_subblock(self, blk: AddressBlock, offset: Optional[int] = None) -> bool:
    if offset is None:
      offset = self._find_address_space(blk.size())
      self.sub_blocks[offset] = blk
      return True
    elif self._check_address_space(blk.size(), offset):
      self.sub_blocks[offset] = blk
      return True

    return False

  @classmethod
  def _sub_blocks_from_dict(cls, definition: dict, blk: _AddressBlockBase) -> None:
    inherited_keys = ['addr_size', 'data_size', 'endianness', 'coverage']

    for subblk in definition['sub_blocks']:
      for k in inherited_keys:
        if k not in subblk and k in definition:
          subblk[k] = definition[k]

      offset = None if "base_address" not in subblk else subblk["base_address"]
      blk.add_subblock(AddressBlock.from_dict(subblk), offset)

  @classmethod
  def _registers_from_dict(cls, definition: dict, blk: _AddressBlockBase) -> None:
    for reg in definition['registers']:
        offset = None if "offset" not in reg else reg['offset']

        if "coverage" not in reg and "coverage" in definition:
          reg["coverage"] = definition["coverage"]

        blk.add_register(Register.from_dict(reg), offset)


class PagedAddressBlock(_AddressBlockBase):
  """An address block, where all the sub-blocks are paged so they start with a zero
  offset, but can only be accessed through a 'page' register which sets the page index."""

  page_reg: Register | None = None
  """The reference to the register used as the page_reg"""
  page_reg_offset: int = -1
  """The page register offset in the register bank"""

  def size(self) -> int:
    high_bytes = []
    for offset, reg in self.registers.items():
      high_bytes.append(offset + (reg.dimension * self.data_bytes()))
    for _, blk in self.sub_blocks.items():
      high_bytes.append(blk.base_address + blk.size())

    return max(high_bytes)

  def add_register(self, reg: Register, offset: Optional[int] = None) -> bool:
    raise NotImplementedError()

  def _check_address_space(self, size: int, offset: int) -> bool:
    """Checks the given offset in the address space has free space greater than
    or equal to the size provided. Only checks against registers since sub-blocks
    are mutually exclusive

    Args:
        size (int): The size of the address space to check
        offset (int): The offset in the address space to check

    Returns:
        bool: True if the address space is free, False otherwise
    """
    upper_bound = size + offset - 1
    for reg_offset, reg in self.registers.items():
      if (upper_bound >= reg_offset + self.data_bytes() - 1) and \
         (offset <= reg_offset + self.data_bytes() - 1):
        return False
      if (upper_bound >= reg_offset) and (offset <= reg_offset):
        return False

    return True

  def add_subblock(self, blk: AddressBlock, offset: Optional[int] = None) -> bool:
    if not self._check_address_space(blk.size(), blk.base_address):
      _log.warning(f"Can't add sub-block ({blk.name}) to paged block ({self.name})." +
                   f" {blk.name} overlaps with existing registers.")
      return False

    if offset is None:
      for i in range(0, 2**(self.data_size)):
        if i not in self.sub_blocks:
          self.sub_blocks[i] = blk
          return True
      _log.warning(f"Can't add sub-block ({blk.name}) to paged block ({self.name})." +
                   f" Maximum number of pages ({2**self.data_size}) reached.")
      return False

    if offset in self.sub_blocks:
      _log.warning(f"Can't add sub-block ({blk.name}) to paged block ({self.name})." +
                   f" {blk.name} overlaps with existing sub-block.")
      return False

    self.sub_blocks[offset] = blk
    return True

  @classmethod
  def from_dict(cls, definition: dict) -> PagedAddressBlock:
    # TODO: Move required keys checking
    required_keys = ['name', 'addr_size', 'data_size', 'page_reg']

    for req_key in required_keys:
      if req_key not in definition:
        err = f"Missing {req_key} key from dict during AddressBlock conversion"
        _log.error(err)
        raise MissingDefinitionException(err)

    blk = super(PagedAddressBlock, cls).from_dict(definition)

    if "offset" not in definition['page_reg']:
      err = f"Missing required offset of page reg during {type(cls)} conversion"
      _log.error(err)
      raise MissingDefinitionException(err)

    blk.page_reg_offset = definition['page_reg']['offset']

    if "coverage" not in definition['page_reg'] and "coverage" in definition:
      definition['page_reg']["coverage"] = definition["coverage"]

    blk.page_reg = Register.from_dict(definition['page_reg'])

    return blk

  @classmethod
  def _registers_from_dict(cls, definition: dict, blk: _AddressBlockBase) -> None:
    raise NotImplementedError()

  @classmethod
  def _sub_blocks_from_dict(cls, definition: dict, blk: _AddressBlockBase) -> None:
    inherited_keys = ['addr_size', 'data_size', 'endianness', 'coverage', 'base_address']

    for subblk in definition['sub_blocks']:
      for k in inherited_keys:
        if k not in subblk and k in definition:
          subblk[k] = definition[k]

      offset = None if "page" not in subblk else subblk["page"]
      blk.add_subblock(AddressBlock.from_dict(subblk), offset)


##########################################################################
# From Dict Methods
##########################################################################
def memory_from_dict(definition: dict) -> Field | Register | AddressBlock:
  raise NotImplementedError("memory_from_dict not implemented")
