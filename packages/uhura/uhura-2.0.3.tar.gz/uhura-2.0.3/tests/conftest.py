import pytest
import random
import numpy as np
import string
import pandas as pd


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
