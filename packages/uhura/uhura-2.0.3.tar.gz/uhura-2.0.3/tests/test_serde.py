from uhura.serde import PickleSerde
from uhura.base import Readable
from uhura.modes import fixture_builder_mode, task_test_mode
from tempfile import TemporaryDirectory
import os


class FakeSerde(PickleSerde):
    file_extension = ".blah"

    def __init__(self):
        self.has_been_read = False
        self.has_been_written = False

    def read_from_file(self, file):
        self.has_been_read = True
        return super().read_from_file(file)

    def write_to_file(self, file, obj):
        self.has_been_written = True
        return super().write_to_file(file, obj)


def test_can_have_custom_serde():
    test_serde = FakeSerde()

    class FakeReader(Readable):
        def read(self):
            return 1

        def get_serde(self):
            return test_serde

    with TemporaryDirectory() as root:
        with fixture_builder_mode(
            input_path=os.path.join(root, "input"), known_good_path=os.path.join(root, "output")
        ):
            client = FakeReader()
            assert not test_serde.has_been_read
            assert not test_serde.has_been_written
            client.read()
            assert test_serde.has_been_written
            assert os.path.exists(os.path.join(root, "input", "FakeReader.blah"))
            assert not test_serde.has_been_read
            client.read()
            assert test_serde.has_been_read
