#!/usr/bin/env python
"""
This script finds compatibility-related comments with a node hash specified
in all files in a given directory (. by default) and looks up the hash in a
repo (~/hg by default) to determine if each of the comments is correct and,
if not, it suggests the correct release. This can prevent accidentally
removing a piece of code that was misattributed to a different (earlier)
release of core hg.

Usage: $0 WDIR HGREPO where WDIR is usually evolve/hgext3rd/ and HGREPO is
the place with core Mercurial repo (not just checkout). Said repo has to be
sufficiently up-to-date, otherwise this script may not work correctly.
"""

from __future__ import print_function

import argparse
import os
import re
from subprocess import check_output

def grepall(workdir, linere):
    for root, dirs, files in os.walk(workdir):
        for fname in files:
            if not fname.endswith('.py'):
                continue
            path = os.path.join(root, fname)
            with open(path, 'r') as src:
                for lineno, line in enumerate(src, 1):
                    for groups in linere.findall(line):
                        yield path, lineno, line, groups

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('workdir', nargs='?', default='.')
    ap.add_argument('hgdir', nargs='?', default=os.path.expanduser('~/hg'))

    opts = ap.parse_args()

    linere = re.compile(r'hg <= ([0-9.]+) \(([0-9a-f+]+)\)')
    basecmd = ['hg', '--cwd', opts.hgdir, 'log', '-T', '{tags}']
    hgenv = {'HGPLAIN': '1', 'HGENCODING': 'UTF-8'}
    relcache = {}

    for path, lineno, line, match in grepall(opts.workdir, linere):
        expected, revset = match

        if revset not in relcache:
            tagrevset = 'max(tag("re:^[0-9]\\.[0-9]$") - (%s)::)' % revset
            cmd = basecmd + ['-r', tagrevset]
            relcache[revset] = check_output(cmd, env=hgenv).decode('UTF-8')

        lastrel = relcache[revset]

        if lastrel != expected:
            print('%s:%d:%s' % (path, lineno, line.rstrip('\r\n')))
            print('\\ actual last major release without %s is %s'
                  % (revset, lastrel))
            print()

if __name__ == '__main__':
    main()
