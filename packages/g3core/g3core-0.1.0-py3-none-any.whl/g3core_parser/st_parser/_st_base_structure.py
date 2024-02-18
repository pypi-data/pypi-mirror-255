import re

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property

from ._st_var import STVariable


@dataclass
class STBaseStructure(ABC):
    contents: str

    def __post_init__(self):
        self._normalize_indentation()

    def __str__(self) -> str:
        return self.contents

    def _normalize_indentation(self) -> None:
        INDENT = 4
        lines = self.contents.split("\n")
        first_line = lines.pop(0).strip()
        last_line = lines.pop(-1).strip()
        formatted_lines = [first_line]
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("VAR") or stripped.startswith("END_VAR"):
                formatted_lines.append(' ' * 1 * INDENT + stripped)
            else:
                formatted_lines.append(' ' * 2 * INDENT + stripped)
        formatted_lines.append(last_line)
        self.contents = "\n".join(formatted_lines)

    def _parse_section(
        self, section_start_kw: str, section_end_kw: str
    ) -> list[STVariable]:
        pattern = f'{section_start_kw}(.*?){section_end_kw}'
        section = re.search(pattern, self.contents, re.DOTALL)
        if not section:
            return []
        vars_matches = re.findall(
            r"(\w+) : ([^\:=]+)(?:(?: := (.*?))?;)(?:\s*\(\*(.*?)\*\))?",
            section.group(1)
            )
        return [
            STVariable(
                name=vm[0],
                dtype=vm[1],
                value=vm[2] if vm[2] else None,
                comment=vm[3] if vm[3] else None
                )
            for vm in vars_matches
            ]

    @cached_property
    def name(self) -> str:
        return self._extract_name()

    @abstractmethod
    def _extract_name(self) -> str:
        ...

    @abstractmethod
    def instantiate(self, *args, **kwargs) -> str:
        ...
