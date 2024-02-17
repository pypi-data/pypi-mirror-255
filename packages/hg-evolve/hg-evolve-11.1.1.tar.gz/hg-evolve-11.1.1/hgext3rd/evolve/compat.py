# Copyright 2017 Octobus <contact@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
"""
Compatibility module
"""

import contextlib

from mercurial.i18n import _
from mercurial import (
    cmdutil,
    context,
    copies as copiesmod,
    dirstate,
    error,
    hg,
    logcmdutil,
    merge as mergemod,
    node,
    obsolete,
    pycompat,
    rewriteutil,
    scmutil,
    util,
)

# hg <= 5.2 (c21aca51b392)
try:
    from mercurial import pathutil
    dirs = pathutil.dirs
except (AttributeError, ImportError):
    dirs = util.dirs  # pytype: disable=module-attr

# hg <= 5.4 (b7808443ed6a)
try:
    from mercurial import mergestate as mergestatemod
    mergestate = mergestatemod.mergestate
except (AttributeError, ImportError):
    mergestate = mergemod.mergestate  # pytype: disable=module-attr

from . import (
    exthelper,
)

eh = exthelper.exthelper()

# Evolution renaming compat

TROUBLES = {
    r'ORPHAN': b'orphan',
    r'CONTENTDIVERGENT': b'content-divergent',
    r'PHASEDIVERGENT': b'phase-divergent',
}

def memfilectx(repo, ctx, fctx, flags, copied, path):
    # XXX Would it be better at the module level?
    varnames = context.memfilectx.__init__.__code__.co_varnames  # pytype: disable=attribute-error

    if r"copysource" in varnames:
        mctx = context.memfilectx(repo, ctx, fctx.path(), fctx.data(),
                                  islink=b'l' in flags,
                                  isexec=b'x' in flags,
                                  copysource=copied.get(path))
    # hg <= 4.9 (550a172a603b)
    elif varnames[2] == r"changectx":
        mctx = context.memfilectx(repo, ctx, fctx.path(), fctx.data(),
                                  islink=b'l' in flags,
                                  isexec=b'x' in flags,
                                  copied=copied.get(path))  # pytype: disable=wrong-keyword-args
    return mctx

