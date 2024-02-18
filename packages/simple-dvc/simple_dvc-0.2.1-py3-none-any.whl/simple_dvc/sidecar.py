"""
Custom implementation of sidecar files.

Sidecar files can refernces reference "Out" objects, which directly correspond
to cached assets or "directories", which are a list of assets. Our
implementation assumes there is only one level of indirection --- i.e.  a
directory "out" will only refernce file-based outs.
"""
import ubelt as ub


def find_unreferenced_data(self):
    """
    TODO: move this elsewhere.

    Ignore:
        >>> from simple_dvc.api import SimpleDVC  # NOQA
        >>> self = SimpleDVC.coerce('.')
    """
    import ubelt as ub
    all_sidecar_fpaths = list(ub.ProgIter(self.find_sidecar_paths_in_dpath(self.dpath), desc='find all sidecars'))

    referenced_cache_fpaths = []
    for fpath in ub.ProgIter(all_sidecar_fpaths, desc='reading sidecars'):
        referenced_cache_fpaths += list(self.resolve_cache_paths(fpath))

    legacy_cache_fpaths = list(ub.flatten([p.ls() for p in self.cache_dir.ls() if p.name != 'files']))

    existing_cache_fpaths = list(self.cache_dir.glob('files/md5/*/*'))

    unreferenced_cache_fpaths = set(existing_cache_fpaths) - set(referenced_cache_fpaths)

    len(unreferenced_cache_fpaths)
    len(existing_cache_fpaths)
    len(referenced_cache_fpaths)

    md5_to_cache_path = ub.udict({p.parent.name + p.name: p for p in existing_cache_fpaths})
    md5_to_legacy_path = ub.udict({p.parent.name + p.name: p for p in legacy_cache_fpaths})
    md5_to_referenced_path = ub.udict({p.parent.name + p.name: p for p in referenced_cache_fpaths})

    for p in md5_to_cache_path.values():
        if p.is_symlink():
            print(p)

    for p in md5_to_legacy_path.values():
        if p.is_symlink():
            print(p)

    legacy_and_updated = (md5_to_cache_path & md5_to_legacy_path)
    legacy_or_updated = (md5_to_legacy_path | md5_to_cache_path)
    md5_to_unreferenced = legacy_or_updated - md5_to_referenced_path

    existing_referenced = md5_to_referenced_path & legacy_or_updated

    legacy_only = md5_to_legacy_path - md5_to_cache_path
    updated_only = md5_to_cache_path - md5_to_legacy_path

    print(f'{len(updated_only)=          }')
    print(f'{len(legacy_only)=           }')
    print(f'{len(legacy_and_updated)=    }')
    print(f'{len(legacy_or_updated)=     }')
    print(f'{len(md5_to_unreferenced)=   }')
    print(f'{len(md5_to_referenced_path)=}')
    print(f'{len(existing_referenced)=   }')


class Out(ub.UDict):
    """
    Wrapper for a DVC out dictionary.

    An "Out" is a dictionary that contains the expected hash of some piece of
    data as well as a relative path that indicates where it should live.

    Example:
        >>> out = Out({'md5': 'badbeaf', 'path': 'baz'})
        >>> out.is_dir
        >>> out.rel_cache_fpath
    """

    @property
    def is_dir(self):
        return self['md5'].endswith('.dir')

    @property
    def rel_cache_fpath(self):
        md5 = self['md5']
        rel_cache_fpath = ub.Path('files/md5') / md5[0:2] / md5[2:]
        return rel_cache_fpath


