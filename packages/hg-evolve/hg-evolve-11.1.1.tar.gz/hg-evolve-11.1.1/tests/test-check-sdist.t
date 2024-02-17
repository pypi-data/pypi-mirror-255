Enable obsolescence to avoid the warning issue when obsmarkers are found

  $ cat << EOF >> "$HGRCPATH"
  > [experimental]
  > evolution = all
  > EOF

  $ cd "$TESTDIR"/..

Archiving to a separate location to avoid hardlink mess when the repo is shared

#if test-repo

  $ hg archive "$TESTTMP"/hg-evolve
  $ cd "$TESTTMP"/hg-evolve

#endif

  $ "$PYTHON" setup.py sdist --dist-dir "$TESTTMP"/dist > /dev/null
  */dist.py:*: UserWarning: Unknown distribution option: 'python_requires' (glob)
    warnings.warn(msg)
  warning: sdist: standard file not found: should have one of README, README.txt (?)
   (?)
  warning: no previously-included files found matching 'docs/tutorial/.netlify'
  warning: no previously-included files found matching '.gitlab-ci.yml'
  warning: no previously-included files found matching '.hg-format-source'
  warning: no previously-included files found matching 'Makefile'
  no previously-included directories found matching 'contrib'
  no previously-included directories found matching 'debian'
  no previously-included directories found matching '.gitlab'
  $ cd "$TESTTMP"/dist

  $ find hg-evolve-*.tar.gz -size +800000c
  hg-evolve-*.tar.gz (glob)

  $ tar -tzf hg-evolve-*.tar.gz | sed 's|^hg-evolve-[^/]*/||' | sort > files
  $ egrep '^tests/test-.*\.(t|py)$' files > test-files
  $ egrep -v '^tests/test-.*\.(t|py)$' files > other-files
  $ wc -l other-files
  148 other-files
  $ wc -l test-files
  ??? test-files (glob)
  $ fgrep debian files
  tests/test-check-debian.t
  $ fgrep __init__.py files
  hgext3rd/__init__.py
  hgext3rd/evolve/__init__.py
  hgext3rd/evolve/thirdparty/__init__.py
  hgext3rd/topic/__init__.py
  $ fgrep common.sh files
  docs/tutorial/testlib/common.sh
  tests/testlib/common.sh
  $ fgrep README files
  README.rst
  docs/README
  docs/tutorial/README.rst
  hgext3rd/topic/README

  $ egrep '(gitlab|contrib|hack|format-source)' files
  [1]
  $ fgrep legacy.py files
  [1]
  $ fgrep netlify files
  [1]
