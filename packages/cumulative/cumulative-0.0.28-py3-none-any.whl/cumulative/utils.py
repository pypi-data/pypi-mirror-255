import logging
import warnings

import numpy as np

from cumulative.options import options

log = logging.getLogger(__name__)


class ValidateWarning(UserWarning):
    pass


def validate_frame(df, warning_prefix):

    stacklevel = 2

    if len(df) == 0:
        warn(
            f"{warning_prefix}: No rows in data frame",
            category=ValidateWarning,
            stacklevel=stacklevel,
        )
        return

    # Check for invalid values (nans, infs)
    count_cells = df.size
    count_invalid_cells = 0
    for col in df.columns:
        # Look for infs/nans as cell values
        count_invalid_cells += df[col].isin([np.inf, -np.inf, np.nan]).sum()
        # Look for infs/nans inside ndarrays
        count_invalid_cells += df[col].apply(lambda a: isinstance(a, np.ndarray) and (not np.isfinite(a).any())).sum()

    if count_invalid_cells > 0:
        warn(
            f"{warning_prefix}: {count_invalid_cells} ({count_invalid_cells / count_cells * 100:.0f}%) not-finite"
            " values (nans/infs) in data frame",
            category=ValidateWarning,
            stacklevel=stacklevel,
        )

    if len(set(df.columns)) != len(df.columns):
        warn(
            f"{warning_prefix}: Duplicate column names in data frame",
            category=ValidateWarning,
            stacklevel=stacklevel,
        )

    if len(df.columns) == 0:
        warn(
            f"{warning_prefix}: No columns in data frame",
            category=ValidateWarning,
            stacklevel=stacklevel,
        )


def warn(*args, stacklevel=1, **kwargs):
    if not options.get("warnings.disable"):
        warnings.warn(*args, stacklevel=stacklevel, **kwargs)
