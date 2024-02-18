from dataclasses import dataclass


@dataclass
class FileInfo:
    sql_type: str
    name: str # 文件名
    table: str # 表名
    id: str
    size: int # 单位字节
    no: int # 顺序编号
    view: str # 视图名
    procedure: str # 过程名
    index: str # 索引名
    operate_object: str # 操作的对象 Table | View | Procedure
