from abc import ABC, abstractmethod

from ..file._fun_file import FunFile
from ..file._typ_file import TypFile


class G3CoreFileSystem(ABC):
    PRIVATE_LIBRARIES = ['_BR']

    def __init__(self) -> None:
        super().__init__()
        self.fun_files: dict[str, FunFile] = {}
        self.typ_files: dict[str, TypFile] = {}

    @abstractmethod
    def _get_file_paths(self, file_extension: str) -> list[str]:
        pass

    @abstractmethod
    def _get_file_contents(self, file_path: str) -> str:
        pass

    def get_fun_file(self, path: str) -> FunFile:
        if path not in self.fun_files:
            self.fun_files[path] = FunFile(self._get_file_contents(path))
        return self.fun_files[path]

    def get_typ_file(self, path: str) -> TypFile:
        if path not in self.typ_files:
            self.typ_files[path] = TypFile(self._get_file_contents(path))
        return self.typ_files[path]
