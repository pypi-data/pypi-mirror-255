from __future__ import absolute_import

import collections
import contextlib
import weakref

from mercurial.i18n import _
from mercurial import (
    branchmap,
    bundle2,
    discovery,
    encoding,
    exchange,
    extensions,
    hg,
    scmutil,
    util,
    wireprototypes,
    wireprotov1server,
)
from mercurial.wireprotov1peer import wirepeer
from . import (
    common,
    compat,
)

urlreq = util.urlreq

@contextlib.contextmanager
def override_context_branch(repo, publishedset=()):
    unfi = repo.unfiltered()

    def overridebranch(p, origbranch):
        def branch():
            branch = origbranch()
            if p.rev() in publishedset:
                return common.formatfqbn(branch=branch)
            return p.fqbn()
        return branch

    class repocls(unfi.__class__):
        # awful hack to see branch as "branch//namespace/topic"
        def __getitem__(self, key):
            ctx = super(repocls, self).__getitem__(key)
            oldbranch = ctx.branch
            oldparents = ctx.parents
            rev = ctx.rev()

            def branch():
                branch = oldbranch()
                if rev in publishedset:
                    return common.formatfqbn(branch=branch)
                return ctx.fqbn()

            def parents():
                parents = oldparents()
                for p in parents:
                    if getattr(p, '_topic_ext_branch_hack', False):
                        continue

                    p.branch = overridebranch(p, p.branch)
                    p._topic_ext_branch_hack = True
                return parents

            ctx.branch = branch
            ctx.parents = parents
            return ctx

    oldrepocls = unfi.__class__
    try:
        unfi.__class__ = repocls
        if repo.filtername is not None:
            repo = unfi.filtered(repo.filtername)
        else:
            repo = unfi
        yield repo
    finally:
        unfi.__class__ = oldrepocls


def _headssummary(orig, pushop, *args, **kwargs):
    repo = pushop.repo.unfiltered()
    remote = pushop.remote

    publishedset = ()
    remotebranchmap = None
    if remote.capable(b'topics-namespaces'):
        origremotebranchmap = remote.branchmaptns
    else:
        origremotebranchmap = remote.branchmap
    publishednode = [c.node() for c in pushop.outdatedphases]
    publishedset = repo.revs(b'ancestors(%ln + %ln)',
                             publishednode,
                             pushop.remotephases.publicheads)

    publishing = (b'phases' not in remote.listkeys(b'namespaces')
                  or bool(remote.listkeys(b'phases').get(b'publishing', False)))
    # remote repo may be non-publishing, but if user does hg push --publish, we
    # still need to consider push operation publishing
    publishing = publishing or pushop.publish

    ctxoverride = util.nullcontextmanager()
    if common.hastopicext(pushop.repo) and remote.capable(b'topics'):
        ctxoverride = override_context_branch(repo, publishedset=publishedset)
        overrides = {(b'_internal', b'tns-publish'): publishing}
    else:
        overrides = {(b'_internal', b'tns-disable-fqbn'): True}
    configoverride = repo.ui.configoverride(overrides, b'topic-namespaces')

    if not common.hastopicext(pushop.repo):
        with ctxoverride, configoverride:
            return orig(pushop, *args, **kwargs)
    elif ((publishing or not remote.capable(b'topics'))
            and not getattr(pushop, 'publish', False)):
        with ctxoverride, configoverride:
            return orig(pushop, *args, **kwargs)

    getrev = compat.getgetrev(repo.unfiltered().changelog)

    def remotebranchmap():
        # drop topic information from changeset about to be published
        result = collections.defaultdict(list)
        items = list(compat.branchmapitems(origremotebranchmap()))
        if not remote.capable(b'topics-namespaces'):
            items = [(common.upgradeformat(branch), heads) for branch, heads in items]
        for branch, heads in items:
            namedbranch, tns, topic = common.parsefqbn(branch)
            for h in heads:
                r = getrev(h)
                if r is not None and r in publishedset:
                    result[common.formatfqbn(branch=namedbranch)].append(h)
                else:
                    result[branch].append(h)
        for heads in result.values():
            heads.sort()
        return result

    with ctxoverride, configoverride:
        try:
            if remotebranchmap is not None:
                remote.branchmap = remotebranchmap
            unxx = repo.filtered(b'unfiltered-topic')
            repo.unfiltered = lambda: unxx
            pushop.repo = repo
            summary = orig(pushop)
            for key, value in summary.items():
                branch, tns, topic = common.parsefqbn(key)
                if topic: # FIXME: also check namespace?
                    if value[0] is None and value[1]:
                        summary[key] = ([value[1][0]], ) + value[1:]
            return summary
        finally:
            if r'unfiltered' in vars(repo):
                del repo.unfiltered
            if remotebranchmap is not None:
                remote.branchmap = origremotebranchmap

