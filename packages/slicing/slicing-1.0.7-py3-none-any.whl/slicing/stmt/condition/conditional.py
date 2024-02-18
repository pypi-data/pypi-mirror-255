import abc
import time

from slicing.constant import FilterType, DOP, DOO


class Conditional:

    # def __init__(self, operate: DOP, operate_object: DOO, assert_values: list[str], filter_type: FilterType):
    def __init__(self, operate: DOP, operate_object: DOO, assert_values: list[str]):
        self.operate = operate
        self.assert_values = assert_values
        # self.filter_type = filter_type
        self.operate_object = operate_object

    # TODO BUG
    def true(self, statement):
        if statement.operate_name() in self.assert_values:
            if statement.operate() == self.operate.name.upper():
                if statement.operate_object() == self.operate_object.name:
                    return True
                    # return self.TRUE()
        return False
        # return self.FALSE()

    # def TRUE(self): return True if self.filter_type == FilterType.Include else False

    # def FALSE(self): return False if self.filter_type == FilterType.Include else True
