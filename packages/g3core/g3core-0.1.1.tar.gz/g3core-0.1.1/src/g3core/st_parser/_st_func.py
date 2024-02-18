import re

from dataclasses import dataclass
from functools import cached_property

from ._st_var import STVariable
from ._st_base_structure import STBaseStructure


@dataclass
class STFunction(STBaseStructure):

    def _extract_name(self) -> str:
        name = re.search(r"FUNCTION\s+(\w+)", self.contents)
        if not name:
            raise TypeError('Cannot parse the name of the function.')
        return name.group(1)

    @cached_property
    def return_type(self) -> str:
        match = re.search(r"FUNCTION\s+.*? :\s+(\w+)", self.contents)
        if not match:
            raise TypeError('Cannot parse return type of the function.')
        return match.group(1)

    @cached_property
    def var_input(self) -> list[STVariable]:
        return self._parse_section('VAR_INPUT', 'END_VAR')

    def instantiate(self, varname: str) -> str:
        return f'f{varname}:{self.name}'


@dataclass
class STFunctionBlock(STBaseStructure):

    def _extract_name(self) -> str:
        name = re.search(r"FUNCTION_BLOCK\s+(\w+)", self.contents)
        if not name:
            raise TypeError('Cannot parse the name of the function block.')
        return name.group(1)

    @cached_property
    def var_in_out(self) -> list[STVariable]:
        return self._parse_section('VAR_IN_OUT', 'END_VAR')

    @cached_property
    def var_input(self) -> list[STVariable]:
        return self._parse_section('VAR_INPUT', 'END_VAR')

    @cached_property
    def var_out(self) -> list[STVariable]:
        return self._parse_section('VAR_OUT', 'END_VAR')

    @cached_property
    def var(self) -> list[STVariable]:
        return self._parse_section('VAR', 'END_VAR')

    def instantiate(self, varname: str) -> str:
        return f'fb{varname}:{self.name}'