class Sidecar(ub.NiceRepr):
    """
    Class that handles information stored in a .dvc sidecar file.

    Given the additional context of a DVC repo, this provides the ability to
    check if the referenced data exists, pull it, or check it out. This does
    not perform any safety checks, which means it is faster than regular DVC,
    but the user must be careful becuase its lack of saftey means you can break
    things.

    Ignore:
        self = Sidecar(ub.Path('KW_C001_CLUSTER_000/S2.dvc').resolve(), dvc)
        self._load_all()
        print(self.summary())

        from simple_dvc.sidecar import *  # NOQA
        path = ub.Path('/media/joncrall/flash1/smart_drop7/Drop7-Cropped2GSD-V2/KW_C001/imgonly-KW_C001-rawbands.kwcoco.zip.dvc')
        dvc = SimpleDVC.coerce(path)
        self = Sidecar(path, dvc)
        self._load_all()
        print(self.summary())
    """

    def __init__(self, fpath, dvc):
        self.fpath = fpath
        self.dvc = dvc
        self._data = None

        self._main_loaded = None

        """
        Note:
            A sidecar contains two direct references:

                * Reference to specific-file outs (usually just one)

                * Reference to a directory outs, which is a file that
                  contains a list of references

            The directory outs are a list of indirect refrences and thse are
            stored in subdir_outs
        """

        self._main_file_outs = []
        self._main_file_out_groups = {
            'done': False,
            'exists': [],
            'missing': [],
        }

        self._main_dir_outs = []
        self._main_dir_out_groups = {
            'done': False,
            'exists': [],
            'missing': [],
        }

        self._subdir_outs = []
        self._sub_file_out_groups = {
            'done': False,
            'exists': [],
            'missing': [],
        }

        self._linked_pairs = []
        self._linked_pair_groups = {
            'done': False,
            'exists': [],
            'missing': [],
        }

        self.rel_fpath = self.fpath.relative_to(dvc.dpath.resolve())
        self._main_type = None

    @property
    def num_subdirs(self):
        assert self._main_loaded
        return len(self._main_dir_outs)

    @property
    def num_main_files(self):
        assert self._main_loaded
        return len(self._main_file_outs)

    def __nice__(self):
        return self.fpath

    def summary(self):
        stats = {
            'type': self._main_type,
        }

        def populate_stats_key(key, groups, stats):
            if groups['done']:
                stats['num_' + key + '_missing'] = len(groups['missing'])
                stats['num_' + key + '_exists'] = len(groups['exists'])
            else:
                stats[key + '_stats'] = 'UNPARSED'

        if self._main_loaded:
            if self._main_file_outs:
                groups = self._main_file_out_groups
                key = 'file_outs'
                populate_stats_key(key, groups, stats)

            if self._main_dir_outs:
                groups = self._main_dir_out_groups
                key = 'dir_outs'
                populate_stats_key(key, groups, stats)

                groups = self._sub_file_out_groups
                key = 'subfile_outs'
                populate_stats_key(key, groups, stats)

            groups = self._linked_pair_groups
            key = 'linked'
            populate_stats_key(key, groups, stats)

        else:
            stats['main_stats'] = 'UNPARSED'

        return stats

    def _load_all(self):
        self._load_main()
        self._group_file_outs()
        self._group_dir_outs()
        self._load_and_group_subdir_files()
        self._group_linked_pairs()

    def _load_main(self):
        """
        Loads pointers from the main sidecar file.

        If this contains directories, then there still may be more data to
        load.
        """
        from kwutil.util_yaml import Yaml
        self._main_file_outs.clear()
        self._main_dir_outs.clear()
        try:
            self._data = Yaml.loads(self.fpath.read_text())
        except IOError:
            self._main_loaded = False
        else:
            self._main_loaded = True
            outs = self._data['outs']
            for out in map(Out, outs):
                if out.is_dir:
                    self._main_dir_outs.append(out)
                else:
                    self._main_file_outs.append(out)

            nfiles = len(self._main_file_outs)
            ndirs = len(self._main_dir_outs)
            if nfiles > 0 and ndirs > 0:
                self._main_type = 'mixed'
            elif nfiles > 0 and ndirs == 0:
                self._main_type = 'file'
            elif nfiles == 0 and ndirs > 0:
                self._main_type = 'dir'
            else:
                self._main_type = 'unknown'

    def _group_file_outs(self):
        """
        Determine which file outputs exist / are missing
        """
        self._main_file_out_groups = {
            'done': True,
            'exists': [],
            'missing': [],
        }
        cache_dpath = self.dvc.cache_dir
        for out in self._main_file_outs:
            local_cache_fpath = cache_dpath / out.rel_cache_fpath
            if local_cache_fpath.exists():
                self._main_file_out_groups['exists'].append(out)
            else:
                self._main_file_out_groups['missing'].append(out)

    def _group_dir_outs(self):
        """
        Determine which directory outputs exist / are missing
        """
        self._main_dir_out_groups = {
            'done': True,
            'exists': [],
            'missing': [],
        }
        cache_dpath = self.dvc.cache_dir
        for out in self._main_dir_outs:
            local_cache_fpath = cache_dpath / out.rel_cache_fpath
            if local_cache_fpath.exists():
                self._main_dir_out_groups['exists'].append(out)
            else:
                self._main_dir_out_groups['missing'].append(out)

    def _load_and_group_subdir_files(self):
        """
        For existing directory outputs, loads them and determines if their
        contents are missing

        print('self._sub_file_out_groups = {}'.format(ub.urepr(self._sub_file_out_groups, nl=3)))
        """
        from kwutil.util_yaml import Yaml
        if not self._main_dir_out_groups['done']:
            self._group_dir_outs()

        cache_dpath = self.dvc.cache_dir
        self._subdir_outs = []
        for dir_out in self._main_dir_out_groups['exists']:
            local_cache_fpath = cache_dpath / dir_out.rel_cache_fpath
            _subouts = Yaml.loads(local_cache_fpath.read_text())
            _subouts = [Out(out) for out in _subouts]
            self._subdir_outs.append((dir_out, _subouts))

        self._sub_file_out_groups = {
            'done': True,
            'exists': [],
            'missing': [],
        }
        for dir_out, subouts in self._subdir_outs:
            for out in subouts:
                rel_cache_fpath = out.rel_cache_fpath
                abs_cache_fpath = cache_dpath / rel_cache_fpath
                if abs_cache_fpath.exists():
                    self._sub_file_out_groups['exists'].append((dir_out, out))
                else:
                    self._sub_file_out_groups['missing'].append((dir_out, out))

    def _iter_linked_pairs(self):
        """
        Yields:
            Tuple[Path, Path] -
                the target checkout link path and the cache path it should
                point to
        """
        cache_dpath = self.dvc.cache_dir
        self_dpath = self.fpath.parent

        if len(self._subdir_outs):
            for dir_out, out in self._sub_file_out_groups['exists']:
                abs_file_fpath = self_dpath / dir_out['path'] / out['relpath']
                abs_cache_fpath = cache_dpath / out.rel_cache_fpath
                yield (abs_cache_fpath, abs_file_fpath)

        if len(self._main_file_outs):
            for out in self._main_file_out_groups['exists']:
                abs_file_fpath = self_dpath / out['path']
                abs_cache_fpath = cache_dpath / out.rel_cache_fpath
                yield (abs_cache_fpath, abs_file_fpath)

    def _group_linked_pairs(self):
        self._linked_pairs = list(self._iter_linked_pairs())
        self._linked_pair_groups = {
            'done': True,
            'exists': [],
            'missing': [],
        }
        for pair in self._linked_pairs:
            link_fpath = pair[1]
            if link_fpath.exists():
                self._linked_pair_groups['exists'].append(pair)
            else:
                self._linked_pair_groups['missing'].append(pair)

    def unsafe_checkout(self):
        """
        Unsafe custom checkout logic
        """
        seen_dpaths = set()
        for cache_fpath, link_fpath in self._iter_linked_pairs():
            dst_dpath = link_fpath.parent
            if dst_dpath not in seen_dpaths:
                dst_dpath.ensuredir()
                seen_dpaths.add(dst_dpath)
            ub.symlink(real_path=cache_fpath, link_path=link_fpath, overwrite=True)

    # def _missing_outs(sidecar):
    #     needs_pull_outs = []
    #     needs_pull_outs.extend(sidecar._main_file_out_groups['missing'])
    #     needs_pull_outs.extend([t[1] for t in sidecar._sub_file_out_groups['missing']])
    #     # Note: if this is populated we likely need to handle the references
    #     # after we pull them down.
    #     needs_pull_outs.extend(sidecar._main_dir_out_groups['missing'])
    #     sidecar._linked_pair_groups['missing']

    # def unsafe_pull(self):
    #     """
    #     Directly pull data for this sidecar only.
    #     """