def wireprotobranchmap(orig, repo, proto):
    if not common.hastopicext(repo):
        return orig(repo, proto)
    unfi = repo.unfiltered()
    oldrepocls = unfi.__class__
    try:
        class repocls(oldrepocls):
            def branchmap(self):
                usetopic = not self.publishing()
                return super(repocls, self).branchmap(topic=usetopic, convertbm=usetopic)

            # Where is branchmaptns method, you might ask? The answer is that
            # this repocls is only relevant when we're trying to use the old
            # branchmap server command. If we use branchmaptns command that was
            # introduced as a part of topic namespaces support, then this
            # repocls shouldn't be used at all.
        unfi.__class__ = repocls
        if repo.filtername is not None:
            repo = unfi.filtered(repo.filtername)
        else:
            repo = unfi
        return orig(repo, proto)
    finally:
        unfi.__class__ = oldrepocls

def wireprotobranchmaptns(repo, proto):
    """copied from wireprotov1server.branchmap()"""
    if not common.hastopicext(repo):
        return wireprotov1server.branchmap(repo, proto)
    heads = []
    entries = compat.bcentries(repo.branchmaptns())
    for branch, nodes in compat.branchmapitems(entries):
        branchname = urlreq.quote(encoding.fromlocal(branch))
        branchnodes = wireprototypes.encodelist(nodes)
        heads.append(b'%s %s' % (branchname, branchnodes))

    return wireprototypes.bytesresponse(b'\n'.join(heads))

def _get_branch_name(ctx):
    # make it easy for extension with the branch logic there
    return ctx.branch()


def _filter_obsolete_heads(repo, heads):
    """filter heads to return non-obsolete ones

    Given a list of heads (on the same named branch) return a new list of heads
    where the obsolete part have been skimmed out.
    """
    new_heads = []
    old_heads = heads[:]
    while old_heads:
        rh = old_heads.pop()
        ctx = repo[rh]
        current_name = _get_branch_name(ctx)
        # run this check early to skip the evaluation of the whole branch
        if not ctx.obsolete():
            new_heads.append(rh)
            continue

        # Get all revs/nodes on the branch exclusive to this head
        # (already filtered heads are "ignored"))
        sections_revs = repo.revs(
            b'only(%d, (%ld+%ld))', rh, old_heads, new_heads,
        )
        keep_revs = []
        for r in sections_revs:
            ctx = repo[r]
            if ctx.obsolete():
                continue
            if _get_branch_name(ctx) != current_name:
                continue
            keep_revs.append(r)
        for h in repo.revs(b'heads(%ld and (::%ld))', sections_revs, keep_revs):
            new_heads.append(h)
    new_heads.sort()
    return new_heads

