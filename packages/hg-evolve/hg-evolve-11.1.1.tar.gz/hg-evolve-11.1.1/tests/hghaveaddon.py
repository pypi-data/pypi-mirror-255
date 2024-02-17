import hghave

@hghave.check("docgraph-ext", "Extension to generate graph from repository")
def docgraph():
    try:
        import hgext.docgraph
        hgext.docgraph.cmdtable # trigger import
    except ImportError:
        try:
            import hgext3rd.docgraph
            hgext3rd.docgraph.cmdtable # trigger import
        except ImportError:
            return False
    return True

@hghave.check("flake8", "Flake8 python linter")
def has_flake8():
    try:
        import flake8

        flake8.__version__
    except ImportError:
        return False
    else:
        return True

@hghave.check("check-manifest", "check-manifest MANIFEST.in checking tool")
def has_check_manifest():
    return hghave.matchoutput('check-manifest --version 2>&1',
                              br'check-manifest version')

@hghave.check("default-cg3", "changegroup3 by default")
def has_default_changegroup3():
    from mercurial import configitems

    try:
        return configitems.coreitems[b'experimental'][b'changegroup3'].default
    except (AttributeError, KeyError):
        return False
