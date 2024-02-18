from slicing.constant import FilterType
from slicing.stmt.condition.conditional import Conditional


class BytesConditional(Conditional):
    def __init__(self, string: str):
        super().__init__(None, None, [])
        self.string = string

    def true(self, statement):
        if statement.fragment.startswith(self.string):
            return True
        return False