hg48 = util.safehasattr(copiesmod, 'stringutil')
# code imported from Mercurial core at ae17555ef93f + patch
def fixedcopytracing(repo, c1, c2, base):
    """A complete copy-patse of copies._fullcopytrace with a one line fix to
    handle when the base is not parent of both c1 and c2. This should be
    converted in a compat function once https://phab.mercurial-scm.org/D3896
    gets in and once we drop support for 4.9, this should be removed."""

    from mercurial import pathutil
    copies = copiesmod

    # In certain scenarios (e.g. graft, update or rebase), base can be
    # overridden We still need to know a real common ancestor in this case We
    # can't just compute _c1.ancestor(_c2) and compare it to ca, because there
    # can be multiple common ancestors, e.g. in case of bidmerge.  Because our
    # caller may not know if the revision passed in lieu of the CA is a genuine
    # common ancestor or not without explicitly checking it, it's better to
    # determine that here.
    #
    # base.isancestorof(wc) is False, work around that
    _c1 = c1.p1() if c1.rev() is None else c1
    _c2 = c2.p1() if c2.rev() is None else c2
    # an endpoint is "dirty" if it isn't a descendant of the merge base
    # if we have a dirty endpoint, we need to trigger graft logic, and also
    # keep track of which endpoint is dirty
    dirtyc1 = not base.isancestorof(_c1)
    dirtyc2 = not base.isancestorof(_c2)
    graft = dirtyc1 or dirtyc2
    tca = base
    if graft:
        tca = _c1.ancestor(_c2)

    # hg <= 4.9 (dc50121126ae)
    try:
        limit = copies._findlimit(repo, c1, c2)  # pytype: disable=module-attr
    except (AttributeError, TypeError):
        limit = copies._findlimit(repo, c1.rev(), c2.rev())  # pytype: disable=module-attr
    if limit is None:
        # no common ancestor, no copies
        return {}, {}, {}, {}, {}
    repo.ui.debug(b"  searching for copies back to rev %d\n" % limit)

    m1 = c1.manifest()
    m2 = c2.manifest()
    mb = base.manifest()

    # gather data from _checkcopies:
    # - diverge = record all diverges in this dict
    # - copy = record all non-divergent copies in this dict
    # - fullcopy = record all copies in this dict
    # - incomplete = record non-divergent partial copies here
    # - incompletediverge = record divergent partial copies here
    diverge = {} # divergence data is shared
    incompletediverge = {}
    data1 = {b'copy': {},
             b'fullcopy': {},
             b'incomplete': {},
             b'diverge': diverge,
             b'incompletediverge': incompletediverge,
             }
    data2 = {b'copy': {},
             b'fullcopy': {},
             b'incomplete': {},
             b'diverge': diverge,
             b'incompletediverge': incompletediverge,
             }

    # find interesting file sets from manifests
    if hg48:
        addedinm1 = m1.filesnotin(mb, repo.narrowmatch())
        addedinm2 = m2.filesnotin(mb, repo.narrowmatch())
    else:
        addedinm1 = m1.filesnotin(mb)
        addedinm2 = m2.filesnotin(mb)
    bothnew = sorted(addedinm1 & addedinm2)
    if tca == base:
        # unmatched file from base
        u1r, u2r = copies._computenonoverlap(repo, c1, c2, addedinm1, addedinm2)  # pytype: disable=module-attr
        u1u, u2u = u1r, u2r
    else:
        # unmatched file from base (DAG rotation in the graft case)
        u1r, u2r = copies._computenonoverlap(repo, c1, c2, addedinm1, addedinm2,  # pytype: disable=module-attr
                                             baselabel=b'base')
        # unmatched file from topological common ancestors (no DAG rotation)
        # need to recompute this for directory move handling when grafting
        mta = tca.manifest()
        if hg48:
            m1f = m1.filesnotin(mta, repo.narrowmatch())
            m2f = m2.filesnotin(mta, repo.narrowmatch())
            baselabel = b'topological common ancestor'
            u1u, u2u = copies._computenonoverlap(repo, c1, c2, m1f, m2f,  # pytype: disable=module-attr
                                                 baselabel=baselabel)
        else:
            u1u, u2u = copies._computenonoverlap(repo, c1, c2, m1.filesnotin(mta),  # pytype: disable=module-attr
                                                 m2.filesnotin(mta),
                                                 baselabel=b'topological common ancestor')

    for f in u1u:
        copies._checkcopies(c1, c2, f, base, tca, dirtyc1, limit, data1)  # pytype: disable=module-attr

    for f in u2u:
        copies._checkcopies(c2, c1, f, base, tca, dirtyc2, limit, data2)  # pytype: disable=module-attr

    copy = dict(data1[b'copy'])
    copy.update(data2[b'copy'])
    fullcopy = dict(data1[b'fullcopy'])
    fullcopy.update(data2[b'fullcopy'])

    if dirtyc1:
        copies._combinecopies(data2[b'incomplete'], data1[b'incomplete'], copy, diverge,  # pytype: disable=module-attr
                              incompletediverge)
    else:
        copies._combinecopies(data1[b'incomplete'], data2[b'incomplete'], copy, diverge,  # pytype: disable=module-attr
                              incompletediverge)

    renamedelete = {}
    renamedeleteset = set()
    divergeset = set()
    for of, fl in list(diverge.items()):
        if len(fl) == 1 or of in c1 or of in c2:
            del diverge[of] # not actually divergent, or not a rename
            if of not in c1 and of not in c2:
                # renamed on one side, deleted on the other side, but filter
                # out files that have been renamed and then deleted
                renamedelete[of] = [f for f in fl if f in c1 or f in c2]
                renamedeleteset.update(fl) # reverse map for below
        else:
            divergeset.update(fl) # reverse map for below

    if bothnew:
        repo.ui.debug(b"  unmatched files new in both:\n   %s\n"
                      % b"\n   ".join(bothnew))
    bothdiverge = {}
    bothincompletediverge = {}
    remainder = {}
    both1 = {b'copy': {},
             b'fullcopy': {},
             b'incomplete': {},
             b'diverge': bothdiverge,
             b'incompletediverge': bothincompletediverge
             }
    both2 = {b'copy': {},
             b'fullcopy': {},
             b'incomplete': {},
             b'diverge': bothdiverge,
             b'incompletediverge': bothincompletediverge
             }
    for f in bothnew:
        copies._checkcopies(c1, c2, f, base, tca, dirtyc1, limit, both1)  # pytype: disable=module-attr
        copies._checkcopies(c2, c1, f, base, tca, dirtyc2, limit, both2)  # pytype: disable=module-attr

    if dirtyc1 and dirtyc2:
        pass
    elif dirtyc1:
        # incomplete copies may only be found on the "dirty" side for bothnew
        assert not both2[b'incomplete']
        remainder = copies._combinecopies({}, both1[b'incomplete'], copy, bothdiverge,  # pytype: disable=module-attr
                                          bothincompletediverge)
    elif dirtyc2:
        assert not both1[b'incomplete']
        remainder = copies._combinecopies({}, both2[b'incomplete'], copy, bothdiverge,  # pytype: disable=module-attr
                                          bothincompletediverge)
    else:
        # incomplete copies and divergences can't happen outside grafts
        assert not both1[b'incomplete']
        assert not both2[b'incomplete']
        assert not bothincompletediverge
    for f in remainder:
        assert f not in bothdiverge
        ic = remainder[f]
        if ic[0] in (m1 if dirtyc1 else m2):
            # backed-out rename on one side, but watch out for deleted files
            bothdiverge[f] = ic
    for of, fl in bothdiverge.items():
        if len(fl) == 2 and fl[0] == fl[1]:
            copy[fl[0]] = of # not actually divergent, just matching renames

    if fullcopy and repo.ui.debugflag:
        repo.ui.debug(b"  all copies found (* = to merge, ! = divergent, "
                      b"% = renamed and deleted):\n")
        for f in sorted(fullcopy):
            note = b""
            if f in copy:
                note += b"*"
            if f in divergeset:
                note += b"!"
            if f in renamedeleteset:
                note += b"%"
            repo.ui.debug(b"   src: '%s' -> dst: '%s' %s\n" % (fullcopy[f], f,
                                                               note))
    del divergeset

    if not fullcopy:
        return copy, {}, diverge, renamedelete, {}

    repo.ui.debug(b"  checking for directory renames\n")

    # generate a directory move map
    d1, d2 = c1.dirs(), c2.dirs()
    # Hack for adding '', which is not otherwise added, to d1 and d2
    d1.addpath(b'/')
    d2.addpath(b'/')
    invalid = set()
    dirmove = {}

    # examine each file copy for a potential directory move, which is
    # when all the files in a directory are moved to a new directory
    for dst, src in fullcopy.items():
        dsrc, ddst = pathutil.dirname(src), pathutil.dirname(dst)
        if dsrc in invalid:
            # already seen to be uninteresting
            continue
        elif dsrc in d1 and ddst in d1:
            # directory wasn't entirely moved locally
            invalid.add(dsrc + b"/")
        elif dsrc in d2 and ddst in d2:
            # directory wasn't entirely moved remotely
            invalid.add(dsrc + b"/")
        elif dsrc + b"/" in dirmove and dirmove[dsrc + b"/"] != ddst + b"/":
            # files from the same directory moved to two different places
            invalid.add(dsrc + b"/")
        else:
            # looks good so far
            dirmove[dsrc + b"/"] = ddst + b"/"

    for i in invalid:
        if i in dirmove:
            del dirmove[i]
    del d1, d2, invalid

    if not dirmove:
        return copy, {}, diverge, renamedelete, {}

    for d in dirmove:
        repo.ui.debug(b"   discovered dir src: '%s' -> dst: '%s'\n" %
                      (d, dirmove[d]))

    movewithdir = {}
    # check unaccounted nonoverlapping files against directory moves
    for f in u1r + u2r:
        if f not in fullcopy:
            for d in dirmove:
                if f.startswith(d):
                    # new file added in a directory that was moved, move it
                    df = dirmove[d] + f[len(d):]
                    if df not in copy:
                        movewithdir[f] = df
                        repo.ui.debug((b"   pending file src: '%s' -> "
                                       b"dst: '%s'\n") % (f, df))
                    break

    return copy, movewithdir, diverge, renamedelete, dirmove

