# Copyright 2017 FUJIWARA Katsunori <foozy@lares.dti.ne.jp>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
"""
Compatibility module
"""
from __future__ import absolute_import

from mercurial.i18n import _
from mercurial import (
    cmdutil,
    error,
    extensions,
    pycompat,
    util,
)

if pycompat.ispy3:
    def branchmapitems(branchmap):
        return branchmap.items()
else:
    # py3-transform: off
    def branchmapitems(branchmap):
        return branchmap.iteritems()
    # py3-transform: on

def bcentries(branchcache):
    if util.safehasattr(branchcache, '_entries'):
        return branchcache._entries
    else:
        # hg <= 4.9 (624d6683c705+b137a6793c51)
        return branchcache

# nodemap.get and index.[has_node|rev|get_rev]
# hg <= 5.2 (02802fa87b74)
def getgetrev(cl):
    """Returns index.get_rev or nodemap.get (for pre-5.3 Mercurial)."""
    if util.safehasattr(cl.index, 'get_rev'):
        return cl.index.get_rev
    return cl.nodemap.get

# hg <= 5.4 (e2d17974a869)
def nonpublicphaseroots(repo):
    if util.safehasattr(repo._phasecache, 'nonpublicphaseroots'):
        return repo._phasecache.nonpublicphaseroots(repo)
    return set().union(
        *[roots for roots in repo._phasecache.phaseroots[1:] if roots]
    )

def overridecommitstatus(overridefn):
    code = cmdutil.commitstatus.__code__
    if r'opts' in code.co_varnames[code.co_argcount:]:
        # commitstatus(..., **opts)
        extensions.wrapfunction(cmdutil, 'commitstatus', overridefn)
    elif r'tip' in code.co_varnames:
        # hg <= 6.5 (489268c8ee7e)
        def _override(orig, repo, node, branch, bheads=None, tip=None, opts=None):
            def _orig(repo, node, branch, bheads=None, tip=None, **opts):
                opts = pycompat.byteskwargs(opts)
                return orig(repo, node, branch, bheads=bheads, tip=tip, opts=opts)
            opts = pycompat.strkwargs(opts)
            return overridefn(_orig, repo, node, branch, bheads=bheads, tip=tip, **opts)
        extensions.wrapfunction(cmdutil, 'commitstatus', _override)
    else:
        # hg <= 5.6 (976b26bdd0d8)
        def _override(orig, repo, node, branch, bheads=None, opts=None):
            def _orig(repo, node, branch, bheads=None, **opts):
                opts = pycompat.byteskwargs(opts)
                return orig(repo, node, branch, bheads=bheads, opts=opts)
            if opts is None:
                opts = {}
            opts = pycompat.strkwargs(opts)
            return overridefn(_orig, repo, node, branch, bheads=bheads, **opts)
        extensions.wrapfunction(cmdutil, 'commitstatus', _override)

if util.safehasattr(error, 'InputError'):
    InputError = error.InputError
else:
    # hg <= 5.6 (8d72e29ad1e0)
    InputError = error.Abort

if util.safehasattr(error, 'StateError'):
    StateError = error.StateError
else:
    # hg <= 5.6 (527ce85c2e60)
    StateError = error.Abort

if util.safehasattr(error, 'CanceledError'):
    CanceledError = error.CanceledError
else:
    # hg <= 5.6 (ac362d5a7893)
    CanceledError = error.Abort

if util.safehasattr(cmdutil, 'check_at_most_one_arg'):
    def check_at_most_one_arg(opts, *args):
        return cmdutil.check_at_most_one_arg(opts, *args)
else:
    # hg <= 5.2 (d587937600be)
    def check_at_most_one_arg(opts, *args):
        def to_display(name):
            return pycompat.sysbytes(name).replace(b'_', b'-')

        previous = None
        for x in args:
            if opts.get(x):
                if previous:
                    raise InputError(_(b'cannot specify both --%s and --%s')
                                     % (to_display(previous), to_display(x)))
                previous = x
        return previous

if util.safehasattr(cmdutil, 'check_incompatible_arguments'):
    code = cmdutil.check_incompatible_arguments.__code__
    if r'others' in code.co_varnames[:code.co_argcount]:
        def check_incompatible_arguments(opts, first, others):
            return cmdutil.check_incompatible_arguments(opts, first, others)
    else:
        # hg <= 5.3 (d4c1501225c4)
        def check_incompatible_arguments(opts, first, others):
            return cmdutil.check_incompatible_arguments(opts, first, *others)
else:
    # hg <= 5.2 (023ad45e2fd2)
    def check_incompatible_arguments(opts, first, others):
        for other in others:
            check_at_most_one_arg(opts, first, other)
