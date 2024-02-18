from slicing.stmt.condition.condition import Condition


class AlwaysTrue(Condition):
    def true(self, statement): return True