# hg <= 4.9 (7694b685bb10)
fixupstreamed = util.safehasattr(scmutil, 'movedirstate')
if not fixupstreamed:
    copiesmod._fullcopytracing = fixedcopytracing

# nodemap.get and index.[has_node|rev|get_rev]
# hg <= 5.2 (02802fa87b74)
def getgetrev(cl):
    """Returns index.get_rev or nodemap.get (for pre-5.3 Mercurial)."""
    if util.safehasattr(cl.index, 'get_rev'):
        return cl.index.get_rev
    return cl.nodemap.get

@contextlib.contextmanager
def changing_parents(repo):
    if util.safehasattr(repo.dirstate, 'changing_parents'):
        changing_parents = repo.dirstate.changing_parents(repo)
    else:
        # hg <= 6.3 (7a8bfc05b691)
        changing_parents = repo.dirstate.parentchange()
    try:
        with changing_parents:
            yield
    finally:
        # hg <= 5.2 (85c4cd73996b)
        if util.safehasattr(repo, '_quick_access_changeid_invalidate'):
            repo._quick_access_changeid_invalidate()

if util.safehasattr(mergemod, '_update'):
    def _update(*args, **kwargs):
        return mergemod._update(*args, **kwargs)
else:
    # hg <= 5.5 (2c86b9587740)
    def _update(*args, **kwargs):
        return mergemod.update(*args, **kwargs)

