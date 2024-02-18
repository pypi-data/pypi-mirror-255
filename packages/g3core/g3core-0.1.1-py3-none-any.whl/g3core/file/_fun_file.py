from dataclasses import dataclass

from ._base_file import BaseFile
from ..st_parser import STFunction, STFunctionBlock


@dataclass
class FunFile(BaseFile):
    def get_function_block(self, fb_name: str) -> STFunctionBlock:
        fb_contents = self._get_structure(
            structure_name=fb_name,
            structure_type='Function block',
            search_pattern=(
                f'(^\\s*FUNCTION_BLOCK\\s+{fb_name}\\s+.*?END_FUNCTION_BLOCK)'
                )
            )
        return STFunctionBlock(fb_contents)

    def get_function(self, func_name: str) -> STFunction:
        f_contents = self._get_structure(
            structure_name=func_name,
            structure_type='Function',
            search_pattern=(
                f'(^\\s*FUNCTION\\s+{func_name}\\s+.*?END_FUNCTION)'
                )
            )
        return STFunction(f_contents)
