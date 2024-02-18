import time
import zipfile
from pathlib import Path

from slicing.reader.reader import Reader
from slicing.stmt.condition.always_true import AlwaysTrue
from slicing.stmt.condition.condition import Condition
from slicing.stype.slice import Slice


class ZipSlice(Slice):
    MAGIC = b'\x50\x4b\x03\x04'

    def __init__(self,
                 reader=Reader(),
                 before_condition: Condition = AlwaysTrue(),
                 after_condition: Condition = AlwaysTrue()):
        super().__init__(reader, before_condition, after_condition)

    @staticmethod
    def magic(file):
        with open(file, 'rb') as f:
            magic_byte = f.read(4)
        return magic_byte == ZipSlice.MAGIC

    def read(self, file: Path):
        if self.writer is None: raise Exception("Slice is not ready")
        with zipfile.ZipFile(file, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            for file_name in file_list:
                with zip_ref.open(file_name, 'r') as file:
                    self.statements(file)



