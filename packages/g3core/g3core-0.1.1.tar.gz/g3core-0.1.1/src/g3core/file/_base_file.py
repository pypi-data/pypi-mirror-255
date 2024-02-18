import re
import typing
import functools

from dataclasses import dataclass

if typing.TYPE_CHECKING:
    from gitlab.v4.objects import Project


@functools.cache
def extract_from_file_contents(
    file_contents: str,
    structure_name: str,
    structure_type: str,
    search_pattern: str
) -> str:
    contents = re.search(
        search_pattern, file_contents, flags=re.DOTALL | re.MULTILINE
        )
    if contents:
        return contents.group(1)
    raise ValueError(
        f'{structure_type} "{structure_name}" was not found in the file.'
        )


@dataclass
class BaseFile:
    contents: str

    @classmethod
    def from_local_path(cls, path: str) -> typing.Self:
        with open(path, 'r', encoding='utf-8') as file:
            return cls(file.read())

    @classmethod
    def from_gitlab(
        cls,
        g3core: 'Project',
        file_path: str,
        branch: str = 'master',
    ) -> typing.Self:
        file = g3core.files.raw(file_path, ref=branch)
        assert isinstance(file, bytes), "Unexpected file contents format"
        return cls(file.decode())

    def _get_structure(
        self,
        structure_name: str,
        structure_type: str,
        search_pattern: str
    ) -> str:
        return extract_from_file_contents(
            self.contents, structure_name, structure_type, search_pattern
            )