class SidecarCollection(list):

    @classmethod
    def from_paths(cls, paths, dvc):
        return cls(Sidecar(p, dvc) for p in paths)

    def _load_sidecars(sidecars, check_links=False):
        from kwutil import util_progress
        stats = ub.ddict(int)
        pman = util_progress.ProgressManager()
        with pman:

            sidecars.subdirs = subdirs = []
            sidecars.mainfiles = mainfiles = []

            for sidecar in pman.progiter(sidecars, desc='read top-level sidecars'):
                sidecar._load_main()
                stats[sidecar._main_type] += 1
                if sidecar.num_subdirs:
                    subdirs.append(sidecar)
                if sidecar.num_main_files:
                    mainfiles.append(sidecar)
                pman.update_info(ub.urepr(stats))

            if mainfiles:
                for sidecar in pman.progiter(mainfiles, desc='read main files'):
                    sidecar._group_file_outs()
                    for k, v in sidecar.summary().items():
                        if k.startswith('num_file_outs'):
                            stats[k] += v
                    pman.update_info(ub.urepr(stats))

            if subdirs:
                for sidecar in pman.progiter(subdirs, desc='read subdirs'):
                    sidecar._load_and_group_subdir_files()

                    for k, v in sidecar.summary().items():
                        if k.startswith('num'):
                            stats[k] += v
                    pman.update_info(ub.urepr(stats))

            if check_links:
                for sidecar in pman.progiter(sidecars, desc='check links'):
                    sidecar._group_linked_pairs()
                    for k, v in sidecar.summary().items():
                        if k.startswith('num_linked'):
                            stats[k] += v
                    pman.update_info(ub.urepr(stats))

    def unsafe_pull(sidecars, remote_name):
        """
        Custom simple implementation of pull that cuts corners

        Pulls data from one cache to this local one.

        Ignore:
            remote_name = 'namek_ssd'
        """
        from simple_dvc import util_fsspec

        dvc = sidecars[0].dvc
        remotes = dvc.list_remotes(name=remote_name)
        remote = remotes[0]
        remote_uri = remote['uri']

        remote_cache_dpath = util_fsspec.FSPath.coerce(remote_uri)

        needs_pull_outs = []
        # good_sidecars = []
        for sidecar in sidecars:
            needs_pull_outs.extend(sidecar._main_file_out_groups['missing'])
            needs_pull_outs.extend([t[1] for t in sidecar._sub_file_out_groups['missing']])
            # Note: if this is populated we likely need to handle the references
            # after we pull them down.
            needs_pull_outs.extend(sidecar._main_dir_out_groups['missing'])

        # ub.dict_hist([s.fpath.parent.name.split('CLUSTER')[0] for s in good_sidecars])
        # ub.dict_hist([s.fpath.parent.name.split('CLUSTER')[0] for s in needs_update_sidecars])
        # missing_cache_fpaths = []
        # for s in needs_update_sidecars:
        #     missing_cache_fpaths.extend(s._missing_subdata_cache_fpaths)
        #     missing_cache_fpaths.extend(s.missing_file_cache_fpaths)

        dst_src_pairs = []
        local_cache_dpath = util_fsspec.LocalPath(dvc.cache_dir)
        for out in ub.ProgIter(needs_pull_outs):
            rel_fpath = out.rel_cache_fpath
            local_fpath = local_cache_dpath / rel_fpath
            remote_fpath = remote_cache_dpath / rel_fpath
            dst = local_fpath
            src = remote_fpath
            dst_src_pairs.append((dst, src))

            if 0:
                import fsspec
                if remote_fpath.exists():
                    dst = local_fpath
                    src = remote_fpath
                    callback = fsspec.callbacks.TqdmCallback()
                    src.fs.get_file(src, dst, callback=callback)
                # remote_fpath.copy(dst)

        if remote_cache_dpath.__protocol__ == 'ssh':
            # We are going to hack to attempt faster copy speeds We abuse the fact
            # that many items will be copied into the same folder and the splitting
            # of that is about random.
            cache_group_to_pairs = ub.group_items(dst_src_pairs, key=lambda t: t[0].parent)
            cache_group_to_pairs = ub.udict(cache_group_to_pairs)
            cache_group_to_pairs.map_values(len)
            tmp_dpath = ub.Path.appdir('simple_dvc/file_transfer_dir').delete().ensuredir()
            commands = []
            for dst_dpath, pairs in ub.ProgIter(list(cache_group_to_pairs.items()), desc='write transfer data'):
                src_fnames = [t[1].name for t in pairs]
                src_dpaths = {t[1].parent for t in pairs}
                assert len(src_dpaths) == 1
                src_dpath = list(src_dpaths)[0]
                hash_name = ub.hash_data(dst_dpath)
                text = '\n'.join(src_fnames)
                file_fpath = tmp_dpath / hash_name
                file_fpath.write_text(text)
                command = f'rsync -va --files-from={file_fpath} namek:{src_dpath} {dst_dpath}'
                commands.append(command)

            import cmd_queue
            queue = cmd_queue.Queue.create(backend='tmux', size=8)
            for command in commands:
                queue.submit(command)
            queue.print_commands()
            queue.run()
        else:
            # TODO: should parallize this
            import fsspec
            for dst, src in ub.ProgIter(dst_src_pairs, desc='simple-dvc pull', verbose=3):
                if not dst.exists() and src.exists():
                    callback = fsspec.callbacks.TqdmCallback()
                    src.fs.get_file(src, dst, callback=callback)

    def unsafe_checkout(sidecars):
        for sidecar in ub.ProgIter(sidecars, desc='custom checkout'):
            # if sidecar._main_file_outs:
            #     break
            sidecar.unsafe_checkout()


