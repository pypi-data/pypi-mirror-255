import enum


class StatementKey(enum.Enum):
    # Table = 1
    # View = 2
    # Procedure = 3
    # Create = 4
    # Update = 5
    # Alter = 6
    Modify = 7
    Type = 8
    TableName = 9
    WaitFill = 10
    ProcedureName = 11
    # Insert = 12
    # Drop = 13
    Into = 14
    ViewName = 15
    # Call = 16
    IndexName = 17
    On = 18
    # Index = 19
    From = 20
    # Delete = 21
    # Truncate = 22


class DOP(enum.Enum):
    """
    DatabaseOperate 简称 DOP
    """
    Create = 104
    Drop = 105
    Alter = 106
    Insert = 107
    Update = 108
    Delete = 109
    Call = 110
    Truncate = 111


class DOO(enum.Enum):
    """
    DatabaseOperateObject 简称 DOO
    """
    Table = 700
    Index = 701
    View = 702
    Procedure = 703


class ListFileInfo(enum.Enum):
    INSERT = 11
    CREATE = 12
    DROP = 13
    ALTER = 14
    UPDATE = 15
    MODIFY = 16
    CALL = 17
    ALL = 18
    TRUNCATE = 19
    DELETE = 20


class FilterType(enum.Enum):
    Include = 100  # 生成满足条件
    Exclude = 101  # 排除满足条件
