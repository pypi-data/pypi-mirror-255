import pandas as pd

from uhura.properties.property_tester import PropertyTester, depends
from uhura.modes import test_transformers
from uhura.properties.transformer import transformer
from uhura.properties.testable_properties import pure, idempotent
import pytest
from random import random


def _example_callable_factory(name, has_prop):
    def inner(tested, arg, result):
        return None, has_prop

    inner.__qualname__ = name
    return inner


def _explode_if_called(_, __):
    raise NotImplementedError()


@pytest.fixture
def example_properties():
    part_a = _example_callable_factory("a", True)
    part_b = depends(part_a)(_example_callable_factory("b", False))
    part_c = depends(part_b)(_explode_if_called)
    part_d = depends(part_a)(_example_callable_factory("d", True))
    part_e = depends(part_a)(_example_callable_factory("e", True))
    part_f = depends(part_d, part_e)(_example_callable_factory("f", True))
    part_g = depends(part_d, part_e)(_example_callable_factory("g", False))
    return tuple([part_g, part_f, part_e, part_d, part_c, part_b, part_a])


def test_tester(example_properties):
    tester = PropertyTester.create_for_properties(example_properties)

    def tested(_):
        pass

    wrapped_tested = tester.add_properties_to_function(tested)
    wrapped_tested(None)
    assert tester.get_repository(tested).positive_properties == frozenset(["a", "d", "e", "f"])


def test_null_depends():
    with pytest.raises(ValueError):
        depends()(_example_callable_factory("a", True))


@transformer
def dummy_transformer(arg):
    return bool(arg)


@transformer
def dummy_transformer_2(_):
    return random()


def dummy_property_with_notes(tested, arg: pd.DataFrame, result=None):
    return arg, True, "Love letter from property"


def test_transformer_test_mode():
    dummy_tester = PropertyTester.create_for_properties([pure, idempotent])
    with test_transformers(tester=dummy_tester):
        dummy_transformer("yes")
        dummy_transformer_2(None)
    assert dummy_tester.get_results(dummy_transformer) == frozenset({"pure", "idempotent"})
    assert dummy_tester.get_results(dummy_transformer_2) == frozenset({"pure"})


def test_property_with_notes(base_df, caplog):
    dummy_tester = PropertyTester.create_for_properties([dummy_property_with_notes])
    decorated_tester = dummy_tester.add_properties_to_function(lambda arg: arg)
    decorated_tester(base_df)
    assert caplog.messages == [
        "[test_property_with_notes.<locals>.<lambda>]: has property dummy_property_with_notes - Love letter from property"
    ]
