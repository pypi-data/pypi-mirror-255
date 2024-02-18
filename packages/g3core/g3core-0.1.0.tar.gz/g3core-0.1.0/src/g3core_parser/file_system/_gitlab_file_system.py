import logging
import functools

from gitlab import Gitlab

from ._base_file_system import G3CoreFileSystem


class G3CoreFileSystemGitlab(G3CoreFileSystem):
    URL = "https://gitlab.elektroline.cz"
    PROJECT_NAME = "plc/SystemG3Core"
    ACCESS_TOKEN = ""
    PROJECT_ID = 263

    def __init__(
        self, branch: str = 'master', ignore_private_lib: bool = True
    ) -> None:
        super().__init__()
        self.ignore_private_lib = ignore_private_lib
        self._branch = branch
        self._file_contents: dict[str, bytes] = {}
        self._fetch_files()

    @property
    def branch(self):
        return self._branch

    def _fetch_files(self):
        with Gitlab(self.URL, self.ACCESS_TOKEN) as gl:
            project = gl.projects.get(self.PROJECT_ID)
            project_items = project.repository_tree(recursive=True, all=True)
            project_files = [
                item for item in project_items
                if item['type'] == 'blob' and
                not (self.ignore_private_lib and item['path'].startswith('_'))
                ]
            project_files_len = len(project_files)
            for i, file in enumerate(project_files):
                logging.info(
                    'Fetching file "%s" (%i / %i)',
                    file['path'], i, project_files_len
                    )
                contents = project.files.raw(file['path'], ref=self._branch)
                self._file_contents[file['path']] = contents

    @functools.cache
    def _get_file_paths(self, file_extension: str) -> list[str]:
        file_paths = []
        for path in self._file_contents:
            if any(priv_lib in path for priv_lib in self.PRIVATE_LIBRARIES):
                if self.ignore_private_lib:
                    continue
            if path.endswith(file_extension):
                file_paths.append(path)
        return file_paths

    @functools.cache
    def _get_file_contents(self, file_path: str) -> str:
        return self._file_contents[file_path].decode()
