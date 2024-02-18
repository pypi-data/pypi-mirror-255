from typing import Iterable
from os import PathLike
from typing import List
import ubelt as ub
from _typeshed import Incomplete
from collections.abc import Generator
from typing import Any

Path = str | PathLike
__docstubs__: str


class SimpleDVC(ub.NiceRepr):
    dvc_root: Incomplete
    remote: Incomplete

    def __init__(self,
                 dvc_root: Incomplete | None = ...,
                 remote: Incomplete | None = ...) -> None:
        ...

    @property
    def dpath(self):
        ...

    @classmethod
    def demo(cls, code: str = ...):
        ...

    @classmethod
    def demo_dpath(cls, reset: bool = ...):
        ...

    def __nice__(self):
        ...

    @classmethod
    def init(cls,
             dpath,
             no_scm: bool = ...,
             force: bool = ...,
             verbose: int = ...):
        ...

    def cache_dir(self):
        ...

    @classmethod
    def coerce(cls, dvc_path, **kw):
        ...

    @classmethod
    def find_root(cls, path: Incomplete | None = ...) -> Path | None:
        ...

    def add(self,
            path: str | PathLike | Iterable[str | PathLike],
            verbose: int = ...) -> None:
        ...

    def pathsremove(self,
                    path: str | PathLike | Iterable[str | PathLike],
                    verbose: int = ...) -> None:
        ...

    def check_ignore(self,
                     path,
                     details: int = ...,
                     verbose: int = ...) -> None:
        ...

    def git_pull(self) -> None:
        ...

    def git_push(self) -> None:
        ...

    def git_commit(self, message) -> None:
        ...

    def git_commitpush(self,
                       message: str = ...,
                       pull_on_fail: bool = ...) -> None:
        ...

    def push(self,
             path: Path | List[Path],
             remote: str | None = None,
             recursive: bool = False,
             jobs: int | None = None,
             verbose: int = ...) -> None:
        ...

    def pull(self,
             path,
             remote: Incomplete | None = ...,
             recursive: bool = ...,
             jobs: Incomplete | None = ...,
             verbose: int = ...,
             allow_missing: bool = ...,
             force: bool = ...) -> None:
        ...

    def request(self,
                path: Path | List[Path],
                remote: Incomplete | None = ...,
                verbose: int = 0,
                pull: bool = False):
        ...

    def unprotect(self, path) -> None:
        ...

    def is_tracked(self, path):
        ...

    @classmethod
    def find_file_tracker(cls, path):
        ...

    def find_dir_tracker(cls, path):
        ...

    def read_dvc_sidecar(self, sidecar_fpath):
        ...

    def resolve_cache_paths(
            self, sidecar_fpath: PathLike | str) -> Generator[Any, None, None]:
        ...

    def find_sidecar_paths_in_dpath(
            self, dpath: Path | str) -> Generator[ub.Path, None, None]:
        ...

    def find_sidecar_paths_associated_with(
            self, dpath: Path | str) -> Generator[ub.Path, None, None]:
        ...

    def sidecar_paths(self,
                      path: Path | str) -> Generator[ub.Path, None, None]:
        ...
