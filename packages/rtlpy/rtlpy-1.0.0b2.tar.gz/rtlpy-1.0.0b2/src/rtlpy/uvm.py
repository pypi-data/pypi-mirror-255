##########################################################################
# Python library to help with the automatic creation of RTL              #
# Copyright (C) 2022, RISCY-Lib Contributors                             #
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

from jinja2 import Environment, PackageLoader

from rtlpy.design.memory import Register, AddressBlock, PagedAddressBlock, _AddressBlockBase


def addrblock_to_ral(ablock: _AddressBlockBase,
                     predictor_type: str = "uvm_reg_predictor#(uvm_sequence_item)") -> str:
  """Convert the provided AddressBlock and all sub-components to UVM registers and blocks.

  Args:
      ablock (AddressBlock): The address block to create the UVM hierarchy from
      predictor_type (str): The UVM predictor to use when creating a paged address block

  Returns:
      str: The string version of the generated RAL
  """
  env = Environment(
    loader=PackageLoader("rtlpy", "_uvm_templates"),
    lstrip_blocks=True,
    trim_blocks=True
  )

  ral_str = ""

  for _, reg in ablock.registers.items():
    ral_str += reg_to_ral(reg, ablock.data_size) + "\n\n"

  for _, subblk in ablock.sub_blocks.items():
    ral_str += addrblock_to_ral(subblk) + "\n\n"

  if isinstance(ablock, AddressBlock):
    template = env.get_template("uvm_reg_block.jinja")
  elif isinstance(ablock, PagedAddressBlock):
    if ablock.page_reg is None:
      raise TypeError(f"addrblock_to_ral has ablock which is {type(ablock)}" +
                      "has a page_reg which is not sent")

    ral_str += reg_to_ral(ablock.page_reg, ablock.data_size) + "\n\n"
    template = env.get_template("uvm_reg_block_paged.jinja")
  else:
    raise TypeError(f"addrblock_to_ral cannot handle an address block of type: {type(ablock)}")

  ral_str += template.render(block=ablock, predictor_type=predictor_type)

  return ral_str


def reg_to_ral(
      reg: Register,
      data_size: int = 32
    ) -> str:
  """Convert the provided register to a UVM Register for the RAL

  Args:
      reg (Register): The register to create the RAL for
      data_size (int, optional): The register data width. Defaults to 32.
      coverage (str, optional): The UVM built in coverage. Defaults to "UVM_NO_COVERAGE".

  Returns:
      str: The string version of the generated RAL
  """
  env = Environment(
    loader=PackageLoader("rtlpy", "_uvm_templates"),
    lstrip_blocks=True,
    trim_blocks=True
  )

  template = env.get_template("uvm_reg.jinja")

  return template.render(reg=reg, data_size=data_size)
