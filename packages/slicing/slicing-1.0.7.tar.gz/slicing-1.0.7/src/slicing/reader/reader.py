from slicing.stype.lines.end_normal_line import EndNormalLine
from slicing.stype.lines.end_procedure_line import EndProcedureLine
from slicing.stype.lines.ingore_line import IgnoreLine
from slicing.stype.lines.start_normal_line import StartNormalLine
from slicing.stype.lines.start_procedure_line import StartProcedureLine
from slicing.stype.state import State


class Reader:
    """
    通用 读取 SQL 的文件， 支持 DUMP 文件 ，增量脚本 ，全量脚本
    """
    def __init__(self):
        self.state = State.TO_BE

    def read(self, file, slicer):
        buffer = []
        for line in file:
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
