import time
from pathlib import Path
import gzip

from slicing.reader.reader import Reader
from slicing.stmt.condition.always_true import AlwaysTrue
from slicing.stmt.condition.condition import Condition
from slicing.stype.slice import Slice


class GZSlice(Slice):
    MAGIC = b'\x1f\x8b'

    def __init__(self, reader=Reader(),
                 before_condition: Condition = AlwaysTrue(),
                 after_condition: Condition = AlwaysTrue()):
        super().__init__(reader, before_condition, after_condition)

    @staticmethod
    def magic(file):
        with open(file, 'rb') as f:
            magic_byte = f.read(2)
        return magic_byte == GZSlice.MAGIC


    def read(self, file: Path):
        if self.writer is None: raise Exception("Slice is not ready")
        with gzip.open(file, mode='rb') as f:
            self.statements(f)



