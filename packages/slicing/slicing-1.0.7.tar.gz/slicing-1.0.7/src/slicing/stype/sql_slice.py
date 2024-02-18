import time
from pathlib import Path

from slicing.reader.reader import Reader
from slicing.stmt.condition.always_true import AlwaysTrue
from slicing.stmt.condition.condition import Condition
from slicing.stype.slice import Slice


class SQLSlice(Slice):
    def __init__(self,
                 reader=Reader(),
                 before_condition: Condition = AlwaysTrue(),
                 after_condition: Condition = AlwaysTrue()):
        super().__init__(reader, before_condition, after_condition)
    def read(self, file: Path):
        if self.writer is None: raise Exception("Slice is not ready")
        with open(file, 'rb') as file:
            self.statements(file)



