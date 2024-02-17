import pandas as pd
from typing import Callable, Optional, Any, Tuple
from functools import wraps, partial
from uhura.properties.property_tester import AbstractPropertyTester
import inspect


def _confirm_evaluated_arg_name(signature, evaluated_arg_name: Optional[str]):
    if evaluated_arg_name is None:
        assert (
            len(signature.parameters) == 1
        ), f"No input_arg specified but the function takes more than one argument: [{signature.parameters}]"
        return list(signature.parameters)[0]
    assert (
        evaluated_arg_name in signature.parameters
    ), f"The input_arg specified [{evaluated_arg_name}] does not belong to the function signature: [{signature.parameters}]"
    return evaluated_arg_name


class _SingleArgFunctionFactory:
    def __init__(self, f: Callable, evaluated_arg_name: str):
        self._callable = f
        self._signature = inspect.Signature.from_callable(f)
        self._evaluated_arg_name = _confirm_evaluated_arg_name(self._signature, evaluated_arg_name)

    def bind_arguments(self, *args, **kwargs) -> Tuple[Any, Callable]:
        bound = self._signature.bind(*args, **kwargs)
        argument = bound.arguments[self._evaluated_arg_name]

        @wraps(self._callable)
        def inner(arg=argument):
            bound.arguments[self._evaluated_arg_name] = arg
            return self._callable(*bound.args, **bound.kwargs)

        return argument, inner


class Transformer:
    tester: Optional[AbstractPropertyTester] = None

    def __init__(self, function: Callable, evaluated_arg_name: Optional[str] = None):
        self._function = function
        self._single_arg_factory = _SingleArgFunctionFactory(function, evaluated_arg_name)

    def __call__(self, *args: Any, **kwargs: Any) -> pd.DataFrame:
        if self.tester is None:
            return self._function(*args, **kwargs)
        else:
            arg, single_arg_function = self._single_arg_factory.bind_arguments(*args, **kwargs)
            return self.tester.add_properties_to_function(single_arg_function)(arg)


def transformer(function: Optional[Callable] = None, evaluated_arg_name: Optional[str] = None):
    """
    A decorator to mark transform functions as part of a data pipeline. These functions can then be assessed
    programmatically to identify what properties they have.

    For single argument functions you can decorate with just '@transformer'

    >>> @transformer
        def add_one(value: int) -> int:
            return value + 1

    For multiple argument functions you will need to specify the 'main' argument, which is the dataset being transformed.

    >>> @transformer(evaluated_arg_name="text")
        def remove_words(text: str, words_to_remove: list) -> str:
            ...

    When not being tested, these decorators act the same as the underlying function.
    """
    if function is None:
        return partial(transformer, evaluated_arg_name=evaluated_arg_name)
    return wraps(function)(Transformer(function=function, evaluated_arg_name=evaluated_arg_name))
