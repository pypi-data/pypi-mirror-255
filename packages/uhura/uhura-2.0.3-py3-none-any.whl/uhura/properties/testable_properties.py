from typing import Callable, List, Optional
import pandas as pd
import numpy as np

from uhura.properties.homomorphic_hash import homomorphic_hash
from uhura.properties.property_tester import depends, SENTINEL


def _get_batched_hash(tested, arg, number_of_batches=5):
    batch_size = max(arg.shape[0] // number_of_batches, 1)
    batch_idxs = list(range(0, arg.shape[0], batch_size))
    batch_idxs.append(batch_idxs[-1] + batch_size)
    # we are doing everything on a single line to avoid doubling the memory needs for `arg`
    return np.bitwise_xor.reduce(
        np.array(
            [
                homomorphic_hash(tested(arg.iloc[batch_idxs[idx] : batch_idxs[idx + 1]]))
                for idx in range(len(batch_idxs[:-1]))
            ]
        )
    )


def create_custom_debugger(
    notes_creator: Optional[Callable[[pd.DataFrame, Optional[pd.DataFrame]], str]]
):
    def debugger(tested, arg: pd.DataFrame, result: Optional[pd.DataFrame] = None):
        notes_arg = notes_creator(arg, None) if notes_creator is not None else ""
        notes = " - ".join([f" pre [{tested.__name__}]:", notes_arg])
        result = tested(arg.copy(deep=True)) if result is SENTINEL else result
        notes_result = notes_creator(arg, result) if notes_creator is not None else ""
        notes += " - ".join([f" post [{tested.__name__}]:", notes_result])
        return result, True, notes

    return debugger


def pure(tested, arg: pd.DataFrame, result: Optional[pd.DataFrame] = None):
    """Test whether a function modifies the dataframe it runs over (ie `arg`)

    Args:
        tested (Callable): the function for which we are testing the property
        arg (pd.DataFrame): the dataframe over which we want to run the function being tested
        result (pd.DataFrame): the result of `tested(arg)` this may already be passed as an argument in case it is
            available and we don't need to run again `tested(arg)` to check the property. So, that we can avoid
            running `tested` unnecessarily.
    Returns:
        pd.DataFrame: The output of running the tested function on the main dataframe ie `tested(arg)`
        bool: It tells if the property is respected
    """
    initial_hash = homomorphic_hash(arg)
    result = tested(arg)
    return result, initial_hash == homomorphic_hash(arg)


@depends(pure)
def homomorphic(tested, arg: pd.DataFrame, result: Optional[pd.DataFrame] = None):
    result = tested(arg) if result is SENTINEL else result
    batch_hash = _get_batched_hash(tested, arg)
    property_respected = homomorphic_hash(result) == batch_hash
    return result, property_respected


@depends(pure)
def idempotent(tested, arg: pd.DataFrame, result: Optional[pd.DataFrame] = None):
    result = tested(arg) if result is SENTINEL else result
    result_hash = homomorphic_hash(result)
    return result, result_hash == homomorphic_hash(tested(result))


def order_invariant(tested, arg: pd.DataFrame, result: Optional[pd.DataFrame] = None):
    """Check whether `tested` output is affected by the order of the rows in `arg`"""
    # `tested` can modify `arg` inplace so to avoid copying it we have to run it against
    # the shuffled version of the `arg` dataframe before we run it against the actual
    # dataframe
    shuffled_result = homomorphic_hash(tested(arg.sample(frac=1)).sort_index())
    result = tested(arg) if result is SENTINEL else result
    return result, homomorphic_hash(result.sort_index()) == shuffled_result


def adds_columns(tested, arg: pd.DataFrame, result: Optional[pd.DataFrame] = None):
    input_columns = set(arg.columns)
    result = result if isinstance(result, pd.DataFrame) else tested(arg)
    result_columns = set(result.columns)
    return result, bool(result_columns - input_columns)


def drops_columns(tested, arg: pd.DataFrame, result: Optional[pd.DataFrame] = None):
    input_columns = set(arg.columns)
    result = tested(arg) if result is SENTINEL else result
    result_columns = set(result.columns)
    return result, bool(input_columns - result_columns)


def preserves_row_count(tested, arg: pd.DataFrame, result: Optional[pd.DataFrame] = None):
    start_len = arg.shape[0]
    result = tested(arg) if result is SENTINEL else result
    return result, start_len == result.shape[0]


def preserves_index_identity(tested, arg: pd.DataFrame, result: Optional[pd.DataFrame] = None):
    arg_index = arg.index
    result = tested(arg) if result is SENTINEL else result
    return result, result.index.equals(arg_index)


def preserves_types(tested, arg: pd.DataFrame, result: Optional[pd.DataFrame] = None):
    start_types = set(arg.columns)
    result = tested(arg) if result is SENTINEL else result
    end_types = set(result.columns)
    intersection = start_types & end_types
    return result, (arg[intersection].dtypes == result[intersection].dtypes).all()


def preserves_index_types(tested, arg: pd.DataFrame, result: Optional[pd.DataFrame] = None):
    start_index = set(arg.index.names)
    result = tested(arg) if result is SENTINEL else result
    end_index = set(result.index.names)
    intersection = start_index & end_index
    intersection = list(set(arg.index.names).intersection(result.index.names))
    respected = type(arg.index) is type(result.index)  # noqa: E721
    if respected:
        if isinstance(arg.index, pd.MultiIndex):
            respected = (
                arg.index.dtypes.loc[intersection] == result.index.dtypes.loc[intersection]
            ).all()
        else:
            respected = (len(intersection) > 0) & (arg.index.dtype == result.index.dtype)
    return result, respected


def get_columns_not_modified_property(columns: List[str]):
    @depends(order_invariant)
    def columns_not_modified(tested, arg: pd.DataFrame, result: Optional[pd.DataFrame] = None):
        arg_sorted = arg.sort_index()
        original_values = {
            c: homomorphic_hash(arg_sorted[c]) for c in columns if c in arg_sorted.columns
        }
        result = tested(arg_sorted) if result is SENTINEL else result
        result_sorted = result.sort_index()
        # TODO we should check the two below as property dependencies here. However,
        # testing multiple properties requires purity, or a refactor. Purity limits the scope
        # of properties and a refactor requires time
        if result_sorted.shape[0] != arg.shape[0]:
            # TODO we should use `preserves_row_count` here
            return result, False, "Cannot test, the dataframe length has changed"
        if not result_sorted.index.equals(arg_sorted.index):
            # TODO we should use `preserves_index_identity` here
            return result, False, "Cannot test, the dataframe index has been changed"
        new_values = {
            c: homomorphic_hash(result_sorted[c])
            for c in original_values
            if c in result_sorted.columns
        }
        changes = []
        for c, vals in original_values.items():
            if c not in new_values:
                changes.append(f"{c} dropped")
            else:
                if not new_values[c] == vals:
                    changes.append(f"{c} modified")

        return result, len(changes) == 0, ", ".join(changes)

    return columns_not_modified


DEFAULT_PROPERTIES = tuple(
    [
        pure,
        homomorphic,
        idempotent,
        order_invariant,
        adds_columns,
        drops_columns,
        preserves_row_count,
        preserves_types,
        preserves_index_types,
    ]
)
