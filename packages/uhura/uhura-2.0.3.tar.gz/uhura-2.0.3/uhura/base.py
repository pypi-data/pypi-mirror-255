import asyncio
import os
from abc import ABC, abstractmethod
from inspect import isasyncgenfunction, iscoroutinefunction, isgeneratorfunction, unwrap
from typing import Generic, Type, TypeVar

from uhura.serde import DEFAULT_SERDE
from uhura.caches import Cache, LocalCache
from uhura.decorables import Decorable

ReadType = TypeVar("ReadType")
WriteType = TypeVar("WriteType")


class Readable(Decorable, ABC, Generic[ReadType]):
    def __init_subclass__(cls) -> None:
        if isasyncgenfunction(cls.read):
            cls.read = _as_stream_read(cls.read)
        elif isgeneratorfunction(cls.read):
            cls.read = _as_sync_stream_read(cls.read)
        super().__init_subclass__()

    @abstractmethod
    async def read(self) -> ReadType:
        raise NotImplementedError()

    def sync_read(self) -> ReadType:
        if iscoroutinefunction(unwrap(self.read)):
            return asyncio.run(self.read())
        return self.read()

    def get_serde(self):
        return DEFAULT_SERDE

    def cache_key(self):
        if hasattr(self, "_read_count"):
            return f"{os.path.join(self.__class__.__name__, str(self._read_count))}{self.get_serde().file_extension}"
        return f"{self.__class__.__name__}{self.get_serde().file_extension}"


def _as_stream_read(read_method):
    async def read(self):
        self._read_count = 0
        async for item in read_method(self):
            yield item
            self._read_count += 1

    return read


def _as_sync_stream_read(read_method):
    def read(self):
        self._read_count = 0
        for item in read_method(self):
            yield item
            self._read_count += 1

    return read


class Writable(Decorable, ABC, Generic[WriteType]):
    @abstractmethod
    async def write(self, obj: WriteType):
        raise NotImplementedError()

    def sync_write(self, obj: WriteType):
        if iscoroutinefunction(unwrap(self.write)):
            return asyncio.run(self.write(obj))
        return self.write(obj)

    def get_serde(self):
        return DEFAULT_SERDE

    def cache_key(self):
        return f"{self.__class__.__name__}{self.get_serde().file_extension}"
