from uhura.comparison import BasicComparer
from operator import methodcaller
import pytest


def test_basic_comparisons():
    comparer = BasicComparer()
    assert comparer(1, 1)
    assert comparer("hello", "hello")
    with pytest.raises(AssertionError):
        comparer(1, "1")
    with pytest.raises(AssertionError):
        comparer("Hello", "hEllo")


def test_actual_preprocessing():
    comparer = BasicComparer()
    comparer.add_actual_preprocessor(int)
    assert comparer("1", 1)


def test_expected_preprocessing():
    comparer = BasicComparer()
    comparer.add_expected_preprocessor(int)
    assert comparer(1, "1")


def test_preprocessing():
    comparer = BasicComparer()
    comparer.add_preprocessor(methodcaller("upper"))
    assert comparer("Hello", "hEllo")
