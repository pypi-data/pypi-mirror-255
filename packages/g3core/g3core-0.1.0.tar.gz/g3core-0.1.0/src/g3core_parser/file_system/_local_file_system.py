import os
import functools

from ._base_file_system import G3CoreFileSystem


class G3CoreFileSystemLocal(G3CoreFileSystem):
    def __init__(
        self, path: str, ignore_private_lib: bool = True
    ) -> None:
        super().__init__()
        self.g3core_dirpath = path
        self.ignore_private_lib = ignore_private_lib

    @functools.cache
    def _get_file_paths(self, file_extension: str) -> list[str]:
        paths = []
        for dirpath, _, filenames in os.walk(self.g3core_dirpath):
            if '.git' in dirpath:
                continue
            if any(priv_lib in dirpath for priv_lib in self.PRIVATE_LIBRARIES):
                if self.ignore_private_lib:
                    continue
            for filename in filenames:
                if filename.endswith(file_extension):
                    paths.append(os.path.join(dirpath, filename))
        return paths

    @functools.cache
    def _get_file_contents(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
