"""
Utilities for pandas.
"""

import pandas as pd

# dtype-related
# DOCS: https://pandas.pydata.org/docs/user_guide/basics.html#dtypes


def is_string_dtype(typ) -> bool:
    # May not be available in earlier pandas. Also remember having to make
    # adjustments to some types.
    return pd.api.types.is_string_dtype(typ)


def is_integer_dtype(typ) -> bool:
    # May not be available in earlier pandas. Bools are considered integers in
    # this.
    return pd.api.types.is_integer_dtype(typ)
