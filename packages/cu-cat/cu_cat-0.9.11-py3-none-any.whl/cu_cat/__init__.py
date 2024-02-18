"""
cu_cat: Learning on dirty categories.
"""
from pathlib import Path as _Path

try:
    from ._check_dependencies import check_dependencies

    # check_dependencies()
except ModuleNotFoundError:
    import warnings

    warnings.warn(
        "pkg_resources is not available, dependencies versions will not be checked."
    )

from ._deduplicate import compute_ngram_distance, deduplicate
from ._datetime_encoder import DatetimeEncoder
from ._dep_manager import DepManager
from ._gap_encoder import GapEncoder  # type: ignore
from ._table_vectorizer import TableVectorizer

from ._version import get_versions
__version__ = get_versions()["version"]
del get_versions

__all__ = [
    "DatetimeEncoder",
    "GapEncoder",
    "TableVectorizer",
    "TableVectorizer",
    "DepManager",
    "deduplicate",
    "compute_ngram_distance"
]
