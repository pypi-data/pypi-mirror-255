from slicing.reader.reader import Reader
from slicing.stype.lines.end_normal_line import EndNormalLine
from slicing.stype.lines.end_procedure_line import EndProcedureLine
from slicing.stype.lines.ingore_line import IgnoreLine
from slicing.stype.lines.start_normal_line import StartNormalLine
from slicing.stype.lines.start_procedure_line import StartProcedureLine
from slicing.stype.state import State, DumpState


class DumpReader:
    """
    专门处理 Dump 的大数据库的文件, 只支持 DUMP 文件
    """
    def __init__(self, tables: list[str]):
        self.state = State.TO_BE
        self.table_state = dict.fromkeys(tables, 0)
        self.pre_table = None
        self.dump_state = DumpState.WaitTable

    def condition(self):
        return [self.start_table_structure(table) for table in self.table_state.keys()]

    def start_table_structure(self, table):
        return f'Table structure for table `{table}`'.encode()

    def all_done(self):
        for table, state in self.table_state.items():
            if state == 0: return False
        return True

    def want(self, line):
        for table in self.table_state.keys():
            if self.pre_table is not None:
                self.dump_state = DumpState.ChangeTable
            if self.start_table_structure(table) in line:
                if self.dump_state == DumpState.WaitTable:
                    self.pre_table = table
                else:
                    self.table_state[self.pre_table] = 1
                    self.pre_table = table
                self.dump_state = DumpState.StartTable
                return True
        return False

    def read(self, file, slicer):
        buffer = []
        for line in file:
            if self.all_done(): break
            if b'Table structure for table' in line:
                if not self.want(line):
                    if self.pre_table is not None:
                        self.table_state[self.pre_table] = 1
                # for table in self.table_state.keys():
                #     if self.pre_table is not None:
                #         self.dump_state = DumpState.ChangeTable
                #     if self.start_table_structure(table) in line:
                #         if self.dump_state == DumpState.WaitTable:
                #             self.pre_table = table
                #         else:
                #             self.table_state[self.pre_table] = 1
                #             self.pre_table = table
                #         self.dump_state = DumpState.StartTable


            if self.dump_state == DumpState.WaitTable or self.dump_state == DumpState.ChangeTable: continue
            for s in [IgnoreLine(),
                      StartNormalLine(),
                      StartProcedureLine(),
                      EndProcedureLine(),
                      EndNormalLine()]:
                if s.match(line):
                    s.accept(self)
            if self.state == State.IGNORE:
                if self.state != State.START_CREATE_PROCEDURE:
                    self.state = State.TO_BE
                continue
            elif self.state == State.START_NORMAL:
                buffer.append(line)
            elif self.state == State.END_NORMAL:
                buffer.append(line)
                slicer.writer.add_statements(buffer.copy())
                self.state = State.TO_BE
                buffer = []
            elif self.state == State.START_CREATE_PROCEDURE:
                buffer.append(line)
            elif self.state == State.END_CREATE_PROCEDURE:
                buffer.append(line)
                slicer.writer.add_statements(buffer.copy())
                self.state = State.TO_BE
                buffer = []

        self.last_line(slicer, buffer)

    def last_line(self, slicer, buffer):
        """
        处理最后一行，没有换行符的情况
        :param slicer:
        :type slicer:
        :param buffer:
        :type buffer:
        :return:
        :rtype:
        """
        if len(buffer) > 0:
            if self.state == State.START_NORMAL:
                slicer.writer.add_statements(buffer.copy())
