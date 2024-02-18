"""
The dbx_accelerator package is the super package to a broad number of systems as enumerated below.

* common: package for functionality that is generic and used across all other packages.

Courseware Development
* dbbuild: Courseware build tools.
* dbgems: Wrappers around misc utility functions used from within a notebook.
* dbhelper: Primary entry point for Notebook based curriculum and the dbx_acceleratorHelper (DA) object.

Automation & REST APIs
* classrooms:
* rest:
* docebo:
* dougrest:

Misc [REST] APIs
* dbrest: Python wrapper around Databricks's REST API
* github: Python wrapper around GitHub's REST API
* google: Python wrapper around Google's REST API
* slack: Python wrapper around Slack's REST API

Special Projects:
* workspaces_3_0:
"""

import os

__all__ = ["validate_dependencies", "sol_acc_util", "dbgems", "companion"]


def validate_dependencies():
    """
    Validates the dependencies required by the dbx_accelerator package.

    This function checks if the dependencies have been validated before. If not, it imports the `dbgems` module
    from the `cdh_ref_python.dbx_accelerator` package and calls its `validate_dependencies` function.

    Raises:
        Any exception raised by the `dbgems.validate_dependencies` function.

    """
    try:
        # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
        assert validated_dependencies
    except NameError:
        try:
            # noinspection PyUnusedLocal
            validated_dependencies = True
            from cdh_ref_python.dbx_accelerator import dbgems

            dbgems.validate_dependencies("dbx_accelerator")
        except:
            pass


validate_dependencies()
