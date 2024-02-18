import scriptconfig as scfg
from _typeshed import Incomplete
from simple_dvc.registery import DVC_RegisteryCLI


class SimpleDVC_CLI(scfg.ModalCLI):

    class Add(scfg.DataConfig):
        __command__: str
        paths: Incomplete

        @classmethod
        def main(cls, cmdline: int = ..., **kwargs) -> None:
            ...

    class Pull(scfg.DataConfig):
        __command__: str
        paths: Incomplete
        verbose: Incomplete
        jobs: Incomplete
        remote: Incomplete
        force: Incomplete
        recursive: Incomplete
        allow_missing: Incomplete

        @classmethod
        def main(cls, cmdline: int = ..., **kwargs) -> None:
            ...

    class Request(scfg.DataConfig):
        __command__: str
        paths: Incomplete
        remote: Incomplete
        verbose: Incomplete
        pull: Incomplete

        @classmethod
        def main(cls, cmdline: int = ..., **kwargs) -> None:
            ...

    class CacheDir(scfg.DataConfig):
        __command__: str
        dvc_root: Incomplete

        @classmethod
        def main(cls, cmdline: int = ..., **kwargs) -> None:
            ...

    class ListSidecars(scfg.DataConfig):
        __command__: str
        path: Incomplete

        @classmethod
        def main(cls, cmdline: int = ..., **kwargs) -> None:
            ...

    class ValidateSidecar(scfg.DataConfig):
        __command__: str
        path: Incomplete
        check_hash: Incomplete

        @classmethod
        def main(cls, cmdline: int = ..., **kwargs) -> None:
            ...

    registery = DVC_RegisteryCLI


main: Incomplete
