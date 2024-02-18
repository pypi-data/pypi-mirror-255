from dataclasses import dataclass

from ._base_file import BaseFile
from ..st_parser import STStruct, STIntEnum


@dataclass
class TypFile(BaseFile):
    def get_struct(self, struct_name: str) -> STStruct:
        fb_contents = self._get_structure(
            structure_name=struct_name,
            structure_type='Struct',
            search_pattern=f'(^\\s*{struct_name}\\s*:\\s*STRUCT.*?END_STRUCT)',
            )
        return STStruct(fb_contents)

    def get_int_enum(self, enum_name: str) -> STIntEnum:
        e_contents = self._get_structure(
            structure_name=enum_name,
            structure_type='Enum',
            search_pattern=f"^\\s*{enum_name}\\s*:\\s*\\(.*?\\);",
            )
        return STIntEnum(e_contents)
