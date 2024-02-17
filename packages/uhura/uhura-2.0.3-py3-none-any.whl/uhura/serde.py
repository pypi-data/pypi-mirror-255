import pickle
from typing import TypeVar, Generic, ClassVar, Any

import pandas as pd

SerdeType = TypeVar("SerdeType")


class Serde(Generic[SerdeType]):
    file_extension: ClassVar[str]

    def read_from_file(self, file) -> SerdeType:
        raise NotImplementedError()

    def write_to_file(self, file, obj: SerdeType):
        raise NotImplementedError()


class PickleSerde(Serde[Any]):
    file_extension = ".pkl"

    def read_from_file(self, file) -> SerdeType:
        with open(file, "rb") as infile:
            return pickle.load(infile)

    def write_to_file(self, file, obj: SerdeType):
        with open(file, "wb") as outfile:
            return pickle.dump(obj, outfile)


DEFAULT_SERDE = PickleSerde()


class ParquetSerde(Serde[pd.DataFrame]):
    file_extension = ".parquet"  # Used in cache key

    def __init__(self, read_kwargs=None, write_kwargs=None):
        self._read_kwargs = read_kwargs if read_kwargs is not None else {}
        self._write_kwargs = write_kwargs if write_kwargs is not None else {}

    def read_from_file(self, file: str) -> pd.DataFrame:
        return pd.read_parquet(file, **self._read_kwargs)

    def write_to_file(self, file: str, obj: pd.DataFrame):
        return obj.to_parquet(file, **self._write_kwargs)
