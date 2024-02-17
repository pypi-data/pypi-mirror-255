from abc import ABC, abstractmethod
from typing import Callable


class Comparer(ABC):
    def __init__(self):
        self._actual_prep = []
        self._expected_prep = []

    def add_actual_preprocessor(self, preprocessor: Callable):
        """Add a preprocessing step to be applied to actual values before they are compared."""
        self._actual_prep.append(preprocessor)

    def add_expected_preprocessor(self, preprocessor: Callable):
        """Add a preprocessing step to be applied to expected values before they are compared."""
        self._expected_prep.append(preprocessor)

    def add_preprocessor(self, preprocessor: Callable):
        """Add a preprocessing step to be applied to both values before they are compared."""
        self.add_actual_preprocessor(preprocessor)
        self.add_expected_preprocessor(preprocessor)

    @abstractmethod
    def base_compare(self, actual, expected):
        raise NotImplementedError()

    def _prep_actual(self, actual):
        for prep in self._actual_prep:
            actual = prep(actual)
        return actual

    def _prep_expected(self, expected):
        for prep in self._expected_prep:
            expected = prep(expected)
        return expected

    def __call__(self, actual, expected):
        return self.base_compare(self._prep_actual(actual), self._prep_expected(expected))


class BasicComparer(Comparer):
    def base_compare(self, actual, expected):
        match = actual == expected
        assert match, f"Expected {expected}, found {actual}"
        return match
