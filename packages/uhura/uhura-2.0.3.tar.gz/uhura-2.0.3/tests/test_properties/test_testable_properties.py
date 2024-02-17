import logging

import pandas as pd
import numpy as np
import functools
import pytest
from typing import Optional, Mapping
import string
import random

from uhura.properties import testable_properties as properties
from uhura.properties import transformer, PropertyTester
from uhura.modes import test_transformers


@pytest.fixture
def base_df():
    df_len = 20
    return pd.DataFrame(
        {
            "a": np.random.randn(df_len),
            "b": random.choices(string.ascii_letters, k=df_len),
            "c": np.repeat(np.nan, df_len),
            "d": range(df_len),
            "b_idx": random.choices(string.ascii_letters, k=df_len),
            "d_idx": range(df_len),
        }
    ).set_index(["b_idx", "d_idx"])


def sequential_counter(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy(deep=True)
    df["counter"] = range(0, df.shape[0])
    return df


def mapper(df: pd.DataFrame, mapper: Optional[Mapping] = None) -> pd.DataFrame:
    mapper = mapper if mapper else {l: l.upper() for l in string.ascii_letters}
    df = df.copy(deep=True)
    df["c"] = df["b"].map(mapper)
    return df


def drop_col(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df = df.copy(deep=True)
    return df.drop(col, axis=1)


def drop_rows(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy(deep=True)
    return df.iloc[:3]


def convert_to_int(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy(deep=True)
    df["a"] = df["a"].astype(int)
    return df


def convert_index_to_int(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy(deep=True)
    idx = df.index
    df = df.reset_index()
    df[idx.names[-1]] = df[idx.names[-1]].astype(str)
    return df.set_index(idx.names)


def add_random(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy(deep=True)
    df["random_column"] = np.random.random(len(df))
    return df


def inplace_add_random(df: pd.DataFrame) -> pd.DataFrame:
    df["random_column"] = np.random.random(len(df))
    return df


logging.getLogger().setLevel(logging.INFO)


@pytest.mark.parametrize(
    "property_test,transformer,expected",
    [
        (properties.homomorphic, mapper, True),
        (properties.homomorphic, sequential_counter, False),
        (properties.idempotent, mapper, True),
        (properties.idempotent, add_random, False),
        (properties.order_invariant, mapper, True),
        (properties.order_invariant, sequential_counter, False),
        (properties.adds_columns, sequential_counter, True),
        (properties.drops_columns, functools.partial(drop_col, col="a"), True),
        (properties.preserves_row_count, sequential_counter, True),
        (properties.preserves_row_count, drop_rows, False),
        (properties.preserves_types, drop_rows, True),
        (properties.preserves_types, convert_to_int, False),
        (properties.preserves_index_types, drop_rows, True),
        (properties.preserves_index_types, convert_index_to_int, False),
        (properties.pure, add_random, True),
        (properties.pure, inplace_add_random, False),
    ],
)
def test_decorators(property_test, transformer, expected, base_df):
    result = transformer(base_df) if property_test is not properties.pure else None
    _, observed = property_test(transformer, arg=base_df, result=result)
    assert expected == observed


def test_columns_not_modified(base_df):
    base_df_copy = base_df.copy(deep=True)
    columns_not_modified = properties.get_columns_not_modified_property(
        ["a", "c", "d", "missing_col"]
    )

    @transformer()
    def modify_and_drop(_df):
        _df = _df[[c for c in _df.columns if c != "c"]]
        _df.loc[_df["d"] == 1, "a"] = -10
        modify_and_drop.counter += 1
        return _df

    modify_and_drop.counter = 0

    @transformer()
    def modfify_other_columns(_df):
        _df["b"] = 10
        return _df

    _tester = PropertyTester.create_for_properties([columns_not_modified])
    with test_transformers(tester=_tester):
        modify_and_drop(base_df.copy(deep=True))
        # test we call twice to test order invariance and that we never call for testing columns modification
        assert modify_and_drop.counter == 2
        results = _tester.get_results(modify_and_drop, summary=False)
        assert results["order_invariant"].has_property
        assert (
            results["get_columns_not_modified_property.<locals>.columns_not_modified"].has_property
            is False
        )
        assert (
            results["get_columns_not_modified_property.<locals>.columns_not_modified"].notes
            == "a modified, c dropped"
        )

        modfify_other_columns(base_df)
        # test that modified column not being tracked is being ignored
        results = _tester.get_results(modfify_other_columns, summary=False)
        assert results["order_invariant"].has_property
        assert results[
            "get_columns_not_modified_property.<locals>.columns_not_modified"
        ].has_property
        assert (
            results["get_columns_not_modified_property.<locals>.columns_not_modified"].notes == ""
        )
        # test that the original index sorting is being preserved even if order invariance is being tested
        pd.testing.assert_index_equal(base_df_copy.index, base_df.index)


def test_property_only_checked_once_with_nested_functions(base_df, caplog):
    """As described in the `_Transformer.__call__` by checking properties
    that require calling the same function several times we may lead to
    combinatorial explosion. This test makes sure that we have a mechanism
    for handling it.
    As of the current implementation homorphism will run the function it
    decorates 6 times. In the case of this test the function being called
    is `function_with_log`. `function_with_log` then calls mapper.
    So, `mapper` will already be called 6 times due to the 6
    `function_with_log` calls. `mapper` then is also checking homomorphism
    on itself. So, the property is going to do 6 `mapper` calls each time
    is being called. So, we would have 6 `function_with_log` that will
    trigger 6 `mapper` calls each, which will lead to 36 mapper calls overall.
    Effectively we only need to test the properties for `mapper` once
    and then call `mapper` only once per `function_with_log` call.
    This should lead to 6 `mapper` calls when its property is checked
    the first time and then 5 other `mapper` calls, one per
    `function_with_log` we need to do to test its homomorphic property

    Also, we are going to call the `mapper` functions another 2 times when
    testing that `function_with_log` and `mapper` and pure. As well as
    other 2 times when running the actual functions in `wrapper`

    """

    @transformer(evaluated_arg_name="df")
    def mapper(df: pd.DataFrame, mapping_dict: Optional[Mapping] = None) -> pd.DataFrame:
        mapping_dict = (
            mapping_dict if mapping_dict else {l: l.upper() for l in string.ascii_letters}
        )
        df = df.copy(deep=True)
        df["c"] = df["b"].map(mapping_dict)
        logging.info("mapper logging")
        mapper.counter += 1
        return df

    mapper.counter = 0

    @transformer(evaluated_arg_name="df")
    def function_with_log(df: pd.DataFrame) -> pd.DataFrame:
        logging.info("function_with_log logging")
        return mapper(df)

    _tester = PropertyTester.create_for_properties([properties.homomorphic])

    with test_transformers(tester=_tester):
        function_with_log(base_df)
        assert mapper.counter == 11
        logging.info("original logging levels restored")
        expected_logs = [
            "function_with_log logging",
            "mapper logging",
            "original logging levels restored",
        ]
        assert len(caplog.messages) == 7
        assert caplog.messages[:2] == expected_logs[:2]
        assert caplog.messages[-1:] == expected_logs[-1:]
        results = _tester.get_results(function_with_log, summary=False)
        assert results["pure"].has_property
        assert results["homomorphic"].has_property

        results = _tester.get_results(mapper, summary=False)
        assert results["pure"].has_property
        assert results["homomorphic"].has_property


def _identity(df):
    return df


def test_preserves_index_types_for_simple_index():
    df = pd.DataFrame(data={"a": list(range(10)), "b": list(range(10))})
    result = _identity(df)
    assert properties.preserves_index_types(_identity, df, result=result)[1]


def test_custom_debugger():
    def how_has_index_changed(arg, result=None):
        if result is not None:
            missing_in_arg = set(result.index) - set(arg.index)
            missing_in_result = set(arg.index) - set(result.index)

            return f"indexes missing in arg: {list(missing_in_arg)} indexes missing in result {list(missing_in_result)}"
        else:
            return f"arg shape {arg.shape}"

    custom_debugger = properties.create_custom_debugger(how_has_index_changed)

    @transformer
    def rename_indexes(df):
        df.rename(index={8: 10, 9: 11}, inplace=True)
        return df

    base_df = pd.DataFrame({"a": range(10)})
    _tester = PropertyTester.create_for_properties([custom_debugger])

    with test_transformers(tester=_tester):
        rename_indexes(base_df)
        results = _tester.get_results(rename_indexes, summary=False)
        assert (
            results["create_custom_debugger.<locals>.debugger"].notes
            == " pre [rename_indexes]: - arg shape (10, 1) post [rename_indexes]: - indexes missing in arg: [10, 11] indexes missing in result [8, 9]"
        )
