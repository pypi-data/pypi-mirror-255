import numpy as np
import pandas as pd


def _safe_hash(df):
    hashed_columns = {}
    for column in df.columns:
        try:
            hashed_columns[column] = pd.util.hash_pandas_object(df[column])
        except TypeError:
            hashed_columns[column] = pd.util.hash_pandas_object(df[column].apply(str))
    return pd.util.hash_pandas_object(pd.concat(hashed_columns, axis=1))


def homomorphic_hash(pandas_object):
    try:
        if isinstance(pandas_object, pd.DataFrame):
            return np.bitwise_xor.reduce(_safe_hash(pandas_object).values)
        return np.bitwise_xor.reduce(pd.util.hash_pandas_object(pandas_object).values)
    except TypeError:
        return hash(pandas_object)
