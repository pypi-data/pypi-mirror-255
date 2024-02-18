from slicing.constant import FilterType, DOP
from slicing.stmt.condition.condition import Condition
from slicing.stmt.condition.table_operate_conditional import TableOperateConditional


class DumpTableCondition(Condition):
    """
    内置的针对Table的过滤
    """
    def __init__(self, tables: list[str], filter_type=FilterType.Include):
        super().__init__(filter_type=filter_type)
        self.add_expect(TableOperateConditional.expect(operate=DOP.Insert, tables=tables))
        self.add_expect(TableOperateConditional.expect(operate=DOP.Create, tables=tables))
        self.add_expect(TableOperateConditional.expect(operate=DOP.Drop, tables=tables))

