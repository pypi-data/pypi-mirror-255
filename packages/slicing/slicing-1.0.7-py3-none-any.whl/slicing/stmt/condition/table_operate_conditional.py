from slicing.constant import DOP, FilterType, DOO
from slicing.stmt.condition.conditional import Conditional


class TableOperateConditional(Conditional):
    # def __init__(self, operate: DOP, tables: list[str], filter_type: FilterType):
    #     super().__init__(operate, DOO.Table, tables, filter_type)
    def __init__(self, operate: DOP, tables: list[str]):
        super().__init__(operate, DOO.Table, tables)

    @classmethod
    def expect(cls, operate: DOP, tables: list[str]):
        return TableOperateConditional(operate, tables)