if (util.safehasattr(mergemod, '_update')
    and util.safehasattr(mergemod, 'update')):

    def update(ctx):
        mergemod.update(ctx)

    def clean_update(ctx):
        mergemod.clean_update(ctx)
else:
    # hg <= 5.5 (c1b603cdc95a)
    def update(ctx):
        hg.updaterepo(ctx.repo(), ctx.node(), overwrite=False)

    def clean_update(ctx):
        hg.updaterepo(ctx.repo(), ctx.node(), overwrite=True)

if util.safehasattr(cmdutil, 'format_changeset_summary'):
    def format_changeset_summary_fn(ui, repo, command, default_spec):
        def show(ctx):
            text = cmdutil.format_changeset_summary(ui, ctx, command=command,
                                                    default_spec=default_spec)
            ui.write(b'%s\n' % text)
        return show
else:
    # hg <= 5.6 (96fcc37a9c80)
    def format_changeset_summary_fn(ui, repo, command, default_spec):
        return logcmdutil.changesetdisplayer(ui, repo,
                                             {b'template': default_spec}).show

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

# allowdivergenceopt is a much newer addition to obsolete.py
# hg <= 5.8 (ba6881c6a178)
allowdivergenceopt = b'allowdivergence'
def isenabled(repo, option):
    if option == allowdivergenceopt:
        if obsolete._getoptionvalue(repo, obsolete.createmarkersopt):
            return obsolete._getoptionvalue(repo, allowdivergenceopt)
        else:
            # note that we're not raising error.Abort when divergence is
            # allowed, but creating markers is not, even on older hg versions
            return False
    else:
        return obsolete.isenabled(repo, option)

if util.safehasattr(dirstate.dirstate, 'set_clean'):
    movedirstate = scmutil.movedirstate
