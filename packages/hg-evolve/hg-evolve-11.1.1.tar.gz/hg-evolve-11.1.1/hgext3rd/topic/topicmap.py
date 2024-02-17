import contextlib
import hashlib

from mercurial.i18n import _
from mercurial.node import nullid
from mercurial import (
    branchmap,
    changegroup,
    extensions,
    repoview,
    util,
)

from . import (
    common,
    compat,
    discovery,
)

basefilter = set([b'base', b'immutable'])
def topicfilter(name):
    """return a "topic" version of a filter level"""
    if name in basefilter:
        return name
    elif name is None:
        return None
    elif name.endswith(b'-topic'):
        return name
    else:
        return name + b'-topic'

def istopicfilter(filtername):
    if filtername is None:
        return False
    return filtername.endswith(b'-topic')

def gettopicrepo(repo):
    if not common.hastopicext(repo):
        return repo
    filtername = topicfilter(repo.filtername)
    if filtername == repo.filtername:
        return repo
    return repo.filtered(filtername)

def _setuptopicfilter(ui):
    """extend the filter related mapping with topic related one"""
    funcmap = repoview.filtertable
    # hg <= 4.9 (caebe5e7f4bd)
    partialmap = branchmap.subsettable

    # filter level not affected by topic that we should not override

    for plainname in list(funcmap):
        newfilter = topicfilter(plainname)
        if newfilter == plainname:
            continue

        def revsfunc(repo, name=plainname):
            return repoview.filterrevs(repo, name)

        base = topicfilter(partialmap[plainname])

        if newfilter not in funcmap:
            funcmap[newfilter] = revsfunc
            partialmap[newfilter] = base
    funcmap[b'unfiltered-topic'] = lambda repo: frozenset()
    partialmap[b'unfiltered-topic'] = b'visible-topic'

def _phaseshash(repo, maxrev):
    """uniq ID for a phase matching a set of rev"""
    revs = set()
    cl = repo.changelog
    fr = cl.filteredrevs
    getrev = compat.getgetrev(cl)
    for n in compat.nonpublicphaseroots(repo):
        r = getrev(n)
        if r not in fr and r < maxrev:
            revs.add(r)
    key = nullid
    revs = sorted(revs)
    if revs:
        s = hashlib.sha1()
        for rev in revs:
            s.update(b'%d;' % rev)
        key = s.digest()
    return key

def modsetup(ui):
    """call at uisetup time to install various wrappings"""
    _setuptopicfilter(ui)
    _wrapbmcache(ui)
    extensions.wrapfunction(changegroup.cg1unpacker, 'apply', cgapply)
    compat.overridecommitstatus(commitstatus)

def cgapply(orig, self, repo, *args, **kwargs):
    """make sure a topicmap is used when applying a changegroup"""
    other = repo.filtered(topicfilter(repo.filtername))
    return orig(self, other, *args, **kwargs)

def commitstatus(orig, repo, node, branch, bheads=None, tip=None, **opts):
    # wrap commit status use the topic branch heads
    ctx = repo[node]
    ctxbranch = common.formatfqbn(branch=ctx.branch())
    if ctx.topic() and ctxbranch == branch:
        bheads = repo.branchheads(b"%s:%s" % (branch, ctx.topic()))

    with discovery.override_context_branch(repo) as repo:
        ret = orig(repo, node, branch, bheads=bheads, tip=tip, **opts)

    # logic copy-pasted from cmdutil.commitstatus()
    if ctx.topic():
        return ret
    parents = ctx.parents()

    if (not opts.get('amend') and bheads and node not in bheads and not any(
        p.node() in bheads and common.formatfqbn(branch=p.branch()) == branch
        for p in parents
    )):
        repo.ui.status(_(b"(consider using topic for lightweight branches."
                         b" See 'hg help topic')\n"))

    return ret

def _wrapbmcache(ui):
    class topiccache(_topiccache, branchmap.branchcache):
        pass
    branchmap.branchcache = topiccache

    try:
        # Mercurial 5.0
        class remotetopiccache(_topiccache, branchmap.remotebranchcache):
            pass
        branchmap.remotebranchcache = remotetopiccache

        def _wrapupdatebmcachemethod(orig, self, repo):
            # pass in the bound method as the original
            return _wrapupdatebmcache(orig.__get__(self), repo)
        extensions.wrapfunction(branchmap.BranchMapCache, 'updatecache', _wrapupdatebmcachemethod)
    except AttributeError:
        # hg <= 4.9 (3461814417f3)
        extensions.wrapfunction(branchmap, 'updatecache', _wrapupdatebmcache)
        # branchcache in hg <= 4.9 doesn't have load method, instead there's a
        # module-level function to read on-disk cache and return a branchcache
        extensions.wrapfunction(branchmap, 'read', _wrapbmread)

