import pytest
from uhura.pandas_tools import compare_data
import pandas as pd

_basic_series = pd.Series(data=list(map(float, range(5))), index=list(reversed(list(range(5)))))


def test_series_len_check():
    with pytest.raises(AssertionError):
        compare_data(_basic_series.iloc[:4], _basic_series)


def test_series_index_check():
    with pytest.raises(AssertionError):
        compare_data(_basic_series.reset_index(), _basic_series)


def test_series_dtype_check():
    with pytest.raises(AssertionError):
        compare_data(_basic_series.astype(int), _basic_series)


def test_series_hash_check():
    _other_series = pd.Series(
        data=list(map(float, range(5))), index=list(reversed(list(range(5))))
    )
    _other_series[2] = 0.45
    with pytest.raises(AssertionError):
        compare_data(_basic_series, _other_series)


def test_skips_unhashable_series():
    unhashable_series = pd.Series(data=[list(range(4)) for _ in range(5)])
    compare_data(unhashable_series, unhashable_series)


_basic_df = pd.DataFrame(
    data=[(i, float(i), str(i)) for i in range(5)],
    columns=["integer", "float", "string"],
    index=list(reversed(list(range(5)))),
)


def test_df_different_number_of_columns_check():
    with pytest.raises(AssertionError):
        compare_data(_basic_df, _basic_df.drop(columns="integer"))


def test_df_different_length_check():
    with pytest.raises(AssertionError):
        compare_data(_basic_df, _basic_df.iloc[:4])


def test_df_different_dtype():
    with pytest.raises(AssertionError):
        compare_data(_basic_df, _basic_df.astype(int))


def test_df_different_hash():
    _different_df = pd.DataFrame(
        data=[(i, float(i), str(i)) for i in range(5)],
        columns=["integer", "float", "string"],
        index=list(reversed(list(range(5)))),
    )
    _different_df.iloc[0, 1] = 45
    with pytest.raises(AssertionError):
        compare_data(_different_df, _basic_df)
