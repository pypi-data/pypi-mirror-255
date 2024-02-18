from slicing.stype.lines.line import Line
from slicing.stype.state import State


class EndProcedureLine(Line):
    def match(self, line):
        return line.startswith(b'delimiter ;') or line.startswith(b'Delimiter ;') or line.startswith(b'DELIMITER ;')

    def accept(self, slicer):
        if slicer.state == State.IGNORE: return
        if slicer.state == State.START_CREATE_PROCEDURE:
            slicer.state = State.END_CREATE_PROCEDURE
