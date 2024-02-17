from functools import partial, wraps
from uhura.base import Readable, Writable
from uhura.composition import match_function_type
from inspect import Signature
from typing import Optional


def uhura_reader(function):
    """
    Decorator to convert functions into uhura readables. This will not change the type signature of the function.
    The cache key will default to the function's qualname.
    example:

    >>> @uhura_reader
    ... def read_int():
    ...     return 1
    """
    signature = Signature.from_callable(function)

    class _SingleFunctionReadable(Readable):
        def __init__(self, *args, **kwargs):
            self.params = signature.bind(*args, **kwargs)

        @match_function_type(function)
        def read(self):
            return function(*self.params.args, **self.params.kwargs)

        def cache_key(self):
            return function.__qualname__

    @wraps(function)
    @match_function_type(function)
    def wrapped(*args, **kwargs):
        return _SingleFunctionReadable(*args, **kwargs).read()

    return wrapped


def uhura_writer(function=None, output_arg: Optional[str] = None):
    """
    Decorator to convert functions into uhura writers. This will not change the type signature of the function.
    The cache key will default to the function's qualname. If the function only takes a single argument
    it will be assumed that this argument is what is being written out. Otherwise you will need to specify an
    output_arg (as a string) for the argument of interest.

    examples:

    >>> @uhura_writer
    ... def write_int(integer):
    ...     pass

    >>> @uhura_writer("integer")
    ... def write_integer_and_log_it(integer, logger):
    ...     pass

    """
    if function is None:
        return partial(uhura_writer, output_arg=output_arg)
    signature = Signature.from_callable(function)
    if len(signature.parameters) > 1 and output_arg not in signature.parameters:
        raise ValueError(f"Invalid/missing output_arg for writer function {function}")

    class _SingleFunctionWritable(Writable):
        def __init__(self, params):
            self.params = params

        @match_function_type(function)
        def write(self, obj):
            self.params.arguments[output_arg] = obj
            return function(*self.params.args, **self.params.kwargs)

        def cache_key(self):
            return function.__qualname__

    @wraps(function)
    @match_function_type(function)
    def wrapped(*args, **kwargs):
        bound = signature.bind(*args, **kwargs)
        if output_arg:
            written_arg = bound.arguments[output_arg]
            return _SingleFunctionWritable(bound).write(written_arg)
        return _SingleFunctionWritable(bound).write(*bound.args, **bound.kwargs)

    return wrapped
