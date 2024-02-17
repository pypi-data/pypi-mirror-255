import pytest
from functools import wraps

from uhura.properties.transformer import transformer
from uhura.properties.property_tester import AbstractPropertyTester


class _DummyTester(AbstractPropertyTester):
    def __init__(self):
        self.intercepted_values = []

    def add_properties_to_function(self, tested):
        @wraps(tested)
        def wrapper(arg):
            self.intercepted_values.append(arg)
            return tested(arg)

        return wrapper


def test_simple_transformer():
    @transformer
    def modify(val: int):
        return val + 2

    intercepted_values = []

    assert modify(10) == 12
    assert intercepted_values == []
    modify.tester = _DummyTester()
    assert modify(12) == 14
    assert modify.tester.intercepted_values == [12]


def test_raises_if_no_argname():
    with pytest.raises(AssertionError):

        @transformer
        def add(a: int, b: int):
            return a + b


def test_raises_if_arg_name_not_in_sig():
    with pytest.raises(AssertionError):

        @transformer(evaluated_arg_name="hello")
        def add(a: int, b: int):
            return a + b


def test_single_arg():
    @transformer(evaluated_arg_name="b")
    def add(a: int, b: int):
        return a + b

    intercepted_values = []
    assert add(1, 2) == 3
    assert intercepted_values == []
    add.tester = _DummyTester()
    assert add(4, 5) == 9
    assert add.tester.intercepted_values == [5]
