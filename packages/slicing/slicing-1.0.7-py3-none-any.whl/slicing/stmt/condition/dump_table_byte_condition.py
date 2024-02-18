from slicing.constant import FilterType
from slicing.stmt.condition.bytes_conditional import BytesConditional
from slicing.stmt.condition.condition import Condition


class DumpTableByteCondition(Condition):
    def __init__(self, tables: list[str], filter_type=FilterType.Include):
        super().__init__(filter_type)
        for table in tables:
            self.add_expect(BytesConditional(f'INSERT INTO `{table}`'))
            self.add_expect(BytesConditional(f'CREATE TABLE `{table}`'))
            self.add_expect(BytesConditional(f'DROP TABLE IF EXISTS `{table}`'))
        # self.add_expect(TableOperateConditional.expect(operate=DOP.Insert, tables=tables, filter_type=filter_type))
        # self.add_expect(TableOperateConditional.expect(operate=DOP.Create, tables=tables, filter_type=filter_type))
        # self.add_expect(TableOperateConditional.expect(operate=DOP.Drop, tables=tables, filter_type=filter_type))
