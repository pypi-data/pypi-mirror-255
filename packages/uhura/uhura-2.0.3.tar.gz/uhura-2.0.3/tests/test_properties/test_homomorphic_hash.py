import pandas as pd
import numpy as np
from uhura.properties.homomorphic_hash import homomorphic_hash
import pytest


@pytest.fixture
def example_messy_df():
    return pd.DataFrame(index=np.arange(10), data={"a": [np.random.random(10) for _ in range(10)]})


def test_can_hash_unhashable(example_messy_df):
    assert homomorphic_hash(example_messy_df)


def test_hash_is_homomorphic(example_messy_df):
    part1 = homomorphic_hash(example_messy_df.loc[:4])
    part2 = homomorphic_hash(example_messy_df.loc[5:])
    assert part1 ^ part2 == homomorphic_hash(example_messy_df)


def test_hash_is_order_invariant(example_messy_df):
    assert homomorphic_hash(example_messy_df) == homomorphic_hash(example_messy_df.sample(frac=1))
