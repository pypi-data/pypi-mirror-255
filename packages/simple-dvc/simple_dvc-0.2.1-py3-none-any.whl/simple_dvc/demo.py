

def init_randomized_dvc_repo(demo_root, with_git=False, reset=False):
    """
    Builds a medium complexity dvc repo, todo:
        implement some tests
    """
    import ubelt as ub
    from simple_dvc import SimpleDVC
    import random

    rng = random.Random(10998676167967)

    precon_dpath = ub.Path.appdir('simpledvc', 'precon')

    config = {
        'with_git': with_git,
        '__internal_version__': 4,
    }

    hashid = ub.hash_data(config, base='hex')[0:8]
    precon_dvc_root = precon_dpath / f'demo_{hashid}'

    precon_stamp = ub.CacheStamp(f'precon_demo_{hashid}', dpath=precon_dpath,
                                 depends=config)
    if reset:
        precon_stamp.clear()
        precon_dvc_root.delete()

    if precon_stamp.expired() or not precon_dvc_root.exists():
        # Build in a staging area first
        dvc_root = precon_dvc_root
        dvc_root.delete()

        if with_git:
            dvc_root.ensuredir()
            ub.cmd('git init', cwd=dvc_root, verbose=2)
            ub.cmd('git config --local user.email "sdvc-tester@kitware.com"', cwd=dvc_root, verbose=2)
            ub.cmd('git config --local user.name "Simple DVC Tester"', cwd=dvc_root, verbose=2)
            ub.cmd('git branch -m main', cwd=dvc_root, verbose=2)

        SimpleDVC.init(dvc_root, no_scm=not with_git)

        dvc = SimpleDVC.coerce(dvc_root)

        if with_git:
            ub.cmd('dvc config core.autostage true', cwd=dvc.dpath, verbose=3)

        ub.cmd('dvc config cache.type symlink,reflink,hardlink,copy', cwd=dvc.dpath, verbose=3)
        ub.cmd('dvc config cache.protected true', cwd=dvc.dpath, verbose=2)
        ub.cmd('dvc config core.analytics false', cwd=dvc.dpath, verbose=2)
        ub.cmd('dvc config core.check_update false', cwd=dvc.dpath, verbose=2)
        ub.cmd('dvc config core.check_update false', cwd=dvc.dpath, verbose=2)

        # Build basic data
        print('Writing demo repo structure')
        (dvc_root / 'test-set1').ensuredir()
        assets_dpath = (dvc_root / 'test-set1/assets').ensuredir()
        for idx in range(1, 21):
            fpath = assets_dpath / f'asset_{idx:03d}.data'
            fpath.write_text(str(idx) * 100)
        manifest_fpath = (dvc_root / 'test-set1/manifest.txt')
        manifest_fpath.write_text('pretend-data')

        root_fpath = dvc_root / 'root_file'
        root_fpath.write_text('----' * 100)

        root_dpath = dvc_root / 'root_dir'

        node_paths = random_nested_paths(rng=rng)

        for node_path in node_paths:
            rel_fpath = ub.Path(*[f'dir_{n}' for n in node_path[0:-1]]) / ('file_' + str(node_path[-1]) + '.data')
            fpath = root_dpath / rel_fpath
            fpath.parent.ensuredir()
            fpath.write_text(str(node_path))
        print('Finished writing demo repo structure')

        print('Adding demo repo structure')
        dvc.add(root_dpath)
        dvc.add(root_fpath)
        dvc.add(manifest_fpath)
        dvc.add(assets_dpath)

        if with_git:
            ub.cmd('cat .dvc/config', cwd=dvc.dpath, verbose=3)
            ub.cmd('git add .dvc/config', cwd=dvc.dpath, verbose=3)
            ub.cmd('git status', cwd=dvc.dpath, verbose=3)
            ub.cmd('git commit -am "initial commit"', cwd=dvc.dpath, verbose=3)
            ub.cmd('git status', cwd=dvc.dpath, verbose=3)

        precon_stamp.renew()

        # import xdev
        # xdev.tree_repr(dvc_root)

    demo_root.delete()
    demo_root.parent.ensuredir()
    precon_dvc_root.copy(demo_root)
    return demo_root


