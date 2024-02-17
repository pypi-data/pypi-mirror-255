"""
Hack to work around module import problems.
"""

__all__ = ["dbgems"]


def _load_dbgems():
    import cdh_ref_python

    if hasattr(cdh_ref_python, "dbgems"):
        return getattr(cdh_ref_python, "dbgems")
    try:
        import cdh_ref_python.dbgems

        return cdh_ref_python.dbgems
    except ModuleNotFoundError:
        pass
    import sys
    from os.path import exists
    from importlib.util import spec_from_file_location, module_from_spec

    module_name = "cdh_ref_python.dbgems"
    rel_path = "cdh_ref_python/dbgems/__init__.py"
    for path in sys.path:
        path = path + "/" + rel_path
        if exists(path):
            break
    else:
        raise ModuleNotFoundError("cdh_ref_python.dbgems not found")
    spec = spec_from_file_location(module_name, path)
    module = module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    cdh_ref_python.dbgems = module
    return module


dbgems = _load_dbgems()
