"""Vectice package.

The Vectice package is a library allowing data-scientists
to record their progress in the [Vectice app](https://docs.vectice.com/).

This package exposes essential Vectice classes and methods:

- the [autolog][vectice.autolog.autolog] method [Beta]
- the [connect][vectice.Connection.connect] method
- the [Workspace][vectice.models.Workspace] class
- the [Project][vectice.models.Project] class
- the [Phase][vectice.models.Phase] class
- the [Iteration][vectice.models.Iteration] class
- the [Dataset][vectice.Dataset] class
- the [Model][vectice.Model] class
"""

from __future__ import annotations

import sys
import warnings

warnings.filterwarnings("ignore", ".*PYARROW_IGNORE_TIMEZONE")
if sys.version_info < (3, 8):
    print(
        "ImportWarning: Python 3.7 is no longer maintained by the community. Upgrade to Python 3.8 or higher to ensure full compatibility with Vectice and access to its complete features."
    )

from vectice import api, autolog, models
from vectice.__version__ import __version__
from vectice.connection import Connection
from vectice.models.dataset import Dataset
from vectice.models.git_version import CodeSource
from vectice.models.model import Metric, Model, Property
from vectice.models.resource import (
    BigQueryResource,
    DatabricksTableResource,
    FileResource,
    GCSResource,
    NoResource,
    Resource,
    S3Resource,
    SnowflakeResource,
)
from vectice.models.resource.metadata import (
    DatasetSourceOrigin,
    DatasetSourceUsage,
    DatasetType,
    DBMetadata,
    File,
    FilesMetadata,
    MetadataDB,
)
from vectice.utils.logging_utils import configure_vectice_loggers, disable_logging

connect = Connection.connect

code_capture = True
"""Global code capture flag, enabled by default.

Code capture is triggered when registering a dataset or a model,
and only works when a valid Git repository is found.
Otherwise a warning is logged, telling what might be misconfigured in the repository.

Captured information include the repository name, URL, branch name, commit hash,
and whether the repository is dirty (has uncommitted changes).

Examples:
    To disable code capture globally:

    >>> import vectice
    >>> vectice.code_capture = False

    To re-enable code capture globally:

    >>> import vectice
    >>> vectice.code_capture = True
"""

configure_vectice_loggers(root_module_name=__name__)
silent = disable_logging
warnings.simplefilter("always", DeprecationWarning)

version = __version__

__all__ = [
    "api",
    "autolog",
    "models",
    "version",
    "connect",
    "DatabricksTableResource",
    "SnowflakeResource",
    "BigQueryResource",
    "Resource",
    "FileResource",
    "GCSResource",
    "S3Resource",
    "NoResource",
    "DatasetSourceUsage",
    "DatasetSourceOrigin",
    "DBMetadata",
    "FilesMetadata",
    "File",
    "MetadataDB",
    "DatasetType",
    "silent",
    "Metric",
    "Model",
    "Property",
    "CodeSource",
    "Dataset",
]