def simple_checkout():
    from simple_dvc.api import SimpleDVC  # NOQA
    import ubelt as ub
    dpath = '.'
    dvc = SimpleDVC.coerce(dpath)
    all_sidecar_fpaths = list(ub.ProgIter(dvc.find_sidecar_paths_in_dpath(dpath), desc='find all sidecars'))
    found_sidecars = list(ub.ProgIter(all_sidecar_fpaths, desc='find sidecars'))
    sidecars = []
    for fpath in ub.ProgIter(found_sidecars, desc='reading sidecars'):
        sidecar = Sidecar(fpath.resolve(), dvc)
        sidecars.append(sidecar)
    sidecars = SidecarCollection(sidecars)
    sidecars._load_sidecars(check_links=True)

    sidecars.unsafe_pull(remote_name='namek_ssd')
    sidecars.unsafe_checkout()


def unsafe_pull_and_checkout():
    import ubelt as ub
    from simple_dvc.api import SimpleDVC  # NOQA
    from simple_dvc.sidecar import SidecarCollection  # NOQA
    import glob
    pattern = '*/*.kwcoco.*'
    pattern = '*/*/*.dvc'
    paths = list(map(ub.Path, glob.glob(pattern)))
    assert len(paths) > 0
    dvc = SimpleDVC.coerce(paths[0])
    sidecar_fpaths = list(ub.flatten([list(dvc.sidecar_paths(p)) for p in paths]))
    sidecars = SidecarCollection.from_paths(sidecar_fpaths, dvc)
    sidecars._load_sidecars(check_links=True)

    remote_name = 'aws'
    remote_name = 'namek_ssd'
    remote_name = 'toothbrush_ssd'
    sidecars.unsafe_pull(remote_name=remote_name)

    sidecars_with_missing_links = []
    for s in sidecars:
        if s._linked_pair_groups['missing']:
            sidecars_with_missing_links.append(s)
    tolink_sidecars = SidecarCollection(sidecars_with_missing_links)
    tolink_sidecars.unsafe_checkout()

    # sidecars.unsafe_checkout()


