from typing import Any
import pandas as pd
from collections import defaultdict
from uhura.comparison import Comparer


def _safe_hash(df):
    hash_sum = 0
    for column in df.columns:
        try:
            hash_sum += pd.util.hash_pandas_object(df[column])
        except TypeError:
            continue
    return hash_sum


def _compare_dataframes(df1: pd.DataFrame, df2: pd.DataFrame):
    """Compare two dataframes

    Multiple asserts before the "overall" hash comparison to allow us to narrow down
    what is wrong
    """
    assert df1.shape == df2.shape, f"Dataframe shapes do not match ({df1.shape} vs {df2.shape})"
    assert all(df1.columns == df2.columns), "Dataframe columns do not match"
    assert all(df1.dtypes == df2.dtypes), "Dataframe dtypes do not match"
    assert all(_safe_hash(df1) == _safe_hash(df2)), "Dataframe hashes do not match"


def _compare_series(ser1: pd.Series, ser2: pd.Series):
    assert len(ser1) == len(ser2), f"Series lengths do not match ({len(ser1)} vs {len(ser2)})"
    assert all(ser1.index == ser2.index), "Series indexes do not match"
    assert ser1.dtype == ser2.dtype, "Series dtypes do not match"
    try:
        assert all(ser1 == ser2), "Series hashes do not match"
    except TypeError:
        pass


def compare_data(data1: Any, data2: Any):
    assert type(data1) is type(data2), f"Data types do not match: {type(data1)} vs {type(data2)}"
    datatype = type(data1)
    if datatype not in COMPARISON_LOOKUP:
        assert data1 == data2, "Observed != Expected"
    else:
        COMPARISON_LOOKUP[datatype](data1, data2)


class PandasComparer(Comparer):
    def base_compare(self, actual, expected):
        return compare_data(actual, expected)


COMPARISON_LOOKUP = {
    pd.DataFrame: _compare_dataframes,
    pd.Series: _compare_series,
}

pandas_comparator = defaultdict(PandasComparer)
