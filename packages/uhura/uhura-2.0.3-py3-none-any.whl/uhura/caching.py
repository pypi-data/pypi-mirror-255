from collections import defaultdict
from functools import wraps
from inspect import isasyncgenfunction, iscoroutinefunction, isgeneratorfunction
from typing import Dict, Type

from uhura.base import Readable, Writable
from uhura.caches import CachingService
from uhura.comparison import BasicComparer
from uhura.composition import async_unit


def cache_local_input(cache_service: CachingService):
    def decorator(readable_cls: Type[Readable]):
        _original_read = readable_cls.read

        @wraps(readable_cls.read)
        def read(self):
            if isasyncgenfunction(_original_read) or isgeneratorfunction(_original_read):
                self._read_count = 0
            cache = cache_service.cache_for_instance(self)
            if cache.exists():
                return cache_service.pull_from_cache(self, _original_read)
            return cache_service.store_and_return(self, _original_read)

        readable_cls.read = read
        return readable_cls

    return decorator


def replace_local_input(cache_service: CachingService):
    def decorator(cls: Type[Readable]):
        _original_read = cls.read

        @wraps(cls.read)
        def read(self):
            if isasyncgenfunction(_original_read) or isgeneratorfunction(_original_read):
                self._read_count = 0
            return cache_service.pull_from_cache(self, _original_read)

        cls.read = read
        return cls

    return decorator


def save_known_good_output(cache_service: CachingService):
    def decorator(writable_cls: Type[Writable]):
        def write(self, obj):
            cache = cache_service.cache_for_instance(self)
            if not cache.exists():
                cache.update(obj)
            pass

        if iscoroutinefunction(writable_cls.write):
            write = async_unit(write)

        writable_cls.write = wraps(writable_cls.write)(write)
        return writable_cls

    return decorator


def compare_known_good_output(
    cache_service: CachingService,
    comparison: Dict = defaultdict(BasicComparer),
):
    def decorator(writable_cls: Type[Writable]):
        def write(self, obj):
            cache = cache_service.cache_for_instance(self)
            if not cache.exists():
                raise FileNotFoundError(f"No fixture found for {writable_cls}.")
            expected = cache.get()
            return comparison[writable_cls.__name__](expected, obj)

        if iscoroutinefunction(writable_cls.write):
            write = async_unit(write)

        writable_cls.write = wraps(writable_cls.write)(write)
        return writable_cls

    return decorator