# Discovery have deficiency around phases, branch can get new heads with pure
# phases change. This happened with a changeset was allowed to be pushed
# because it had a topic, but it later become public and create a new branch
# head.
#
# Handle this by doing an extra check for new head creation server side
def _nbheads(repo):
    code = scmutil.filteredhash.__code__
    if r'needobsolete' not in code.co_varnames[:code.co_argcount]:
        # hg <= 6.0 (053a5bf508da)
        filterfn = _filter_obsolete_heads
    else:
        filterfn = lambda repo, heads: heads
    data = {}
    for b in repo.branchmap().iterbranches():
        namedbranch, tns, topic = common.parsefqbn(b[0])
        if tns != b'none' or topic:
            continue
        oldheads = [repo[n].rev() for n in b[1]]
        newheads = filterfn(repo, oldheads)
        data[b[0]] = newheads
    return data

def handlecheckheads(orig, op, inpart):
    """This is used to check for new heads when publishing changeset"""
    orig(op, inpart)
    if not common.hastopicext(op.repo) or op.repo.publishing():
        return
    tr = op.gettransaction()
    if tr.hookargs[b'source'] not in (b'push', b'serve'): # not a push
        return
    tr._prepushheads = _nbheads(op.repo)
    reporef = weakref.ref(op.repo)
    if util.safehasattr(tr, '_validator'):
        # hg <= 5.3 (36f08ae87ef6)
        oldvalidator = tr._validator

    def _validate(tr):
        repo = reporef()
        if repo is not None:
            repo.invalidatecaches()
            finalheads = _nbheads(repo)
            for branch, oldnb in tr._prepushheads.items():
                newheads = finalheads.pop(branch, [])
                if len(oldnb) < len(newheads):
                    cl = repo.changelog
                    newheads = sorted(set(newheads).difference(oldnb))
                    heads = scmutil.nodesummaries(repo, [cl.node(r) for r in newheads])
                    msg = _(
                        b"push creates new heads on branch '%s': %s"
                        % (branch, heads)
                    )
                    raise compat.StateError(msg)
            for branch, newnb in finalheads.items():
                if 1 < len(newnb):
                    cl = repo.changelog
                    heads = scmutil.nodesummaries(repo, [cl.node(r) for r in newnb])
                    msg = _(
                        b"push creates new branch '%s' with multiple heads: %s"
                        % (branch, heads)
                    )
                    hint = _(b"merge or see 'hg help push' for details about "
                             b"pushing new heads")
                    raise compat.StateError(msg, hint=hint)

    def validator(tr):
        _validate(tr)
        return oldvalidator(tr)

    if util.safehasattr(tr, '_validator'):
        # hg <= 5.3 (36f08ae87ef6)
        tr._validator = validator
    else:
        tr.addvalidator(b'000-new-head-check', _validate)

handlecheckheads.params = frozenset()

def _pushb2phases(orig, pushop, bundler):
    if common.hastopicext(pushop.repo):
        checktypes = (b'check:heads', b'check:updated-heads')
        hascheck = any(p.type in checktypes for p in bundler._parts)
        if not hascheck and pushop.outdatedphases:
            exchange._pushb2ctxcheckheads(pushop, bundler)
    return orig(pushop, bundler)

def wireprotocaps(orig, repo, proto):
    caps = orig(repo, proto)
    if common.hastopicext(repo) and repo.peer().capable(b'topics'):
        caps.append(b'topics')
        caps.append(b'topics-namespaces')
    return caps

# **kwargs is for accommodating an optional changelog argument
# hg <= 4.8 (5e5c8f2a1eb5)
def wrapbranchinfo(orig, self, rev, **kwargs):
    # NOTE: orig can be either branchinfo() or _branchinfo()!
    b, close = orig(self, rev, **kwargs)
    if common.hastopicext(self._repo):
        if self._repo.ui.configbool(b'_internal', b'tns-disable-fqbn'):
            # the config option prevents this function from doing anything,
            # this happens when e.g. the remote repo doesn't have topic
            # extension enabled
            pass
        elif self._repo.ui.configbool(b'_internal', b'tns-publish'):
            # when this rev gets published, only branch will stay
            b = common.formatfqbn(branch=b)
        else:
            ctx = self._repo[rev]
            b = ctx.fqbn()
    return b, close