def random_nested_paths(num=30, rng=None):
    """
    Use networkx to make a random complex directory structure.

    Args:
        num (int): number of nodes in the random file system
        rng (None | int): random state / seed

    Returns:
        List[List[int]]:
            A list of "paths", which are represented as list of "names".

    CommandLine:
        xdoctest -m simple_dvc.demo random_nested_paths

    Example:
        >>> from simple_dvc.demo import *  # NOQA
        >>> import ubelt as ub
        >>> node_paths = random_nested_paths(num=10, rng=123)
        >>> print(f'node_paths = {ub.urepr(node_paths, nl=1)}')
        node_paths = [
            [2, 7, 0, 1],
            [2, 7, 0, 6, 8, 3],
            [2, 4],
            [2, 5],
            [2, 7, 0, 6, 8, 9],
        ]
    """
    import networkx as nx
    import ubelt as ub
    graph = nx.erdos_renyi_graph(num, p=0.2, directed=True, seed=rng)
    WORKAROUND_NX_3_2_REGRESSION = 1
    if WORKAROUND_NX_3_2_REGRESSION:
        for u, v, d in graph.edges(data=True):
            d['weight'] = 1.0

    try:
        tree = nx.minimum_spanning_arborescence(graph)
    except Exception:
        # Ensure a arboresence will exist
        sccs = list(nx.strongly_connected_components(graph))
        chosen = [min(scc) for scc in sccs]
        for u, v in ub.iter_window(chosen, 2):
            graph.add_edge(u, v, weight=1)
        tree = nx.minimum_spanning_arborescence(graph)

    # nx.write_network_text(tree)
    sources = [n for n in tree.nodes if not tree.pred[n]]
    sinks = [n for n in tree.nodes if not tree.succ[n]]

    node_paths = []
    for t in sinks:
        for s in sources:
            paths = list(nx.all_simple_edge_paths(tree, s, t))
            if paths:
                node_path = [u for (u, v) in paths[0]] + [t]
                node_paths.append(node_path)
    return node_paths


def simple_demo_repo(dvc_root):
    """
    Build a simple repo using only standard dvc commands for upstream MWEs
    """
    import ubelt as ub

    # Build in a staging area first
    assert not dvc_root.exists(), 'directory must not exist yet'
    dvc_root = dvc_root
    dvc_root.ensuredir()

    def cmd(command):
        return ub.cmd(command, cwd=dvc_root, verbose=2, system=True)

    cmd('git init')
    cmd('dvc init')

    cmd('dvc config core.autostage true')
    cmd('dvc config cache.type symlink,reflink,hardlink,copy')
    cmd('dvc config cache.protected true')
    cmd('dvc config core.analytics false')
    cmd('dvc config core.check_update false')
    cmd('dvc config core.check_update false')

    # Build basic data
    (dvc_root / 'test-set1').ensuredir()
    assets_dpath = (dvc_root / 'test-set1/assets').ensuredir()
    for idx in range(1, 21):
        fpath = assets_dpath / f'asset_{idx:03d}.data'
        fpath.write_text(str(idx) * 100)
    manifest_fpath = (dvc_root / 'test-set1/manifest.txt')
    manifest_fpath.write_text('pretend-data')

    root_fpath = dvc_root / 'root_file'
    root_fpath.write_text('----' * 100)

    cmd(f'dvc add {root_fpath}')
    cmd(f'dvc add {manifest_fpath}')
    cmd(f'dvc add {assets_dpath}')

    cmd('git commit -am "initial commit"')


def mwe():
    import ubelt as ub

    # Build a simple fresh dvc repo
    dvc_root = ub.Path.appdir('simpledvc', 'simple_demo')
    dvc_root.delete()
    simple_demo_repo(dvc_root)

    _ = ub.cmd('dvc cache migrate -vvv', cwd=dvc_root, verbose=3, system=True)
