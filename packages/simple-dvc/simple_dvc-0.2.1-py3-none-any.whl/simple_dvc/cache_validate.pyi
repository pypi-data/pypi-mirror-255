import scriptconfig as scfg
from _typeshed import Incomplete


class DvcCacheValidateCLI(scfg.DataConfig):
    path: Incomplete

    @classmethod
    def main(cls, cmdline: int = ..., **kwargs) -> None:
        ...


def find_cached_fpaths(dvc, dpath) -> None:
    ...


__cli__ = DvcCacheValidateCLI
main: Incomplete
