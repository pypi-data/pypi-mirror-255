import asyncio
import operator
import os
import random
import tempfile
from inspect import isasyncgen
from typing import AsyncIterable, Iterable

import pytest

from uhura.base import Readable, Writable
from uhura.caches import (
    CachingService,
)
from uhura.caching import (
    cache_local_input,
    compare_known_good_output,
    replace_local_input,
    save_known_good_output,
)
from uhura.functional import uhura_reader, uhura_writer
from uhura.modes import fixture_builder_mode, task_test_mode


class RandomReadable(Readable[float]):
    async def read(self) -> float:
        return random.random()


@uhura_reader
async def random_function():
    return random.random()


@uhura_reader
def sync_random_function():
    return random.random()


class SyncRandomReadable(Readable[float]):
    def read(self) -> float:
        return random.random()


@uhura_reader
def sync_random_stream():
    for _ in range(10):
        yield random.random()


@uhura_reader
async def random_stream():
    for _ in range(10):
        yield random.random()


class RandomStreamReadable(Readable[float]):
    async def read(self) -> AsyncIterable[float]:
        for _ in range(10):
            yield random.random()


class SyncRandomStreamReadable(Readable[float]):
    def read(self) -> Iterable[float]:
        for _ in range(10):
            yield random.random()


class DummyWritable(Writable[int]):
    async def write(self, obj):
        pass


@uhura_writer
async def dummy_write(obj):
    pass


@uhura_writer
def sync_dummy_write(obj):
    pass


def dummy_write_with_arg(arg_value="test"):
    @uhura_writer(output_arg="obj")
    def dummy_write(obj=None, arg=arg_value):
        pass

    return dummy_write


class SyncDummyWritable(Writable[int]):
    def write(self, obj):
        pass


def _as_sync(coro):
    def inner(*args, **kwargs):
        return asyncio.run(coro(*args, **kwargs))

    return inner


@pytest.mark.parametrize(
    "read_method",
    [
        RandomReadable().sync_read,
        SyncRandomReadable().sync_read,
        _as_sync(random_function),
        sync_random_function,
    ],
)
def test_simple_input_caching(read_method):
    uncached_read = read_method()
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_service = CachingService.default(base_path=temp_dir)
        with Readable.decorated_with(cache_local_input(cache_service)):
            first_cached_read = read_method()
            assert (
                uncached_read != first_cached_read
            ), "Random readable is always returning the same thing"
            second_cached_read = read_method()
            assert first_cached_read == second_cached_read, "Readable not being cached"
        with Readable.decorated_with(replace_local_input(cache_service)):
            read_from_previous_cache = read_method()
            assert (
                first_cached_read == read_from_previous_cache
            ), "Reading from simple cache failed to return the same result"
    post_cache_read = read_method()
    assert post_cache_read != second_cached_read, "Removing simple cache failed"
    pass


async def _take_5(stream_read):
    items = []
    async for item in stream_read:
        items.append(item)
        if len(items) == 5:
            break
    return items


def _get_5_from_stream(stream):
    if isasyncgen(stream):
        return asyncio.run(_take_5(stream))
    items = []
    for item in stream:
        items.append(item)
        if len(items) == 5:
            break
    return items


def _make_look_like_a_normal_readable(function):
    function.read = function
    return function


@pytest.mark.parametrize(
    "stream_readable",
    [
        RandomStreamReadable(),
        SyncRandomStreamReadable(),
        _make_look_like_a_normal_readable(sync_random_stream),
        _make_look_like_a_normal_readable(random_stream),
    ],
)
def test_stream_input_caching(stream_readable):
    uncached_read = _get_5_from_stream(stream_readable.read())
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_service = CachingService.default(base_path=temp_dir, depth=5)
        with Readable.decorated_with(cache_local_input(cache_service)):
            first_cache_read = _get_5_from_stream(stream_readable.read())
            assert sorted(uncached_read) != sorted(
                first_cache_read
            ), "Random readable is always returning the same thing"
            second_cache_read = _get_5_from_stream(stream_readable.read())
            assert sorted(first_cache_read) == sorted(
                second_cache_read
            ), "Stream Readable is not being cached"
        with Readable.decorated_with(replace_local_input(cache_service)):
            read_from_previous_cache = _get_5_from_stream(stream_readable.read())
            assert sorted(first_cache_read) == sorted(
                read_from_previous_cache
            ), "Reading from cache failed to return the same result"
    post_cache_read = _get_5_from_stream(stream_readable.read())
    assert sorted(post_cache_read) != sorted(read_from_previous_cache), "Removing cache failed"
    pass


