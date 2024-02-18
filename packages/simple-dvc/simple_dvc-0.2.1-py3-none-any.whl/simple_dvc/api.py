#!/usr/bin/env python3
"""
A simplified Python DVC API
"""
import ubelt as ub
import os
from kwutil import util_path
from kwutil.util_yaml import Yaml

__docstubs__ = """
Path = str | PathLike
"""


class SimpleDVC(ub.NiceRepr):
    """
    A Simple DVC API

    Args:
        dvc_root (str | PathLike): path to DVC repo directory
        remote (str): dvc remote to sync to by default

    CommandLine:
        xdoctest -m simple_dvc.api SimpleDVC

    Example:
        >>> from simple_dvc import SimpleDVC
        >>> self = SimpleDVC.demo()
        >>> a_file_fpath = self.dpath / 'a_file.txt'
        >>> if not a_file_fpath.exists():
        >>>     a_file_fpath.write_text('hello')
        >>> self.add(a_file_fpath)
    """

    def __init__(self, dvc_root=None, remote=None):
        self.dvc_root = dvc_root
        self.remote = remote

    def list_remotes(self, name=None):
        info = ub.cmd('dvc remote list', cwd=self.dvc_root, check=True)
        remotes = []
        for line in info.stdout.split('\n'):
            if line:
                _name, _uri = line.split('\t')
                if name is None or name == _name:
                    remotes.append({
                        'name': _name,
                        'uri': _uri,
                    })
        return remotes

    @property
    def dpath(self):
        return self.dvc_root

    @classmethod
    def demo(cls, dpath=None, reset=False, with_git=False):
        """
        Create a demo DVC repo for tests.

        Args:
            dpath (str | PathLike):
                If specified force the repo to be made here.
                Otherwise choose a default.

        Example:
            >>> from simple_dvc.api import *  # NOQA
            >>> cls = SimpleDVC
            >>> self1 = cls.demo(with_git=0)
            >>> self2 = cls.demo(with_git=1)
        """
        from simple_dvc import demo
        import ubelt as ub
        if dpath is None:
            if with_git:
                base = 'demo_v2'
            else:
                base = 'demo_v1'
            demo_root = ub.Path.appdir('simple_dvc', 'demos', base)
        else:
            demo_root = dpath
        demo.init_randomized_dvc_repo(demo_root, with_git=True, reset=reset)
        self = cls(demo_root)
        return self

    @classmethod
    def demo_dpath(cls, reset=False):
        dvc_dpath = ub.Path.appdir('simple_dvc/test/test_dvc_repo')
        if reset:
            dvc_dpath.delete()
        if not dvc_dpath.exists():
            dvc_dpath.ensuredir()
            verbose = 2
            # Init empty git repo
            ub.cmd('git init --quiet', cwd=dvc_dpath, verbose=verbose)
            ub.cmd('git config --local receive.denyCurrentBranch "warn"', cwd=dvc_dpath, verbose=verbose)
            # Init empty dvc repo
            ub.cmd('dvc init --quiet', cwd=dvc_dpath, verbose=verbose)
            ub.cmd('dvc config core.autostage true', cwd=dvc_dpath, verbose=verbose)
            ub.cmd('dvc config cache.type "symlink,hardlink,copy"', cwd=dvc_dpath, verbose=verbose)
            ub.cmd('dvc config cache.shared group', cwd=dvc_dpath, verbose=verbose)
            ub.cmd('dvc config cache.protected true', cwd=dvc_dpath, verbose=verbose)
        return dvc_dpath

    def __nice__(self):
        return f'dvc_root={self.dvc_root}'

    @classmethod
    def init(cls, dpath, no_scm=False, force=False, verbose=0):
        """
        Initialize a DVC repo in a path
        """
        dpath = ub.Path(dpath.ensuredir())
        args = ['dvc', 'init']
        if verbose:
            args += ['--verbose']
        if force:
            args += ['--force']
        if no_scm:
            args += ['--no-scm']
        ub.cmd(args, cwd=dpath, verbose=3, check=True)
        self = cls(dpath)
        return self

    @ub.memoize_property
    def cache_dir(self):
        info = ub.cmd('dvc cache dir', cwd=self.dvc_root, check=True)
        cache_dpath = ub.Path(info['out'].strip())
        return cache_dpath

    @classmethod
    def coerce(cls, dvc_path, **kw):
        """
        Given a path inside DVC, finds the root.
        """
        dvc_root = cls.find_root(dvc_path)
        return cls(dvc_root, **kw)

    @classmethod
    def find_root(cls, path=None):
        """
        Given a path, search its ancestors to find the root of a dvc repo.

        Returns:
            Path | None
        """
        if path is None:
            raise Exception('no way to find dvc root')
        # Need to find it from the path
        path = ub.Path(path).resolve()
        max_parts = len(path.parts)
        curr = path
        found = None
        for _ in range(max_parts + 1):
            cand = curr / '.dvc'
            if cand.exists():
                found = curr
                break
            curr = curr.parent
        return found

    def _ensure_root(self, paths):
        if self.dvc_root is None:
            self.dvc_root = self.find_root(paths[0])
            print('found new self.dvc_root = {!r}'.format(self.dvc_root))
        return self.dvc_root

    def _ensure_remote(self, remote):
        if remote is None:
            remote = self.remote
        return remote

    def _resolve_root_and_relative_paths(self, paths):
        # try:
        #     dvc_root = self._ensure_root(paths)
        #     rel_paths = [os.fspath(p.relative_to(dvc_root)) for p in paths]
        # except Exception as ex:
        #     print(f'ex={ex}')
        # Handle symlinks: https://dvc.org/doc/user-guide/troubleshooting#add-symlink
        # not sure if this is safe
        dvc_root = self._ensure_root(paths)
        if dvc_root is None:
            raise Exception('unable to find a DVC root')
        dvc_root = dvc_root.resolve()
        # Note: this could resolve the symlink to the dvc cache which we dont want
        # rel_paths = [os.fspath(p.resolve().relative_to(dvc_root)) for p in paths]
        # Fixed version?
        parent_resolved = [p.parent.resolve() / p.name for p in paths]
        rel_paths = [os.fspath(p.relative_to(dvc_root)) for p in parent_resolved]

        return dvc_root, rel_paths

    def add(self, path, verbose=0):
        """
        Args:
            path (str | PathLike | Iterable[str | PathLike]):
                a single or multiple paths to add
        """
        dvc_root, rel_paths = self._dvc_path_op('add', path, verbose)
        has_autostage = ub.cmd('dvc config core.autostage', cwd=dvc_root, check=True)['out'].strip() == 'true'
        if not has_autostage:
            print('warning: Need autostage to complete the git commit')
            # raise NotImplementedError('Need autostage to complete the git commit')

    def pathsremove(self, path, verbose=0):
        """
        Args:
            path (str | PathLike | Iterable[str | PathLike]):
                a single or multiple paths to add
        """
        self._dvc_path_op('remove', path, verbose)

    def _dvc_path_op(self, op, path, verbose=0):
        """
        Args:
            path (str | PathLike | Iterable[str | PathLike]):
                a single or multiple paths to add
        """
        if verbose >= 3:
            print(f'Running dvc op={op}')
        dvc_main = _import_dvc_main()
        paths = list(map(ub.Path, _ensure_iterable(path)))
        if len(paths) == 0:
            print('No paths to add')
            return
        dvc_root, rel_paths = self._resolve_root_and_relative_paths(paths)
        with util_path.ChDir(dvc_root):
            dvc_command = [op] + rel_paths
            extra_args = self._verbose_extra_args(verbose)
            dvc_command = dvc_command + extra_args
            ret = dvc_main(dvc_command)
        if ret != 0:
            raise Exception(f'Failed to {op} files')
        return dvc_root, rel_paths

    def check_ignore(self, path, details=0, verbose=0):
        dvc_main = _import_dvc_main()
        paths = list(map(ub.Path, _ensure_iterable(path)))
        if len(paths) == 0:
            print('No paths to add')
            return
        dvc_root, rel_paths = self._resolve_root_and_relative_paths(paths)
        with util_path.ChDir(dvc_root):
            dvc_command = ['check-ignore'] + rel_paths
            if details:
                dvc_command += ['--details']
            extra_args = self._verbose_extra_args(verbose)
            dvc_command = dvc_command + extra_args
            ret = dvc_main(dvc_command)
        if ret != 0:
            raise Exception('Failed check-ignore')

    def git_pull(self):
        ub.cmd('git pull', verbose=3, check=True, cwd=self.dvc_root)

    def git_push(self):
        ub.cmd('git push', verbose=3, check=True, cwd=self.dvc_root)

    def git_commit(self, message):
        ub.cmd(f'git commit -m "{message}"', verbose=3, check=True, cwd=self.dvc_root)

    def git_commitpush(self, message='', pull_on_fail=True):
        """
        TODO: better name here?
        """
        # dangerous?
        try:
            self.git_commit(message)
        except Exception as e:
            ex = e
            if 'nothing added to commit' not in ex.output:
                raise
        else:
            try:
                self.git_push()
            except Exception:
                if pull_on_fail:
                    print('Initial push failed, will pull and then try once more')
                    self.git_pull()
                    self.git_push()
                else:
                    raise

    def _verbose_extra_args(self, verbose):
        extra_args = []
        if verbose:
            verbose = max(min(3, verbose), 1)
            extra_args += ['-' + 'v' * verbose]
        return extra_args

    def _remote_extra_args(self, remote, recursive, jobs, verbose):
        extra_args = self._verbose_extra_args(verbose)
        if remote:
            extra_args += ['-r', remote]
        if jobs is not None:
            extra_args += ['--jobs', str(jobs)]
        if recursive:
            extra_args += ['--recursive']
        return extra_args

    def push(self, path, remote=None, recursive=False, jobs=None, verbose=0):
        """
        Push the content tracked by .dvc files to remote storage.

        Args:
            path (Path | List[Path]):
                one or more file paths that should have an associated .dvc
                sidecar file or if recursive is true, a directory containing
                multiple tracked files.

            remote (str):
                the name of the remote registered in the .dvc/config to push to

            recursive (bool):
                if True, then items in ``path`` can be a directory.

            jobs (int): number of parallel workers
        """
        dvc_main = _import_dvc_main()
        paths = list(map(ub.Path, _ensure_iterable(path)))
        if len(paths) == 0:
            print('No paths to push')
            return
        remote = self._ensure_remote(remote)
        dvc_root, rel_paths = self._resolve_root_and_relative_paths(paths)
        extra_args = self._remote_extra_args(remote, recursive, jobs, verbose)
        with util_path.ChDir(dvc_root):
            dvc_command = ['push'] + extra_args + [str(p) for p in rel_paths]
            dvc_main(dvc_command)

    def pull(self, path, remote=None, recursive=False, jobs=None, verbose=0, allow_missing=False, force=False):
        """
        Wrapper around DVC pull

        CommandLine:
            xdoctest -m simple_dvc.api SimpleDVC.pull

        Example:
            >>> from simple_dvc.api import SimpleDVC  # NOQA
            >>> import ubelt as ub
            >>> remote = SimpleDVC.demo(with_git=1)
            >>> dpath = ub.Path.appdir('simple_dvc/doctest/pull').delete().ensuredir()
            >>> dvc_dpath = dpath / 'repo'
            >>> # Clone a Demo DVC repo, setup the remote, and test
            >>> _ = ub.cmd(f'git clone {remote.dpath / ".git"} {dvc_dpath}', verbose=3)
            >>> _ = ub.cmd(f'dvc remote add local --default {remote.dpath / ".dvc/cache"}', verbose=3, cwd=dvc_dpath)
            >>> # Setup our local API
            >>> self = SimpleDVC(dvc_dpath)
            >>> # Test a basic file pull
            >>> assert not (dvc_dpath / 'root_file').exists()
            >>> # Note: pull does accept the non-dvc file request
            >>> self.pull(dvc_dpath / 'root_file.dvc')
            >>> assert (dvc_dpath / 'root_file').exists()
            >>> # Test a basic directory pull
            >>> assert not (dvc_dpath / 'root_dir').exists()
            >>> self.pull(dvc_dpath / 'root_dir.dvc')
            >>> assert (dvc_dpath / 'root_dir').exists()
            >>> # Test a recursive pull
            >>> assert not (dvc_dpath / 'test-set1/manifest.txt').exists()
            >>> assert not (dvc_dpath / 'test-set1/assets/').exists()
            >>> self.pull(dvc_dpath / 'test-set1', recursive=True)
            >>> assert (dvc_dpath / 'test-set1/manifest.txt').exists()
            >>> assert (dvc_dpath / 'test-set1/assets/').exists()
            >>> assert len((dvc_dpath / 'test-set1/assets/').ls()) > 1
        """
        dvc_main = _import_dvc_main()
        paths = list(map(ub.Path, _ensure_iterable(path)))
        if len(paths) == 0:
            print('No paths to pull')
            return
        remote = self._ensure_remote(remote)
        dvc_root, rel_paths = self._resolve_root_and_relative_paths(paths)
        extra_args = self._remote_extra_args(remote, recursive, jobs, verbose)
        with util_path.ChDir(dvc_root):
            dvc_command = ['pull'] + extra_args + [str(p) for p in rel_paths]
            dvc_main(dvc_command)

    def request(self, path, remote=None, verbose=0, pull=False):
        """
        Requests to ensure that a specific file from DVC exists.

        Any files that do not exist, check to see if there is an associated
        .dvc sidecar file. If any sidecar files are missing, an error is
        thrown.  Otherwise we attempt to pull the missing files.

        TODO:
            * Add argument to validate that the data was pulled correctly
            (i.e. there are no dangling symlinks)

        Args:
            path (Path | List[Path]):
                one or more file paths that should have an associated .dvc
                sidecar file.

            remote : specify the DVC remote

            verbose (int): verbosity

            pull (bool): if True pull instead of request (convinience option)

        CommandLine:
            xdoctest -m simple_dvc.api SimpleDVC.request

        Example:
            >>> from simple_dvc.api import SimpleDVC  # NOQA
            >>> import ubelt as ub
            >>> remote = SimpleDVC.demo(with_git=1)
            >>> dpath = ub.Path.appdir('simple_dvc/doctest/request').delete().ensuredir()
            >>> dvc_dpath = dpath / 'repo'
            >>> # Clone a Demo DVC repo, setup the remote, and test
            >>> _ = ub.cmd(f'git clone {remote.dpath / ".git"} {dvc_dpath}', verbose=3)
            >>> _ = ub.cmd(f'dvc remote add local --default {remote.dpath / ".dvc/cache"}', verbose=3, cwd=dvc_dpath)
            >>> # Setup our local API
            >>> self = SimpleDVC(dvc_dpath)
            >>> # Test a recursive pull
            >>> assert not (dvc_dpath / 'test-set1/manifest.txt').exists()
            >>> assert not (dvc_dpath / 'test-set1/assets/').exists()
            >>> path = dvc_dpath / 'test-set1/assets/asset_004.data'
            >>> self.request(path, verbose=0)
            >>> assert (dvc_dpath / 'test-set1/assets/').exists()
            >>> assert len((dvc_dpath / 'test-set1/assets/').ls()) > 1
        """
        paths = list(map(ub.Path, _ensure_iterable(path)))

        if verbose:
            print('checking paths = {}'.format(ub.urepr(paths, nl=1)))

        # TODO: if sidecar files are given in the request, resolve those to
        # non-sidecar paths here.
        missing_data = [path for path in paths if not path.exists()]

        if verbose:
            print('missing_data = {}'.format(ub.urepr(missing_data, nl=1)))

        if pull:
            missing_data = paths

        if missing_data:
            dvc_root, rel_paths = self._resolve_root_and_relative_paths(missing_data)

            def _find_sidecar(rel_path):
                rel_path = ub.Path(rel_path)
                first_cand = dvc_root / rel_path.augment(stem=rel_path.name, ext='.dvc')
                if first_cand.exists():
                    return first_cand
                rel_parts = rel_path.parts
                for i in reversed(range(len(rel_parts))):
                    parts = rel_parts[0:i]
                    cand_dat = dvc_root.joinpath(*parts)
                    cand_dvc = cand_dat.augment(stem=cand_dat.name, ext='.dvc')
                    if cand_dvc.exists():
                        return cand_dvc
                raise IOError(f'Could not find sidecar for: rel_path={rel_path} in dvc_root={dvc_root}. Wrong path, or need to git pull?')

            to_pull = [_find_sidecar(rel_path) for rel_path in rel_paths]
            missing_sidecar = [dvc_fpath for dvc_fpath in to_pull if not dvc_fpath.exists()]

            if missing_sidecar:
                if len(missing_sidecar) < 10:
                    print(f'missing_sidecar={missing_sidecar}')
                raise Exception(f'There were {len(missing_sidecar)} / {len(paths)} missing sidecar files')

            if to_pull:
                print(f'to_pull={to_pull}')
                self.pull(to_pull, remote=remote, verbose=verbose)

    def unprotect(self, path, verbose=0):
        dvc_main = _import_dvc_main()
        paths = list(map(ub.Path, _ensure_iterable(path)))
        if len(paths) == 0:
            print('No paths to unprotect')
            return
        dvc_root, rel_paths = self._resolve_root_and_relative_paths(paths)
        flags = []
        if verbose:
            flags += ['--verbose']
        with util_path.ChDir(dvc_root):
            dvc_command = ['unprotect'] + flags + rel_paths
            dvc_main(dvc_command)

    def is_tracked(self, path):
        path = ub.Path(path)
        tracker_fpath = self.find_file_tracker(path)
        if tracker_fpath is not None:
            return True
        else:
            tracker_fpath = self.find_dir_tracker(path)
            if tracker_fpath is not None:
                raise NotImplementedError

    @classmethod
    def find_file_tracker(cls, path):
        assert not path.name.endswith('.dvc')
        tracker_fpath = path.augment(tail='.dvc')
        if tracker_fpath.exists():
            return tracker_fpath

    def find_dir_tracker(cls, path):
        # Find if an ancestor parent dpath is tracked
        path = ub.Path(path).absolute()
        prev = path
        dpath = path.parent
        while (not (dpath / '.dvc').exists()) and prev != dpath:
            tracker_fpath = dpath.augment(tail='.dvc')
            if tracker_fpath.exists():
                return tracker_fpath
            prev = dpath
            dpath = dpath.parent
        tracker_fpath = dpath.augment(tail='.dvc')
        if tracker_fpath.exists():
            return tracker_fpath

    def read_dvc_sidecar(self, sidecar_fpath):
        sidecar_fpath = ub.Path(sidecar_fpath)
        data = Yaml.loads(sidecar_fpath.read_text())
        return data

    def resolve_cache_paths(self, sidecar_fpath):
        """
        Given a .dvc file, enumerate the paths in the cache associated with it.

        Args:
            sidecar_fpath (PathLike | str): path to the .dvc file

        Example:
            >>> from simple_dvc.api import SimpleDVC  # NOQA
            >>> self = SimpleDVC.demo()
            >>> # on a file
            >>> sidecar_fpath = self.dpath / 'test-set1/manifest.txt.dvc'
            >>> resolved_cache_paths = list(self.resolve_cache_paths(sidecar_fpath))
            >>> print('resolved_cache_paths = {}'.format(ub.urepr(resolved_cache_paths, nl=1)))
            >>> # on a simple directory
            >>> sidecar_fpath = self.dpath / 'test-set1/assets.dvc'
            >>> resolved_cache_paths = list(self.resolve_cache_paths(sidecar_fpath))
            >>> print('resolved_cache_paths = {}'.format(ub.urepr(resolved_cache_paths, nl=1)))
            >>> # on a complex directory
            >>> sidecar_fpath = self.dpath / 'root_dir.dvc'
            >>> resolved_cache_paths = list(self.resolve_cache_paths(sidecar_fpath))
            >>> print('resolved_cache_paths = {}'.format(ub.urepr(resolved_cache_paths, nl=1)))
        """
        sidecar_fpath = ub.Path(sidecar_fpath)
        data = Yaml.loads(sidecar_fpath.read_text())

        dvc3_cache_base = (self.cache_dir / 'files/md5')
        try_dvc3 = dvc3_cache_base.exists()

        # TODO: dvc 3.0 added new hashes! Yay! But we have to support this.
        for item in data['outs']:
            md5 = item['md5']

            if try_dvc3:
                cache_fpath = self.cache_dir / 'files' / 'md5' / md5[0:2] / md5[2:]
                if not cache_fpath.exists():
                    cache_fpath = self.cache_dir / md5[0:2] / md5[2:]
            else:
                cache_fpath = self.cache_dir / md5[0:2] / md5[2:]
                if not cache_fpath.exists():
                    cache_fpath = self.cache_dir / 'files' / 'md5' / md5[0:2] / md5[2:]

            if md5.endswith('.dir') and cache_fpath.exists():
                dir_data = Yaml.loads(cache_fpath.read_text())
                for item in dir_data:
                    file_md5 = item['md5']
                    assert not file_md5.endswith('.dir'), 'unhandled'
                    if try_dvc3:
                        file_cache_fpath = self.cache_dir / 'files' / 'md5' / file_md5[0:2] / file_md5[2:]
                    else:
                        file_cache_fpath = self.cache_dir / file_md5[0:2] / file_md5[2:]

                    yield file_cache_fpath
            yield cache_fpath

    def _sidecar_references(self, sidecar_fpath):
        """
        Args:
            fpath (str | PathLike): path to a sidecar file.

        Yields:
            Dict:
                Information about each sidecar file as they are read.
        """
        import json
        sidecar_fpath = ub.Path(sidecar_fpath)
        data = Yaml.loads(sidecar_fpath.read_text())
        cache_dir = self.cache_dir
        dvc3_cache_base = (cache_dir / 'files/md5')
        assert dvc3_cache_base.exists()

        sidecar_root = sidecar_fpath.parent

        # TODO: dvc 3.0 added new hashes! Yay! But we have to support this.
        for item in data['outs']:
            md5 = item['md5']
            co_path = sidecar_root / item['path']
            item['co_path'] = os.fspath(co_path)
            item['co_path_exists'] = co_path.exists()
            cache_fpath = cache_dir / 'files' / 'md5' / md5[0:2] / md5[2:]
            item['cache_path'] = os.fspath(cache_fpath)
            item['cache_exists'] = cache_fpath.exists()
            yield item
            if md5.endswith('.dir'):
                if cache_fpath.exists():
                    dir_data = json.loads(cache_fpath.read_text())
                    # file_items = []
                    for file_item in dir_data:
                        file_md5 = file_item['md5']
                        file_co_path = co_path / file_item['relpath']
                        assert not file_md5.endswith('.dir'), 'unhandled'
                        file_cache_fpath = cache_dir / 'files' / 'md5' / file_md5[0:2] / file_md5[2:]
                        file_item['parent'] = os.fspath(cache_fpath)
                        file_item['cache_path'] = os.fspath(file_cache_fpath)
                        file_item['co_path'] = os.fspath(file_co_path)
                        file_item['cache_exists'] = file_cache_fpath.exists()
                        file_item['co_exists'] = file_co_path.exists()
                        yield file_item

    def find_sidecar_paths_in_dpath(self, dpath):
        """
        Find DVC sidecar files in a directory.

        Args:
            dpath (Path | str): directory in dvc repo to search

        Yields:
            ub.Path: existing dvc sidecar files
        """
        # TODO: handle .dvcignore
        dpath = ub.Path(dpath)
        for r, ds, fs in dpath.walk():

            # Don't recurse into directories associated with a DVC file.
            fs_set = set(fs)
            remove_idxs = []
            for idx, d in enumerate(ds):
                if d + '.dvc' in fs_set:
                    remove_idxs.append(idx)
            for idx in remove_idxs[::-1]:
                del ds[idx]

            # Otherwise yield all dvc files in the path
            for f in fs:
                if f.endswith('.dvc'):
                    yield r / f

    def find_sidecar_paths_associated_with(self, dpath):
        """
        DEPRECATE:

            Use sidecar_paths

        Args:
            dpath (Path | str): directory in dvc repo to search

        Yields:
            ub.Path: existing dvc sidecar files
        """
        # TODO: handle .dvcignore
        dpath = ub.Path(dpath)
        for r, ds, fs in dpath.walk():
            for f in fs:
                if f.endswith('.dvc'):
                    yield r / f

    def sidecars(self, path):
        """
        Generates all sidecar objects associated with a path.
        """
        from simple_dvc.sidecar import Sidecar
        for fpath in self.sidecar_paths(path):
            sidecar = Sidecar(fpath, dvc=self)
            yield sidecar

    def sidecar_paths(self, path):
        """
        Given a path in a DVC repo, resolve it to a sidecar file that it
        corresponds to.

        Cases:
            * Input is a .dvc file - return it

            * Input is a file with an associated .dvc - return the assocaited .dvc file

            * Input is inside a folder tracked by dvc - return the .dvc file of the folder

            * Input is a folder with multiple .dvc paths in it - return all .dvc files in the folder.

        If the input is a .dvc file return it.

        If it is inside a directory that corresponds to a dvc repo, search for
        that.

        Args:
            path (Path | str): directory or file in dvc repo to search

        Yields:
            ub.Path: existing dvc sidecar files

        Example:
            >>> from simple_dvc.api import SimpleDVC  # NOQA
            >>> self = SimpleDVC.demo()
            >>> #
            >>> # Calling on an untracked directory returns all sidecars in the
            >>> # directory
            >>> all_sidecars = list(self.sidecar_paths(self.dpath))
            >>> assert len(all_sidecars) > 1
            >>> #
            >>> # Calling on a tracked file in a directory returns the sidecar for
            >>> # that directory
            >>> tracked_fpath = (self.dpath / 'test-set1/assets').ls()[0]
            >>> dir_sidecar = list(self.sidecar_paths(tracked_fpath))
            >>> assert len(dir_sidecar) == 1
            >>> #
            >>> # Calling on a dvc file returns the dvc file
            >>> asset_dvc_fpath = (self.dpath / 'test-set1/assets.dvc')
            >>> found_sidecars = list(self.sidecar_paths(asset_dvc_fpath))
            >>> assert found_sidecars == [asset_dvc_fpath]
            >>> #
            >>> # Calling on a tracked file returns the dvc file
            >>> manifest_dvc_fpath = (self.dpath / 'test-set1/manifest.txt.dvc')
            >>> manifest_fpath = (self.dpath / 'test-set1/manifest.txt')
            >>> found_sidecars = list(self.sidecar_paths(manifest_dvc_fpath))
            >>> assert found_sidecars == [manifest_dvc_fpath]
            >>> found_sidecars = list(self.sidecar_paths(manifest_fpath))
            >>> assert found_sidecars == [manifest_dvc_fpath]
        """
        # TODO: handle .dvcignore
        path = ub.Path(path).absolute()
        if path.name.endswith('.dvc'):
            yield path
        elif path.augment(tail='.dvc').exists():
            yield path.augment(tail='.dvc')
        else:
            cand = self.find_dir_tracker(path)
            if cand is not None:
                yield cand
            else:
                if path.is_dir():
                    yield from self.find_sidecar_paths_in_dpath(path)


def _ensure_iterable(inputs):
    return inputs if ub.iterable(inputs) else [inputs]


def _import_dvc_main():
    try:
        from dvc import main as dvc_main_mod
        dvc_main = dvc_main_mod.main
    except (ImportError, ModuleNotFoundError):
        from dvc.cli import main as dvc_main
    return dvc_main


SDVC = SimpleDVC
