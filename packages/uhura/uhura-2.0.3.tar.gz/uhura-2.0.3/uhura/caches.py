import abc
import logging
import os
from abc import abstractmethod
from collections import defaultdict
from inspect import isasyncgenfunction, iscoroutinefunction, isgeneratorfunction
from typing import Callable, DefaultDict, Optional, Protocol, Type  # ParamSpec

from uhura.composition import async_unit, compose
from uhura.serde import Serde, DEFAULT_SERDE

logger = logging.getLogger("uhura.caches")


class Cache(abc.ABC):
    @abstractmethod
    def exists(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def get(self):
        raise NotImplementedError()

    @abstractmethod
    def update(self, obj):
        raise NotImplementedError()


class Cacheable(Protocol):
    _read_count: Optional[int]  # Created in streaming readables (generators, async iterators etc.)

    def cache_key(self):
        if hasattr(self, "_read_count"):
            return os.path.join(self.__class__.__name__, str(self._read_count))
        return self.__class__.__name__

    def get_serde(self) -> Serde:
        raise NotImplementedError()


class LocalCache(Cache):
    def __init__(self, path: str, serde=DEFAULT_SERDE) -> None:
        self._path = path
        self._serde = serde

    def exists(self):
        return os.path.exists(self._path)

    def update(self, obj):
        logger.info(f"Dumping to {self._path}")

        if not os.path.exists(os.path.dirname(self._path)):
            os.makedirs(os.path.dirname(self._path), exist_ok=True)
        self._serde.write_to_file(self._path, obj)
        return obj

    def get(self):
        return self._serde.read_from_file(self._path)

    @classmethod
    def cache_for_instance(cls, cacheable: Cacheable, base_path: str):
        return cls(os.path.join(base_path, cacheable.cache_key()), cacheable.get_serde())


async def _take(async_iterable, n=5):
    index = 0
    async for item in async_iterable:
        index += 1
        if index > n:
            break
        yield item


def _sync_take(iterable, n=5):
    index = 0
    for item in iterable:
        index += 1
        if index > n:
            break
        yield item


class CachingService:
    def __init__(self, lookup, base_path, depth=4):
        self._base_path = base_path
        self._depth = depth
        self._lookup: DefaultDict[str, Callable[[Cacheable, str, ...], Cache]] = lookup

    def _iterate_from_cache(self, instance: Cacheable):
        for _ in range(self._depth):
            cache = self.cache_for_instance(instance)
            yield cache.get()
            instance._read_count += 1

    def cache_for_instance(self, instance: Cacheable):
        return self._lookup[instance.cache_key()](instance, self._base_path)

    def store_and_return(self, instance: Cacheable, method):
        def _update(value):
            cache = self.cache_for_instance(instance)
            if cache.exists():
                return cache.get()
            else:
                cache.update(value)
                return value

        if isasyncgenfunction(method):
            return _take(compose(method, _update)(instance), n=self._depth)
        if isgeneratorfunction(method):
            return _sync_take(compose(method, _update)(instance), n=self._depth)
        return compose(method, _update)(instance)

    def pull_from_cache(self, instance: Cacheable, original_method):
        if isasyncgenfunction(original_method):
            return async_unit(self._iterate_from_cache(instance))
        if isgeneratorfunction(original_method):
            return self._iterate_from_cache(instance)
        if iscoroutinefunction(original_method):
            return async_unit(self.cache_for_instance(instance).get())
        return self.cache_for_instance(instance).get()

    @classmethod
    def default(cls, base_path, **kwargs):
        return cls(
            lookup=defaultdict(lambda: LocalCache.cache_for_instance),
            base_path=base_path,
            **kwargs,
        )
