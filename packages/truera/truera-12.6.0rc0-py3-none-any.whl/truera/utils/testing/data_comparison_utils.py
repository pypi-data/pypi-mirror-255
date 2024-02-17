from typing import Union
import unittest

import numpy as np
import pandas as pd

from truera.test.util.truera_workspace_test_utils import sanitize_local_path


def _updateOrReadData(
    actual_data: Union[pd.DataFrame, np.ndarray],
    expected_data_filename: str,
    update_file: bool = False,
    dtype=None,
    parse_dates=None
) -> pd.DataFrame:
    if update_file:
        if isinstance(actual_data, np.ndarray):
            actual_data = pd.DataFrame(data=actual_data)
        actual_data.to_csv(expected_data_filename, index=None)
    return pd.read_csv(
        expected_data_filename, dtype=dtype, parse_dates=parse_dates
    )


def assertDataEqualsWithTestCase(
    test_case: unittest.TestCase,
    actual_data: Union[pd.DataFrame, np.ndarray],
    expected_data_filename: str,
    update_file: bool = False,
    check_names: bool = True
):
    assertDataAlmostEqualsWithTestCase(
        test_case,
        actual_data,
        expected_data_filename,
        atol=0,
        rtol=0,
        update_file=update_file,
        check_names=check_names
    )


def assertDataAlmostEqualsWithTestCase(
    test_case: unittest.TestCase,
    actual_data: Union[pd.DataFrame, np.ndarray],
    expected_data_filename: str,
    atol: float = 1e-3,
    rtol: float = 1e-3,
    update_file: bool = False,
    check_names: bool = True,
    col_dtypes=None,
    parse_dates=None
):
    expected_data = _updateOrReadData(
        actual_data,
        expected_data_filename,
        update_file=update_file,
        dtype=col_dtypes,
        parse_dates=parse_dates
    )
    if update_file:
        test_case.fail("Test in record mode. (update_file=True)")
    if isinstance(actual_data, pd.DataFrame):
        pd.testing.assert_frame_equal(
            actual_data,
            expected_data,
            atol=atol,
            rtol=rtol,
            check_names=check_names,
        )
    elif isinstance(actual_data, pd.Series):
        pd.testing.assert_series_equal(
            actual_data,
            expected_data[expected_data.columns[0]],
            atol=atol,
            rtol=rtol,
            check_names=check_names
        )

    elif isinstance(actual_data, np.ndarray):
        test_case.assertTrue(
            np.allclose(
                actual_data.ravel(),
                expected_data.to_numpy().ravel(),
                atol=atol,
                rtol=rtol
            )
        )
    else:
        raise TypeError(
            f"actual_data must be one of [pandas.DataFrame, numpy.ndarray] but given {type(actual_data)}!"
        )


def assert_data_frame_equal(
    actual: pd.DataFrame,
    expected_filename: str,
    atol: float = 1e-8,
    rtol: float = 1e-8,
    normalize_index_name: bool = True,
    read_as_same_dtypes: bool = True,
    ignore_col_order: bool = False,
    update_file: bool = False
) -> None:
    if normalize_index_name:
        actual.index.name = "__truera_index__"
    expected_filename = sanitize_local_path(expected_filename)
    if update_file:
        actual.to_csv(expected_filename)
    if not read_as_same_dtypes:
        expected = pd.read_csv(expected_filename, index_col=0)
    else:
        dtypes = actual.dtypes.to_dict()
        if actual.index.name:
            dtypes[actual.index.name] = actual.index.dtype
        expected = pd.read_csv(expected_filename, index_col=0, dtype=dtypes)
    if ignore_col_order:
        expected.sort_index(axis=1, inplace=True)
        actual.sort_index(axis=1, inplace=True)
    pd.testing.assert_frame_equal(
        expected,
        actual,
        check_exact=False,
        atol=atol,
        rtol=rtol,
    )