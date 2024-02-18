import time
from pathlib import Path

from slicing.constant import DOP, DOO, FilterType
from slicing.factory import SliceFactory
from slicing.stmt.condition.condition import Condition
from slicing.stmt.condition.conditional import Conditional


if __name__ == '__main__':
    start = time.perf_counter()
    # 修改的文件路径
    path = Path("D:\\aws\\eclinical40_auto_testing\\slicing\\src\\slicing\\tests\\resources")
    file = path.joinpath(Path("V49__iwrs_business_schema_initial_sql.sql"))

    condition = Condition(filter_type=FilterType.Include)
    condition.add_expect(Conditional(DOP.Create,  # 指定操作
                                     DOO.View,  # 指定操作的对象索引
                                     assert_values=["v_siteinventory", "v_inventory"]  # 要生成的索引名
                                     )
                         )
    condition.add_expect(Conditional(DOP.Drop,  # 指定操作
                                     DOO.View,  # 指定操作的对象索引
                                     assert_values=["v_siteinventory", "v_inventory"]  # 要生成的索引名
                                     )
                         )
    tid = SliceFactory.slice(absolute_file_path=file, absolute_out_put_folder=Path("Result"), after_condition=condition)

    print(tid)
    print("wait:", time.perf_counter() - start)
