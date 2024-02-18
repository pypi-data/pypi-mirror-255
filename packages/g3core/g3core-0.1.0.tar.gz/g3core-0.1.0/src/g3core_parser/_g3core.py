import typing

from .file_system._local_file_system import G3CoreFileSystemLocal
from .file_system._gitlab_file_system import G3CoreFileSystemGitlab

if typing.TYPE_CHECKING:
    from .file_system._base_file_system import G3CoreFileSystem
    from .st_parser import STFunction, STFunctionBlock, STIntEnum, STStruct


class G3Core:
    def __init__(self, file_system: 'G3CoreFileSystem') -> None:
        self.file_system = file_system

    @classmethod
    def from_local(
        cls, path: str, ignore_private_lib: bool = True
    ) -> typing.Self:
        return cls(G3CoreFileSystemLocal(path, ignore_private_lib))

    @classmethod
    def from_giltab(
        cls, branch: str = 'master', ignore_private_lib: bool = True
    ) -> typing.Self:
        return cls(G3CoreFileSystemGitlab(branch, ignore_private_lib))

    def find_function_block(
        self, fb_name: str, search_here_first: str | None = None
    ) -> tuple[str, 'STFunctionBlock']:
        if search_here_first:
            file = self.file_system.get_fun_file(search_here_first)
            try:
                return search_here_first, file.get_function_block(fb_name)
            except ValueError:
                pass
        for path in self.file_system._get_file_paths(".fun"):
            file = self.file_system.get_fun_file(path)
            try:
                return path, file.get_function_block(fb_name)
            except ValueError:
                continue
        err_msg = f'Function Block "{fb_name}" was not found in G3Core files.'
        raise ValueError(err_msg)

    def find_function(
        self, f_name: str, search_here_first: str | None = None
    ) -> tuple[str, 'STFunction']:
        if search_here_first:
            file = self.file_system.get_fun_file(search_here_first)
            try:
                return search_here_first, file.get_function(f_name)
            except ValueError:
                pass
        for path in self.file_system._get_file_paths(".fun"):
            file = self.file_system.get_fun_file(path)
            try:
                return path, file.get_function(f_name)
            except ValueError:
                continue
        err_msg = f'Function "{f_name}" was not found in G3Core files.'
        raise ValueError(err_msg)

    def find_struct(
        self, s_name: str, search_here_first: str | None = None
    ) -> tuple[str, 'STStruct']:
        if search_here_first:
            file = self.file_system.get_typ_file(search_here_first)
            try:
                return search_here_first, file.get_struct(s_name)
            except ValueError:
                pass
        for path in self.file_system._get_file_paths(".typ"):
            file = self.file_system.get_typ_file(path)
            try:
                return path, file.get_struct(s_name)
            except ValueError:
                continue
        err_msg = f'Struct "{s_name}" was not found in G3Core files.'
        raise ValueError(err_msg)

    def find_enum(
        self, e_name: str, search_here_first: str | None = None
    ) -> tuple[str, 'STIntEnum']:
        if search_here_first:
            file = self.file_system.get_typ_file(search_here_first)
            try:
                return search_here_first, file.get_int_enum(e_name)
            except ValueError:
                pass
        for path in self.file_system._get_file_paths(".typ"):
            file = self.file_system.get_typ_file(path)
            try:
                return path, file.get_int_enum(e_name)
            except ValueError:
                continue
        err_msg = f'Enum "{e_name}" was not found in G3Core files.'
        raise ValueError(err_msg)
