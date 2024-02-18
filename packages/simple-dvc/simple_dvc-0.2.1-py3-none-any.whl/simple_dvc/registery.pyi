import scriptconfig as scfg
from _typeshed import Incomplete


class DataRegistry:
    registry_fpath: Incomplete

    def __init__(self, registry_fpath: Incomplete | None = ...) -> None:
        ...

    def pandas(self, **kwargs):
        ...

    def list(self, **kwargs) -> None:
        ...

    def add(self, name, path, **kwargs) -> None:
        ...

    def set(self, name, path: Incomplete | None = ..., **kwargs) -> None:
        ...

    def remove(self, name) -> None:
        ...

    def read(self):
        ...

    def query(self, must_exist: bool = ..., **kwargs):
        ...

    def find(self,
             on_error: str = ...,
             envvar: Incomplete | None = ...,
             **kwargs):
        ...


def find_dvc_dpath(name=..., on_error: str = ..., **kwargs):
    ...


def find_smart_dvc_dpath(*args, **kw):
    ...


class CommonRegistryConfig(scfg.DataConfig):
    name: Incomplete
    hardware: Incomplete
    priority: Incomplete
    tags: Incomplete
    path: Incomplete


class DVC_RegisteryCLI(scfg.ModalCLI):
    __command__: str

    class Add(CommonRegistryConfig):
        __command__: str

        @classmethod
        def main(cls, cmdline: int = ..., **kwargs) -> None:
            ...

    class List(CommonRegistryConfig):
        __command__: str
        must_exist: Incomplete

        @classmethod
        def main(cls, cmdline: int = ..., **kwargs) -> None:
            ...

    class Remove(CommonRegistryConfig):
        __command__: str

        @classmethod
        def main(cls, cmdline: int = ..., **kwargs) -> None:
            ...

    class Set(CommonRegistryConfig):
        __command__: str

        @classmethod
        def main(cls, cmdline: int = ..., **kwargs) -> None:
            ...

    class Find(CommonRegistryConfig):
        __command__: str
        must_exist: Incomplete

        @classmethod
        def main(cls, cmdline: int = ..., **kwargs) -> None:
            ...
