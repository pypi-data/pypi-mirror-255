import re

from dataclasses import dataclass
from functools import cached_property

from ._st_var import STVariable
from ._st_base_structure import STBaseStructure


@dataclass
class STStruct(STBaseStructure):

    @cached_property
    def members(self) -> list[STVariable]:
        return self._parse_section('STRUCT', 'END_STRUCT')

    def _extract_name(self) -> str:
        name = re.search(r"^\s*(\w+)\s*:\s*STRUCT", self.contents)
        if not name:
            raise TypeError('Cannot parse the name of the struct.')
        return name.group(1)

    def instantiate(self, varname: str, **config_params: str) -> str:
        raise NotImplementedError
