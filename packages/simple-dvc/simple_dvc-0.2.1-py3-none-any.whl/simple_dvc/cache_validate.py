#!/usr/bin/env python3
import scriptconfig as scfg
"""
The following describes a DVC Error I ran into.

    The cache files were corrupted, and dvc does not seem to have a way to
    check for this (so I wrote this script).

    But after I removed the corrupted cache files on machine2, I tried to push
    them from machine1 (with a good cache) to machine2, but dvc didn't realize
    that machine1 had files that machine2 was missing. Perhaps this is because
    the missing files were behind a .dir object in the cache?

It would be good to get a MWE for this.
"""

import ubelt as ub


class DvcCacheValidateCLI(scfg.DataConfig):
    """
    Checks for corruption in the dvc cache.
    """
    __command__ = 'cache_validate'
    path = scfg.Value(None, help='path to a dvc repo or file to validate the cache for', position=1)

    @classmethod
    def main(cls, cmdline=1, **kwargs):
        """
        Ignore:
            from simple_dvc.cache_validate import *
            path = '/home/joncrall/remote/toothbrush/data/dvc-repos/smart_data_dvc-ssd/Drop7-Cropped2GSD'
            path = '/data/joncrall/dvc-repos/smart_data_dvc/Drop7-Cropped2GSD'
            cmdline = 0
            kwargs = dict(path=path)
            cls = DvcCacheValidateCLI

        Example:
            >>> # xdoctest: +SKIP
            >>> from simple_dvc.cache_validate import *  # NOQA
            >>> cmdline = 0
            >>> kwargs = dict(path='.')
            >>> cls = DvcCacheValidateCLI
            >>> cls.main(cmdline=cmdline, **kwargs)
        """
        import rich
        config = cls.cli(cmdline=cmdline, data=kwargs, strict=True)
        rich.print('config = ' + ub.urepr(config, nl=1))

        from simple_dvc import SimpleDVC
        dvc = SimpleDVC.coerce(config.path)
        rich.print(f'config.path: [link={config.path}]{config.path}[/link]')
        rich.print(f'dvc.dvc_root: [link={dvc.dvc_root}]{dvc.dvc_root}[/link]')
        rich.print(f'dvc.cache_dir: [link={dvc.cache_dir}]{dvc.cache_dir}[/link]')

        # list(dvc.find_file_tracker(ub.Path(config.path).absolute()))

        # TODO: better way to list all the cache files associated with a
        # directory or a dvc file.
        path = ub.Path(config.path).absolute()
        sidecar_paths = list(ub.ProgIter(dvc.sidecar_paths(path), desc='list sidecars'))

        corrupt_checks = True

        corrupt_fpaths = []
        valid_fpaths = []
        missing_fpaths = []
        maybe_valid_fpaths = []

        # if 0:
        #     for d in valid_fpaths:
        #         if d['cache_fpath'].name == '5e6e84d75213fd149aa6956935dce5.dir':
        #             raise Exception

        for sidecar_fpath in ub.ProgIter(sidecar_paths, verbose=3, desc='iter sidecars'):
            print('sidecar_fpath = {}'.format(ub.urepr(sidecar_fpath, nl=1)))
            # print(f'{len(corrupt_fpaths)=}')
            # print(f'{len(valid_fpaths)=}')
            # print(f'{len(missing_fpaths)=}')
            # print(f'{len(maybe_valid_fpaths)=}')
            for cache_fpath in dvc.resolve_cache_paths(sidecar_fpath):
                item = {'cache_fpath': cache_fpath, 'sidecar_fpath': sidecar_fpath}
                if not cache_fpath.exists():
                    print('issue with cache_fpath = {}'.format(ub.urepr(cache_fpath, nl=1)))
                    missing_fpaths.append(item)
                else:
                    is_dirfile = cache_fpath.name.endswith('.dir')
                    if corrupt_checks:
                        md5_hash = ub.hash_file(cache_fpath, hasher='md5')
                        prefix, suffix = md5_hash[0:2], md5_hash[2:]
                        if is_dirfile:
                            suffix = suffix + '.dir'
                        file_prefix = cache_fpath.parent.name
                        file_suffix = cache_fpath.name
                        if prefix != file_prefix or suffix != file_suffix:
                            print('CORRUPT FILE: ' + str(cache_fpath))
                            corrupt_fpaths.append(item)
                        else:
                            valid_fpaths.append(item)
                    else:
                        maybe_valid_fpaths.append(item)

        do_delete = 0
        if do_delete:
            for p in corrupt_fpaths:
                p.delete()

        if 0:
            from kwutil.copy_manager import CopyManager
            cman = CopyManager()

            seen_ = set()

            # A hacky fixup for missing files
            existing_cache_dir = ub.Path('/home/joncrall/remote/toothbrush/data/dvc-repos/smart_data_dvc/.dvc/cache')
            for info in ub.ProgIter(missing_fpaths):
                info['cache_fpath'].exists()

                rel_fpath = info['cache_fpath'].relative_to(dvc.cache_dir)
                if not rel_fpath.startswith('files/md5'):
                    rel_fpath = ub.Path('files/md5') / rel_fpath

                other_fpath = (existing_cache_dir / rel_fpath)
                this_fpath = dvc.cache_dir / rel_fpath

                if this_fpath.exists():
                    continue

                if this_fpath in seen_:
                    print("skip")
                    continue
                seen_.add(this_fpath)

                assert other_fpath.exists()
                assert not this_fpath.exists()
                assert info['sidecar_fpath'].exists()
                cman.submit(other_fpath, this_fpath)

            print(f'Copying {len(cman)} files')
            cman.run()


