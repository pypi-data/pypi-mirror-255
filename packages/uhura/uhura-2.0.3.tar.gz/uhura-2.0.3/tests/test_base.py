from uhura.base import Readable, Writable


def test_sync_read():
    class Reader(Readable[int]):
        async def read(self) -> int:
            return 1

    assert Reader().sync_read() == 1


def test_sync_write():
    has_been_written = False

    class Writer(Writable[int]):
        async def write(self, obj):
            nonlocal has_been_written
            has_been_written = True
            pass

    Writer().sync_write(1)
    assert has_been_written
