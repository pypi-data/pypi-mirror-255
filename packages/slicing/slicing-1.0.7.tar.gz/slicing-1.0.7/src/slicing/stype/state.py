import enum


class State(enum.Enum):
    TO_BE = 888
    START_CREATE_PROCEDURE = 999
    END_CREATE_PROCEDURE = 998
    START_NORMAL = 997
    END_NORMAL = 996
    IGNORE = 995


class DumpState(enum.Enum):
    WaitTable = -1
    StartTable = 0
    ChangeTable = 1