def find_cached_fpaths(dvc, dpath):
    for fpath in dvc.find_sidecar_paths(dpath):
        yield from dvc.resolve_cache_paths(ub.Path(fpath))


r"""
Notes:

    raw_bands/QA_C001/ave_B05_B06_B07_B09_B8A_blue_cirrus_coastal_green_nir_red_swir16_swir22/ave_20170301T070000Z_049_B05_B06_B07_B09_B8A_blue_cirrus_coastal_green_nir_red_swir16_swir22_S2_595ec869d8df6b23_a313a3e080fccf50.tif


tofix = '''
63/9de8ed3afd3f739e652b28f0c4fcbc
d3/40f349ada479900e95ee0028bf1695
67/c9d784622d3eaed3608d46c941e22d
64/9b8af71be219bec8bf370ce65c4235
51/7de88c346d6493225013594da02643
57/113aa658d600f7e49242e06df1a346
1d/4a2102b434cf17cc61e3071d62190f
96/6154ab7ed358cebb77822f7020a784
22/6fee2363722bcbd2b7599c290a9199
d3/5eea786fe4a20ead51dff651df6fef
'''.strip().split('\n')


p1 = '/home/joncrall/remote/namek/data/dvc-repos/smart_data_dvc/.dvc/cache/files/md5/'
p2 = '/media/joncrall/flash1/smart_data_dvc/.dvc/cache/files/md5/'


for s in tofix:
    src = 'namek:' + p1 + s
    dst = p2 + s
    command = f'scp {src} {dst}'
    # command = f'rm {dst}'
    print(command)


rsync -avpr

63/9de8ed3afd3f739e652b28f0c4fcbc

    63/9de8ed3afd3f739e652b28f0c4fcbc
    /media/joncrall/flash1/smart_data_dvc/.dvc/cache/files/md5/d3/40f349ada479900e95ee0028bf1695
    /media/joncrall/flash1/smart_data_dvc/.dvc/cache/files/md5/67/c9d784622d3eaed3608d46c941e22d
    /media/joncrall/flash1/smart_data_dvc/.dvc/cache/files/md5/64/9b8af71be219bec8bf370ce65c4235
    /media/joncrall/flash1/smart_data_dvc/.dvc/cache/files/md5/51/7de88c346d6493225013594da02643
    /media/joncrall/flash1/smart_data_dvc/.dvc/cache/files/md5/57/113aa658d600f7e49242e06df1a346
    /media/joncrall/flash1/smart_data_dvc/.dvc/cache/files/md5/1d/4a2102b434cf17cc61e3071d62190f
    /media/joncrall/flash1/smart_data_dvc/.dvc/cache/files/md5/96/6154ab7ed358cebb77822f7020a784
    /media/joncrall/flash1/smart_data_dvc/.dvc/cache/files/md5/22/6fee2363722bcbd2b7599c290a9199
    /media/joncrall/flash1/smart_data_dvc/.dvc/cache/files/md5/d3/5eea786fe4a20ead51dff651df6fef



"""


__cli__ = DvcCacheValidateCLI
main = __cli__.main

if __name__ == '__main__':
    """

    CommandLine:
        python ~/code/watch/dev/poc/dvc_cache_validate.py
        python -m dvc_cache_validate
    """
    main()
