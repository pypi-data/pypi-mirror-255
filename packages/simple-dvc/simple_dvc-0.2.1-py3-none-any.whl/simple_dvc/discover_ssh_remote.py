#!/usr/bin/env python3
"""
The idea is ssh into the remote, check where the cache dir is, and then set it
correctly on our end. This requires that the DVC repo is in the same location
relative to the home dir on the remote machine, but otherwise assumptions are
minimal.
"""
from os.path import normpath
from os.path import realpath
from os.path import expanduser
from os.path import relpath
import os
import ubelt as ub
import scriptconfig as scfg


class DiscoverSshRemoteCLI(scfg.DataConfig):
    """
    If you have a DVC repo checked out on another machine with the same
    directory layout (with respect to your home drive) as this machine, then
    this command finds the location of the cache on that remote machine and
    adds an appropriate DVC remote in this repo that references it.
    """
    __command__ = 'discover_ssh_remote'

    host = scfg.Value(None, position=1, required=True, help=ub.paragraph(
            '''
            Server to sync to via ssh (e.g. user@servername.edu)
            '''))
    forward_ssh_agent = scfg.Value(False, isflag=True, short_alias=['A'], help=ub.paragraph(
            '''
            Enable forwarding of the ssh authentication agent connection
            '''))
    dry = scfg.Value(False, isflag=True, short_alias=['n'], help='Perform a dry run')
    force = scfg.Value(False, isflag=True, help='Force push and hard reset the remote.')

    @classmethod
    def main(cls, cmdline=1, **kwargs):
        """
        Example:
            >>> # xdoctest: +SKIP
            >>> from simple_dvc.discover_ssh_remote import *  # NOQA
            >>> cmdline = 0
            >>> kwargs = dict()
            >>> cls = DiscoverSshRemoteCLI
            >>> cls.main(cmdline=cmdline, **kwargs)
        """
        import rich
        config = cls.cli(cmdline=cmdline, data=kwargs, strict=True)
        rich.print('config = ' + ub.urepr(config, nl=1))
        dvc_discover_ssh_remote(**config)

__cli__ = DiscoverSshRemoteCLI
main = __cli__.main


def _getcwd():
    """
    Workaround to get the working directory without dereferencing symlinks.
    This may not work on all systems.

    References:
        https://stackoverflow.com/questions/1542803/getcwd-dereference-symlinks
    """
    # TODO: use ubelt version if it lands
    canidate1 = os.getcwd()
    real1 = normpath(realpath(canidate1))

    # test the PWD environment variable
    candidate2 = os.getenv('PWD', None)
    if candidate2 is not None:
        real2 = normpath(realpath(candidate2))
        if real1 == real2:
            # sometimes PWD may not be updated
            return candidate2
    return canidate1


def git_default_push_remote_name():
    local_remotes = ub.cmd('git remote -v')['out'].strip()
    lines = [line for line in local_remotes.split('\n') if line]
    candidates = []
    for line in lines:
        parts = line.split('\t')
        remote_name, remote_url_type = parts
        if remote_url_type.endswith('(push)'):
            candidates.append(remote_name)
    if len(candidates) == 1:
        remote_name = candidates[0]
    return remote_name


def dvc_discover_ssh_remote(host, remote=None, forward_ssh_agent=False,
                            dry=False, force=False):
    cwd = _getcwd()
    cwd = ub.Path(cwd)
    relcwd = relpath(cwd, expanduser('~'))

    # Build a list of places where the remote is likely to be located.
    candidate_remote_cwds = []
    candidate_remote_cwds.append(relcwd)

    # TODO: look at symlinks relative to home and try those but resolved?

    candidate_remote_cwds.append(cwd)
    candidate_remote_cwds.append(cwd.resolve())

    remote_cache_dir = None

    for remote_cwd in candidate_remote_cwds:
        # Build one command to execute on the remote
        remote_parts = [
            'cd {remote_cwd}',
        ]
        remote_parts.append('dvc cache dir')
        ssh_flags = []
        if forward_ssh_agent:
            ssh_flags += ['-A']
        ssh_flags = ' '.join(ssh_flags)

        remote_part = ' && '.join(remote_parts)
        command_template = 'ssh {ssh_flags} {host} "' + remote_part + '"'
        kw = dict(
            host=host,
            remote_cwd=remote_cwd,
            ssh_flags=ssh_flags
        )
        command = command_template.format(**kw)
        print(command)
        info = ub.cmd(command, verbose=3)
        if info['ret'] == 0:
            remote_cache_dir = info['out'].strip()
            break
        else:
            print('Warning: Unable to find candidate DVC repo on the remote')

    if remote_cache_dir is None:
        raise Exception('No candidates were found')

    local_command = f'dvc remote add --local {host} ssh://{host}{remote_cache_dir}'
    if not dry:
        # /media/joncrall/raid/home/joncrall/data/dvc-repos/smart_watch_dvc/.dvc/cache
        ub.cmd(local_command, verbose=3)
    else:
        print(local_command)


if __name__ == '__main__':
    r"""
    Ignore:
        dvc remote add --local ooo ssh://ooo/data/joncrall/dvc-repos/smart_data_dvc/.dvc/cache

    CommandLine:
        python -m dvc_discover_ssh_remote namek --dry

        python ~/code/simple_dvc/simple_dvc/discover_ssh_remote.py ooo --dry
    """
    main()