# **kwargs is for accommodating an optional changelog argument
# hg <= 4.8 (5e5c8f2a1eb5)
def wrapslowbranchinfo(orig, self, rev, **kwargs):
    if self.branchinfo == self._branchinfo:
        # _branchinfo() gets called directly and needs to do the conversion
        return wrapbranchinfo(orig, self, rev, **kwargs)
    else:
        # _branchinfo() gets called through branchinfo(), the latter will need
        # to do the conversion
        return orig(self, rev, **kwargs)

def wrapaddpartrevbranchcache(orig, repo, bundler, outgoing):
    """making sure we send rev-branch-cache that only has bare branches"""
    overrides = {(b'_internal', b'tns-disable-fqbn'): True}
    with repo.ui.configoverride(overrides, b'topic-namespaces'):
        orig(repo, bundler, outgoing)

def wraphgpeer(orig, uiorrepo, opts, *args, **kwargs):
    """hg.peer() that checks if there are explicit arguments for e.g. pull"""
    peer = orig(uiorrepo, opts, *args, **kwargs)
    if any(opts.get(k) for k in (b'rev', b'bookmark', b'branch')):
        peer.ui.setconfig(b'_internal', b'tns-explicit-target', True, b'topic-namespaces')
    return peer

def wraphgremoteui(orig, src, opts):
    """hg.remoteui() that copies tns-related config options to peer ui"""
    dst = orig(src, opts)
    if util.safehasattr(src, 'baseui'):  # looks like a repository
        src = src.ui
    # we need to copy topic namespaces from local config to peer ui, since it
    # needs to be accessible for peer command executors
    namespaces = src.configlist(b'experimental', b'tns-default-pull-namespaces', [b'*'])
    dst.setconfig(b'experimental', b'tns-default-pull-namespaces', namespaces, b'copied')
    return dst

def modsetup(ui):
    """run at uisetup time to install all destinations wrapping"""
    extensions.wrapfunction(discovery, '_headssummary', _headssummary)
    extensions.wrapfunction(wireprotov1server, 'branchmap', wireprotobranchmap)
    wireprotov1server.commands.pop(b'branchmap')
    wireprotov1server.wireprotocommand(b'branchmap', permission=b'pull')(wireprotov1server.branchmap)
    extensions.wrapfunction(wireprotov1server, '_capabilities', wireprotocaps)
    wirepeer.branchmaptns = wirepeer.branchmap
    wireprotov1server.wireprotocommand(b'branchmaptns', permission=b'pull')(wireprotobranchmaptns)
    extensions.wrapfunction(branchmap.revbranchcache, 'branchinfo', wrapbranchinfo)
    # branchinfo method can get replaced by _branchinfo method directly when
    # on-disk revbranchcache is not available, see revbranchcache.__init__()
    extensions.wrapfunction(branchmap.revbranchcache, '_branchinfo', wrapslowbranchinfo)
    # we need a proper wrap b2 part stuff
    extensions.wrapfunction(bundle2, 'handlecheckheads', handlecheckheads)
    bundle2.handlecheckheads.params = frozenset()
    bundle2.parthandlermapping[b'check:heads'] = bundle2.handlecheckheads
    if util.safehasattr(bundle2, 'handlecheckupdatedheads'):
        # we still need a proper wrap b2 part stuff
        extensions.wrapfunction(bundle2, 'handlecheckupdatedheads', handlecheckheads)
        bundle2.handlecheckupdatedheads.params = frozenset()
        bundle2.parthandlermapping[b'check:updated-heads'] = bundle2.handlecheckupdatedheads
    extensions.wrapfunction(bundle2, 'addpartrevbranchcache', wrapaddpartrevbranchcache)
    extensions.wrapfunction(exchange, '_pushb2phases', _pushb2phases)
    exchange.b2partsgenmapping[b'phase'] = exchange._pushb2phases
    extensions.wrapfunction(hg, 'peer', wraphgpeer)
    extensions.wrapfunction(hg, 'remoteui', wraphgremoteui)
