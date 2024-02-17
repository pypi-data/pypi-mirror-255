"""
Wrap 'retained_extras_on_rebase' (from either mercurial or evolve) to retain
the "useful" extra.
"""

from mercurial import rewriteutil

try:
    rewriteutil.retained_extras_on_rebase
except AttributeError:
    # install the compatibility layer on older version
    from hgext3rd.evolve import compat
    compat.retained_extras_on_rebase # silence linter

def extsetup(ui):
    rewriteutil.retained_extras_on_rebase.add(b'useful')
