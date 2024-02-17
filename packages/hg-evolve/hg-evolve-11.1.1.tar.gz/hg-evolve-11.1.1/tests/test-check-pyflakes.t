#require test-repo pyflakes

Copied from Mercurial core (60ee2593a270)

  $ cd "`dirname "$TESTDIR"`"

run pyflakes on all tracked files ending in .py or with a python shebang

  $ hg files -0 'set:(**.py or grep("^#!.*python")) - removed()' \
  > -X hgext3rd/evolve/thirdparty \
  > 2>/dev/null \
  > | xargs -0 "$PYTHON" -m pyflakes 2>/dev/null