@pytest.mark.parametrize(
    "write_method",
    [
        DummyWritable().sync_write,
        SyncDummyWritable().sync_write,
        sync_dummy_write,
        dummy_write_with_arg("test"),
        _as_sync(dummy_write),
    ],
)
def test_output_caching_and_comparison(write_method):
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_service = CachingService.default(base_path=temp_dir)
        with Writable.decorated_with(save_known_good_output(cache_service)):
            write_method(1)
        with Writable.decorated_with(compare_known_good_output(cache_service)):
            with pytest.raises(AssertionError):
                write_method(2)  # Test raises if different
            write_method(1)  # But not if the same
    write_method(123)  # Test returns to normal write afterwards


@pytest.mark.parametrize(
    ["simple_read", "stream_read", "writer"],
    [
        (RandomReadable(), RandomStreamReadable(), DummyWritable()),
        (SyncRandomReadable(), SyncRandomStreamReadable(), SyncDummyWritable()),
    ],
)
def test_missing_files(simple_read, stream_read, writer):
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_service = CachingService.default(base_path=temp_dir)
        with Readable.decorated_with(cache_local_input(cache_service)):
            with Writable.decorated_with(save_known_good_output(cache_service)):
                simple_read.sync_read()
                _get_5_from_stream(stream_read.read())
                writer.sync_write(1)

        Readable.add_decorator(replace_local_input(cache_service))
        Writable.add_decorator(compare_known_good_output(cache_service))

    with pytest.raises(FileNotFoundError):
        simple_read.sync_read()

    with pytest.raises(FileNotFoundError):
        _get_5_from_stream(stream_read.read())

    with pytest.raises(FileNotFoundError):
        writer.sync_write(1)

    Writable.remove_last_decorator()
    Readable.remove_last_decorator()


@pytest.mark.parametrize(
    ["simple_read", "stream_read", "writer"],
    [
        (RandomReadable(), RandomStreamReadable(), DummyWritable()),
        (SyncRandomReadable(), SyncRandomStreamReadable(), SyncDummyWritable()),
    ],
)
def test_modes(simple_read, stream_read, writer):
    _initial_strategy = operator.add
    _changed_strategy = operator.mul

    def _important_function(strategy=_initial_strategy):
        addition = simple_read.sync_read()
        series = _get_5_from_stream(stream_read.read())
        writer.sync_write(strategy(series[0], addition))
        pass

    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = os.path.join(temp_dir, "good_output")
        input_path = os.path.join(temp_dir, "input")

        with fixture_builder_mode(known_good_path=output_path, input_path=input_path):
            _important_function()

        with task_test_mode(known_good_path=output_path, input_path=input_path):
            _important_function()
            with pytest.raises(AssertionError):
                _important_function(_changed_strategy)  # You've broken something!


_fake_database = {"id1": 27, "id2": 34}


class DatabaseReader(Readable[float]):
    def __init__(self, id_: str):
        self._id = id_

    def read(self):
        return _fake_database[self._id] + random.random()

    def cache_key(self):
        return f"DatabaseReader/{self._id}"


def test_cache_key():
    with fixture_builder_mode():
        assert DatabaseReader("id1").read() == DatabaseReader("id1").read()
        assert DatabaseReader("id2").read() == DatabaseReader("id2").read()
        assert (
            DatabaseReader("id1").read() != DatabaseReader("id2").read()
        ), "Cache key being ignored"
