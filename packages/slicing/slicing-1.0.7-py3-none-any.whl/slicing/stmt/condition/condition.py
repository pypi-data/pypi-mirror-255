from functools import reduce

from slicing.stmt.condition.conditional import Conditional
from slicing.constant import FilterType


class Condition:
    def __init__(self, filter_type=FilterType.Include):
        self.conditionals: list[Conditional] = []
        self.filter_type = filter_type

    def true(self, statement):
        if self.filter_type == FilterType.Include:
            return reduce(lambda x, y: x or y, [conditional.true(statement) for conditional in self.conditionals])
        else:
            return not reduce(lambda x, y: x or y, [conditional.true(statement) for conditional in self.conditionals])


    def add_expect(self, conditional: Conditional):
        self.conditionals.append(conditional)

    def TRUE(self, flag): return flag if self.filter_type == FilterType.Include else False

    def FALSE(self, flag): return not flag if self.filter_type == FilterType.Exclude else not flag