def find_and_fix_missing_files():
    """
    Find DVC files where the data hasn't been checked out yet.

    Ignore:
        import sys, ubelt
        sys.path.append(ubelt.expandpath('~/code/simple_dvc'))
        from simple_dvc.sidecar import *  # NOQA

    """
    from simple_dvc.api import SimpleDVC  # NOQA
    from simple_dvc.sidecar import Sidecar, SidecarCollection
    import ubelt as ub
    dpath = '.'
    dvc = SimpleDVC.coerce(dpath)
    all_sidecar_fpaths = list(ub.ProgIter(dvc.find_sidecar_paths_in_dpath(dpath), desc='find all sidecars'))
    found_sidecars = list(ub.ProgIter(all_sidecar_fpaths, desc='find sidecars'))
    sidecars = []
    for fpath in ub.ProgIter(found_sidecars, desc='reading sidecars'):
        # if 'SA_' in str(fpath):
        # if 'kwcoco' in fpath.name:
        fpath = fpath.resolve()
        if 1:
            # if fpath.name in {'S2.dvc', 'WV.dvc', 'WV1.dvc'}:
            # if fpath.name in {'WV1.dvc'}:
            # if not fpath.augment(ext='').exists():
            sidecar = Sidecar(fpath, dvc)
            sidecars.append(sidecar)
    sidecars = SidecarCollection(sidecars)
    sidecars._load_sidecars()

    sidecars.unsafe_pull()

    for sidecar in ub.ProgIter(sidecars, desc='custom checkout'):
        sidecar.unsafe_checkout()

    # needs_update_sidecars = []
    # good_sidecars = []
    # for sidecar in sidecars:
    #     if len(sidecar.missing_file_cache_fpaths):
    #         needs_update_sidecars.append(sidecar)
    #     if len(sidecar._missing_subdata_cache_fpaths):
    #         needs_update_sidecars.append(sidecar)
    #     else:
    #         good_sidecars.append(sidecar)

    # ub.dict_hist([s.fpath.parent.name.split('CLUSTER')[0] for s in good_sidecars])
    # ub.dict_hist([s.fpath.parent.name.split('CLUSTER')[0] for s in needs_update_sidecars])

    # missing_cache_fpaths = []
    # for s in needs_update_sidecars:
    #     missing_cache_fpaths.extend(s._missing_subdata_cache_fpaths)

    # #### HACKS TO TRY AND MANUALLY GRAB THINGS
    # remote_url = '/flash/smart_drop7/.dvc/cache'
    # from watch.utils import util_fsspec
    # fs = util_fsspec.SSHPath._new_fs(host='namek.kitware.com')
    # remote_cache_dpath = util_fsspec.FSPath(remote_url, fs=fs)
    # local_cache_dpath = dvc.cache_dir

    # dst_src_pairs = []
    # for local_fpath in ub.ProgIter(missing_cache_fpaths):
    #     rel_fpath = local_fpath.relative_to(dvc.cache_dir)
    #     remote_fpath = remote_cache_dpath / rel_fpath
    #     dst_src_pairs.append((local_fpath, remote_fpath))

    #     if 0:
    #         remote_fpath.exists()
    #         dst = util_fsspec.LocalPath(local_fpath)
    #         src = remote_fpath
    #         src.fs.get_file(src, dst)
    #         # remote_fpath.copy(dst)

    # # We are going to hack to attempt faster copy speeds We abuse the fact that
    # # many items will be copied into the same folder and the splitting of that
    # # is about random.
    # cache_group_to_pairs = ub.group_items(dst_src_pairs, key=lambda t: t[0].parent)
    # cache_group_to_pairs = ub.udict(cache_group_to_pairs)
    # cache_group_to_pairs.map_values(len)

    # tmp_dpath = ub.Path.appdir('simple_dvc/file_transfer_dir').delete().ensuredir()
    # commands = []
    # for dst_dpath, pairs in ub.ProgIter(list(cache_group_to_pairs.items()), desc='write transfer data'):
    #     src_fnames = [t[1].name for t in pairs]
    #     src_dpaths = {t[1].parent for t in pairs}
    #     assert len(src_dpaths) == 1
    #     src_dpath = list(src_dpaths)[0]
    #     hash_name = ub.hash_data(dst_dpath)
    #     text = '\n'.join(src_fnames)
    #     file_fpath = tmp_dpath / hash_name
    #     file_fpath.write_text(text)
    #     command = f'rsync -va --files-from={file_fpath} namek:{src_dpath} {dst_dpath}'
    #     commands.append(command)

    # import cmd_queue
    # queue = cmd_queue.Queue.create(backend='tmux', size=8)
    # for command in commands:
    #     queue.submit(command)
    # queue.print_commands()
    # queue.run()

    # pullable = []
    # unpullable = []
    # for sidecar in ub.ProgIter(has_subdir_to_sidecars[False]):
    #     print(f'sidecar={sidecar}')

    #     for rel_fpath in list(sidecar._top_level_rel_cache_paths()):
    #         local_cache_fapth = local_cache_dpath / rel_fpath
    #         remote_cache_fpath = remote_cache_dpath / rel_fpath
    #         if remote_cache_fpath.exists():
    #             pullable.append(
    #                 (local_cache_fapth, remote_cache_fpath)
    #             )
    #         else:
    #             unpullable.append(
    #                 (local_cache_fapth, remote_cache_fpath)
    #             )

    # """
    # /media/joncrall/flash1/smart_drop7/.dvc/cache/files/md5/ea/97baa46fe2de460499f9ee6316602b.dir
    # /media/joncrall/flash1/smart_drop7/Drop7-Cropped2GSD-V2/CN_C001/CN_C001_CLUSTER_377/
    # """

    # for dst, src in ub.ProgIter(pullable):
    #     dst = util_fsspec.LocalPath(dst)
    #     src.fs.get_file(src, dst)
    #     # src.copy(dst)
    #     ...

    # # Def manual pull
    # if not local_cache_fapth.exists():
    #     local_cache_fapth = util_fsspec.LocalPath(local_cache_fapth)
    #     remote_cache_fpath.copy(local_cache_fapth)
    #     remote_cache_fpath.fs.get_file(remote_cache_fpath, local_cache_fapth)
