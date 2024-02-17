# utility to setup pythonpath to point into the tested repository

export SRCDIR="`dirname $TESTDIR`"
if [ -n "$PYTHONPATH" ]; then
    export HGTEST_ORIG_PYTHONPATH=$PYTHONPATH
    if uname -o 2> /dev/null | grep -q Msys; then
        export PYTHONPATH="$SRCDIR;$PYTHONPATH"
    else
        export PYTHONPATH=$SRCDIR:$PYTHONPATH
    fi
else
    export PYTHONPATH=$SRCDIR
fi
