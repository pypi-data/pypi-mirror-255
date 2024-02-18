#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
"""
CLI definition
"""
import scriptconfig as scfg  # NOQA
import ubelt as ub
from simple_dvc.api import SimpleDVC


class SimpleDVC_CLI(scfg.ModalCLI):
    """
    A DVC CLI That uses our simplified (and more permissive) interface.

    The main advantage is that you can run these commands outside a DVC repo as
    long as you point to a valid in-repo path.
    """

    class Add(scfg.DataConfig):
        """
        Add data to the DVC repo.
        """
        __command__ = 'add'

        paths = scfg.Value([], nargs='+', position=1, help='Input files / directories to add')
        verbose = scfg.Value(0, short_alias=['v'], isflag=True, help='verbosity')

        @classmethod
        def main(cls, cmdline=1, **kwargs):
            config = cls.cli(cmdline=cmdline, data=kwargs, strict=True)
            dvc = SimpleDVC()
            dvc.add(config.paths, verbose=config.verbose)

    class Pull(scfg.DataConfig):
        """
        Pull data from a DVC remote.
        """
        __command__ = 'pull'

        paths = scfg.Value([], nargs='+', position=1, help='Data to attempt to pull')

        verbose = scfg.Value(0, short_alias=['v'], isflag=True, help='verbosity')
        jobs = scfg.Value('default', short_alias=['-j'], help='Number of jobs to run simultaneously. The default value is 4 * cpu_count()')
        remote = scfg.Value(None, short_alias=['r'], help='Remote storage to pull from')

        force = scfg.Value(False, isflag=True, short_alias=['f'], help='Do not prompt when removing working directory files.')
        recursive = scfg.Value(False, isflag=True, short_alias=['R'], help='Pull cache for subdirectories of the specified directory')
        allow_missing = scfg.Value(False, isflag=True, help='Ignore errors if some of the files or directories are missing')

        @classmethod
        def main(cls, cmdline=1, **kwargs):
            config = cls.cli(cmdline=cmdline, data=kwargs, strict=True)
            dvc = SimpleDVC()
            pull_kwargs = ub.compatible(config, dvc.pull)
            dvc.pull(config.paths, **pull_kwargs)

    class Push(scfg.DataConfig):
        """
        Push data to a DVC remote.
        """
        __command__ = 'push'

        paths = scfg.Value([], nargs='+', position=1, help='Data to attempt to push')

        verbose = scfg.Value(0, short_alias=['v'], isflag=True, help='verbosity')
        jobs = scfg.Value('default', short_alias=['-j'], help='Number of jobs to run simultaneously. The default value is 4 * cpu_count()')
        remote = scfg.Value(None, short_alias=['r'], help='Remote storage to push from')

        # force = scfg.Value(False, isflag=True, short_alias=['f'], help='Do not prompt when removing working directory files.')
        recursive = scfg.Value(False, isflag=True, short_alias=['R'], help='Push cache for subdirectories of the specified directory')
        # allow_missing = scfg.Value(False, isflag=True, help='Ignore errors if some of the files or directories are missing')

        @classmethod
        def main(cls, cmdline=1, **kwargs):
            config = cls.cli(cmdline=cmdline, data=kwargs, strict=True)
            dvc = SimpleDVC()
            push_kwargs = ub.compatible(config, dvc.push)
            dvc.push(config.paths, **push_kwargs)

    class Request(scfg.DataConfig):
        """
        Like pull, but only tries to pull if the requested file doesn't exist.
        """
        __command__ = 'request'

        paths = scfg.Value([], nargs='+', position=1, help='Data to attempt to pull. Individual args can be a YAML list.')
        remote = scfg.Value(None, short_alias=['r'], help='remote to pull from if needed')
        verbose = scfg.Value(0, short_alias=['v'], isflag=True, help='verbosity')
        pull = scfg.Value(0, isflag=True, help='if True, pull instead of request.')

        @classmethod
        def main(cls, cmdline=1, **kwargs):
            config = cls.cli(cmdline=cmdline, data=kwargs, strict=True)
            import rich
            if config.verbose:
                rich.print(ub.urepr(config, nl=1))
            dvc = SimpleDVC()
            paths = config.paths
            from kwutil.util_path import coerce_patterned_paths
            resolved_paths = coerce_patterned_paths(paths, globfallback=True)
            if config.verbose:
                print('resolved_paths = {}'.format(ub.urepr(resolved_paths, nl=1)))
            dvc.request(resolved_paths, verbose=config.verbose, pull=config.pull)

    class CacheDir(scfg.DataConfig):
        """
        Print the cache directory
        """
        __command__ = 'cache_dir'

        dvc_root = scfg.Value('.', position=1, help='get the cache path for this DVC repo')

        @classmethod
        def main(cls, cmdline=1, **kwargs):
            config = cls.cli(cmdline=cmdline, data=kwargs, strict=True)
            dvc = SimpleDVC(dvc_root=config.dvc_root)
            print(dvc.cache_dir)

    class ListSidecars(scfg.DataConfig):
        """
        List all sidecars associated with a path.
        """
        __command__ = 'sidecars'
        path = scfg.Value('.', position=1, help='sidecar file')

        @classmethod
        def main(cls, cmdline=1, **kwargs):
            config = cls.cli(cmdline=cmdline, data=kwargs, strict=True)
            dvc = SimpleDVC.coerce(config.path)
            for fpath in dvc.sidecar_paths(config.path):
                print(fpath)

    class ValidateSidecar(scfg.DataConfig):
        """
        Validate that everything marked in a sidecar file looks ok.
        """
        __command__ = 'validate_sidecar'
        path = scfg.Value(None, position=1, help='path associated with sidecars to validate')
        check_hash = scfg.Value(False, isflag=True, help='if true also check hashes')

        @classmethod
        def main(cls, cmdline=1, **kwargs):
            import rich
            config = cls.cli(cmdline=cmdline, data=kwargs, strict=True)
            dvc = SimpleDVC.coerce(config.path)

            from kwutil import util_progress
            pman0 = util_progress.ProgressManager()
            with pman0:
                sidecar_fpaths = list(pman0.progiter(dvc.sidecar_paths(config.path), desc='find sidecars'))

            def process_item(item):
                if config.check_hash:
                    if item['cache_exists']:
                        got_md5 = ub.hash_file(item['cache_path'], hasher='md5')
                        item['checksum_ok'] = item['md5'].startswith(got_md5)
                    else:
                        item['checksum_ok'] = None

            pman1 = util_progress.ProgressManager('progiter', verbose=3)
            for sidecar_fpath in pman1.progiter(sidecar_fpaths, desc='read sidecar'):
                print(f'Validate: sidecar_fpath={sidecar_fpath}')
                item_gen = dvc._sidecar_references(sidecar_fpath)
                first_item = None
                items = []

                item = next(item_gen)
                process_item(item)
                total = None
                if 'nfiles' in item:
                    total = item['nfiles']
                items.append(item)

                pman2 = util_progress.ProgressManager()
                with pman2:
                    for item in pman2.progiter(item_gen, total=total):
                        process_item(item)
                        items.append(item)
                first_item = items[0]
                if len(items) > 1:
                    first_item['n_file_co_exists'] = sum(f['co_exists'] for f in items[1:])
                    first_item['n_file_cache_exists'] = sum(f['cache_exists'] for f in items[1:])
                    if config.check_hash:
                        # first_item['n_file_checksum_ok'] = sum(flag for f in items[1:] if (flag := f['checksum_ok']) is not None)
                        first_item['n_file_checksum_ok'] = sum(f['checksum_ok'] for f in items[1:] if f['checksum_ok'] is not None)
                rich.print(ub.urepr(first_item, nl=1))

    # registery = DVC_RegisteryCLI
    from simple_dvc.registery import DVC_RegisteryCLI as registery
    from simple_dvc.cache_validate import DvcCacheValidateCLI
    from simple_dvc.discover_ssh_remote import DiscoverSshRemoteCLI

    # Add a subset of the registry to the top level?
    # Find = registery.Find


main = SimpleDVC_CLI.main


if __name__ == '__main__':
    """
    CommandLine:
        python ~/code/simple_dvc/simple_dvc/main.py
    """
    main()
