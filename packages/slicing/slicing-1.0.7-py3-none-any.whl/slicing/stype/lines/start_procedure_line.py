from slicing.stype.lines.line import Line
from slicing.stype.state import State


class StartProcedureLine(Line):
    def match(self, line):
        return line.startswith(b'delimiter //') or line.startswith(b'DELIMITER //') or line.startswith(b'Delimiter //')

    def accept(self, slicer):
        if slicer.state == State.IGNORE: return
        slicer.state = State.START_CREATE_PROCEDURE
