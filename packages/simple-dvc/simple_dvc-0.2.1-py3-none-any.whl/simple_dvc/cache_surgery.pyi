import scriptconfig as scfg
from _typeshed import Incomplete

modal: Incomplete


class CachePurgeCLI(scfg.DataConfig):
    __command__: str
    path: Incomplete
    workers: Incomplete
    invert: Incomplete

    @classmethod
    def main(cls, cmdline: bool = ..., **kwargs) -> None:
        ...


class CacheCopyCLI(scfg.Config):
    __command__: str
    __default__: Incomplete

    @classmethod
    def main(cls, cmdline: bool = ..., **kwargs) -> None:
        ...


def find_cached_fpaths(dvc, dpath) -> None:
    ...
