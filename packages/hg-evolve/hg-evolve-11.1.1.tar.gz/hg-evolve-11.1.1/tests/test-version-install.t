  $ cat >> $HGRCPATH <<EOF
  > [extensions]
  > EOF
  $ echo "evolve=$(echo $(dirname $TESTDIR))/hgext3rd/evolve/" >> $HGRCPATH

Test outputting version number

  $ hg version -v
  Mercurial Distributed SCM (version *) (glob)
  (see https://mercurial-scm.org for more information)
  
  Copyright (C) 2005-* (glob)
  This is free software; see the source for copying conditions. There is NO
  warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
  
  Enabled extensions:
  
    evolve  external  * (glob)

Test install
TODO: fix warning
  $ "$PYTHON" "$TESTDIR/../setup.py" install --root "$TESTTMP/installtest" > /dev/null
  */distutils/dist.py:*: UserWarning: Unknown distribution option: 'python_requires' (glob)
    warnings.warn(msg)
