from inspect import (
    isasyncgenfunction,
    iscoroutinefunction,
    isgeneratorfunction,
    isgenerator,
    isawaitable,
    isasyncgen,
)
from functools import wraps
from typing import Callable, TypeVar


_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")


def compose(before: Callable[[_A], _B], after: Callable[[_B], _C]) -> Callable[[_A], _C]:
    if iscoroutinefunction(before):
        return _awaitable_compose(before, after)
    if isasyncgenfunction(before):
        return _asyncgen_compose(before, after)
    if isgeneratorfunction(before):
        return _generator_compose(before, after)
    return _compose(before, after)


def _awaitable_compose(before, after):
    @wraps(before)
    async def composed(*args, **kwargs):
        return after(await before(*args, **kwargs))

    return composed


def _asyncgen_compose(before, after):
    @wraps(before)
    async def composed(*args, **kwargs):
        async for x in before(*args, **kwargs):
            yield after(x)

    return composed


def _generator_compose(before, after):
    @wraps(before)
    def composed(*args, **kwargs):
        for x in before(*args, **kwargs):
            yield after(x)

    return composed


def _compose(before, after):
    @wraps(before)
    def composed(*args, **kwargs):
        return after(before(*args, **kwargs))

    return composed


def async_unit(obj):
    if isgenerator(obj):
        return _asyncgen_unit(obj)
    if isawaitable(obj) or isasyncgen(obj):
        return obj
    if callable(obj):
        return _function_to_coro(obj)
    return _awaitable_unit(obj)


def _awaitable_unit(value):
    async def unit():
        return value

    return unit()


def _asyncgen_unit(gen):
    async def unit():
        for x in gen:
            yield x

    return unit()


def _function_to_coro(f):
    async def inner(*args, **kwargs):
        return f(*args, **kwargs)

    return inner


def match_function_type(wrapped):
    def decorator(f):
        if iscoroutinefunction(wrapped):

            async def inner(*args, **kwargs):
                return await f(*args, **kwargs)

        elif isgeneratorfunction(wrapped):

            def inner(*args, **kwargs):
                yield from f(*args, **kwargs)

        elif isasyncgenfunction(wrapped):

            async def inner(*args, **kwargs):
                async for item in f(*args, **kwargs):
                    yield item

        else:
            inner = f
        return inner

    return decorator