else:  # hg <= 5.8 (8a50fb0784a9)
    # TODO: call core's version once we've dropped support for hg <= 4.9
    def movedirstate(repo, newctx, match=None):
        """Move the dirstate to newctx and adjust it as necessary.

        A matcher can be provided as an optimization. It is probably a bug to pass
        a matcher that doesn't match all the differences between the parent of the
        working copy and newctx.
        """
        oldctx = repo[b'.']
        ds = repo.dirstate
        dscopies = dict(ds.copies())
        ds.setparents(newctx.node(), node.nullid)
        s = newctx.status(oldctx, match=match)
        for f in s.modified:
            if ds[f] == b'r':
                # modified + removed -> removed
                continue
            ds.normallookup(f)

        for f in s.added:
            if ds[f] == b'r':
                # added + removed -> unknown
                ds.drop(f)
            elif ds[f] != b'a':
                ds.add(f)

        for f in s.removed:
            if ds[f] == b'a':
                # removed + added -> normal
                ds.normallookup(f)
            elif ds[f] != b'r':
                ds.remove(f)

        # Merge old parent and old working dir copies
        oldcopies = copiesmod.pathcopies(newctx, oldctx, match)
        oldcopies.update(dscopies)
        newcopies = {
            dst: oldcopies.get(src, src)
            for dst, src in oldcopies.items()
        }
        # Adjust the dirstate copies
        for dst, src in newcopies.items():
            if src not in newctx or dst in newctx or ds[dst] != b'a':
                src = None
            ds.copy(src, dst)

# hg <= 4.9 (e1ceefab9bca)
code = context.overlayworkingctx._markdirty.__code__
if 'copied' not in code.co_varnames[:code.co_argcount]:
    def fixedmarkcopied(self, path, origin):
        self._markdirty(path, exists=True, date=self.filedate(path),
                        flags=self.flags(path), copied=origin)

    context.overlayworkingctx.markcopied = fixedmarkcopied

# what we're actually targeting here is e079e001d536
# hg <= 5.0 (dc3fdd1b5af4)
try:
    from mercurial import state as statemod
    markdirtyfixed = util.safehasattr(statemod, '_statecheck')
except (AttributeError, ImportError):
    markdirtyfixed = False
if not markdirtyfixed:
    def fixedmarkdirty(
        self,
        path,
        exists,
        data=None,
        date=None,
        flags='',
        copied=None,
    ):
        # data not provided, let's see if we already have some; if not, let's
        # grab it from our underlying context, so that we always have data if
        # the file is marked as existing.
        if exists and data is None:
            oldentry = self._cache.get(path) or {}
            data = oldentry.get('data')
            if data is None:
                data = self._wrappedctx[path].data()

        self._cache[path] = {
            'exists': exists,
            'data': data,
            'date': date,
            'flags': flags,
            'copied': copied,
        }

    context.overlayworkingctx._markdirty = fixedmarkdirty

def setbranch(repo, branch):
    # this attribute was introduced at about the same time dirstate.setbranch()
    # was modified
    # hg <= 6.3 (e9379b55ed80)
    if util.safehasattr(dirstate, 'requires_changing_files_or_status'):
        repo.dirstate.setbranch(branch, repo.currenttransaction())
    else:
        repo.dirstate.setbranch(branch)

if util.safehasattr(dirstate.dirstate, 'get_entry'):
    def dirchanges(dirstate):
        return [
            f for f in dirstate if not dirstate.get_entry(f).maybe_clean
        ]
else:
    # hg <= 5.9 (dcd97b082b3b)
    def dirchanges(dirstate):
        return [f for f in dirstate if dirstate[f] != b'n']

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

try:
    retained_extras_on_rebase = rewriteutil.retained_extras_on_rebase
    preserve_extras_on_rebase = rewriteutil.preserve_extras_on_rebase
except AttributeError:
    # hg <= 6.4 (cbcbf63b6dbf)
    retained_extras_on_rebase = {
        b'source',
        b'intermediate-source',
    }

    def preserve_extras_on_rebase(old_ctx, new_extra):
        """preserve the relevant `extra` entries from old_ctx on rebase-like operations
        """
        old_extra = old_ctx.extra()
        for key in retained_extras_on_rebase:
            value = old_extra.get(key)
            if value is not None:
                new_extra[key] = value

    # give other extensions an opportunity to collaborate
    rewriteutil.retained_extras_on_rebase = retained_extras_on_rebase
    rewriteutil.preserve_extras_on_rebase = preserve_extras_on_rebase
