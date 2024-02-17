import asyncio

import pytest

from uhura import Readable, Writable
from functools import wraps


class ReadOne(Readable[int]):
    async def read(self):
        return 1


def _make_read_two(cls):
    @wraps(cls.read)
    async def read(self):
        return 2

    cls.read = read
    pass


def test_can_add_and_remove_decorators_to_existing_readables():
    read_one = ReadOne()
    assert asyncio.run(read_one.read()) == 1
    Readable.add_decorator(_make_read_two)
    assert asyncio.run(read_one.read()) == 2, "Decorator failed to apply to existing readable"
    Readable.remove_last_decorator()
    assert asyncio.run(read_one.read()) == 1, "Decorator was not removed from existing readable"


def test_decorators_only_apply_one_mro_layer_deep():
    class Read1(ReadOne):
        pass

    class ReadUno(Read1):
        async def read(self):
            return 3

    with Readable.decorated_with(_make_read_two):
        assert asyncio.run(ReadUno().read()) == 3  # Not covered by uhura
        assert asyncio.run(Read1().read()) == 2
    assert asyncio.run(Read1().read()) == 1


def test_can_add_and_remove_decorators_to_new_readables():
    Readable.add_decorator(_make_read_two)

    class NewReadOne(Readable[int]):
        async def read(self):
            return 1

    new_read_one = NewReadOne()
    assert asyncio.run(new_read_one.read()) == 2, "Decorator failed to apply to new readable"
    Readable.remove_last_decorator()
    assert asyncio.run(new_read_one.read()) == 1, "Decorator was not removed from new readable"

    class OtherNewReadOne(Readable[int]):
        async def read(self):
            return 1

    other_new_read_one = OtherNewReadOne()
    assert (
        asyncio.run(other_new_read_one.read()) == 1
    ), "Decorator is still being applied to future readables!"


def _make_read_three(cls):
    @wraps(cls.read)
    async def read(self):
        return 3

    cls.read = read
    pass


def test_can_decorate_new_readables_multiple_times():
    Readable.add_decorator(_make_read_two)
    Readable.add_decorator(_make_read_three)

    class NewReadOne(Readable[int]):
        async def read(self):
            return 1

    new_read_one = NewReadOne()
    assert asyncio.run(new_read_one.read()) == 3, "Decorator failed to apply to new readable"
    Readable.remove_last_decorator()
    assert (
        asyncio.run(new_read_one.read()) == 2
    ), "Last decorator was not removed from new readable"
    Readable.remove_last_decorator()
    assert (
        asyncio.run(new_read_one.read()) == 1
    ), "All decorators were not removed from new readable"

    class OtherNewReadOne(Readable[int]):
        async def read(self):
            return 1

    other_new_read_one = OtherNewReadOne()
    assert (
        asyncio.run(other_new_read_one.read()) == 1
    ), "Decorator is still being applied to future readables!"


def test_can_decorate_existing_readables_multiple_times():
    read_one = ReadOne()
    assert asyncio.run(read_one.read()) == 1
    with Readable.decorated_with(_make_read_two):
        assert asyncio.run(read_one.read()) == 2, "Decorator failed to apply to existing readable"
        with Readable.decorated_with(_make_read_three):
            assert (
                asyncio.run(read_one.read()) == 3
            ), "Second Decorator failed to apply to existing readable"
        assert (
            asyncio.run(read_one.read()) == 2
        ), "Second Decorator was not removed from existing readable"
    assert (
        asyncio.run(read_one.read()) == 1
    ), "First Decorator was not removed from existing readable"


class DummyClient(Readable[int], Writable[int]):
    async def read(self) -> int:
        return 1

    async def write(self, obj: int):
        pass


def test_multiple_inheritance_chains_dont_mess_with_each_other():
    dummy_client = DummyClient()

    def break_write(cls):
        @wraps(cls.write)
        async def write(self, obj):
            raise ValueError

        cls.write = write
        return cls

    Readable.add_decorator(_make_read_two)
    Writable.add_decorator(break_write)
    assert asyncio.run(dummy_client.read()) == 2, "Decoration failed"
    with pytest.raises(ValueError):
        asyncio.run(dummy_client.write(1))
    Readable.remove_last_decorator()
    with pytest.raises(ValueError):
        asyncio.run(dummy_client.write(2))
    Writable.remove_last_decorator()


def test_test_multiple_inheritance_future_works():
    Readable.add_decorator(_make_read_two)

    def break_write(cls):
        @wraps(cls.write)
        async def write(self, obj):
            raise ValueError

        cls.write = write
        return cls

    Writable.add_decorator(break_write)

    class NewReadable(Readable):
        async def read(self):
            pass

    Readable.remove_last_decorator()
    Writable.remove_last_decorator()