def _wrapupdatebmcache(orig, repo):
    previous = getattr(repo, '_autobranchmaptopic', False)
    try:
        repo._autobranchmaptopic = False
        return orig(repo)
    finally:
        repo._autobranchmaptopic = previous

# needed to prevent reference used for 'super()' call using in branchmap.py to
# no go into cycle. (yes, URG)
_oldbranchmap = branchmap.branchcache

@contextlib.contextmanager
def oldbranchmap():
    previous = branchmap.branchcache
    try:
        branchmap.branchcache = _oldbranchmap
        yield
    finally:
        branchmap.branchcache = previous

class _topiccache(object): # combine me with branchmap.branchcache

    def __init__(self, *args, **kwargs):
        # super() call may fail otherwise
        with oldbranchmap():
            super(_topiccache, self).__init__(*args, **kwargs)
        self.phaseshash = None

    def copy(self):
        """return an deep copy of the branchcache object"""
        entries = compat.bcentries(self)
        args = (entries, self.tipnode, self.tiprev, self.filteredhash,
                self._closednodes)
        if util.safehasattr(self, '_repo'):
            # hg <= 5.7 (6266d19556ad)
            args = (self._repo,) + args
        new = self.__class__(*args)
        new.phaseshash = self.phaseshash
        return new

    def load(self, repo, lineiter):
        """call branchmap.load(), and then transform branch names to be in the
        new "//" format
        """
        super(_topiccache, self).load(repo, lineiter)
        entries = compat.bcentries(self)

        for branch in tuple(entries):
            formatted = common.formatfqbn(branch=branch)
            if branch != formatted:
                entries[formatted] = entries.pop(branch)

    def validfor(self, repo):
        """Is the cache content valid regarding a repo

        - False when cached tipnode is unknown or if we detect a strip.
        - True when cache is up to date or a subset of current repo."""
        valid = super(_topiccache, self).validfor(repo)
        if not valid:
            return False
        elif not istopicfilter(repo.filtername) or self.phaseshash is None:
            # phasehash at None means this is a branchmap
            # come from non topic thing
            return True
        else:
            try:
                valid = self.phaseshash == _phaseshash(repo, self.tiprev)
                return valid
            except IndexError:
                return False

    def write(self, repo):
        """write cache to disk if it's not topic-only, but first transform
        cache keys from branches in "//" format into bare branch names
        """
        # we expect mutable set to be small enough to be that computing it all
        # the time will be fast enough
        if not istopicfilter(repo.filtername):
            cache = self.copy()
            entries = compat.bcentries(cache)

            for formatted in tuple(entries):
                branch, tns, topic = common.parsefqbn(formatted)
                if branch != formatted:
                    entries[branch] = entries.pop(formatted)

            super(_topiccache, cache).write(repo)

    def update(self, repo, revgen):
        """Given a branchhead cache, self, that may have extra nodes or be
        missing heads, and a generator of nodes that are strictly a superset of
        heads missing, this function updates self to be correct.
        """
        if not istopicfilter(repo.filtername):
            return super(_topiccache, self).update(repo, revgen)

        # See topic.discovery._headssummary(), where repo.unfiltered gets
        # overridden to return .filtered('unfiltered-topic'). revbranchcache
        # only can be created for unfiltered repo (filtername is None), so we
        # do that here, and this revbranchcache will be cached inside repo.
        # When we get rid of *-topic filters, then this workaround can be
        # removed too.
        repo.unfiltered().revbranchcache()

        super(_topiccache, self).update(repo, revgen)
        self.phaseshash = _phaseshash(repo, self.tiprev)

def _wrapbmread(orig, repo):
    """call branchmap.read(), and then transform branch names to be in the
    new "//" format
    """
    partial = orig(repo)
    if partial is None:
        # because of IOError or OSError
        return partial

    entries = compat.bcentries(partial)

    for branch in tuple(entries):
        formatted = common.formatfqbn(branch=branch)
        if branch != formatted:
            entries[formatted] = entries.pop(branch)

    return partial
