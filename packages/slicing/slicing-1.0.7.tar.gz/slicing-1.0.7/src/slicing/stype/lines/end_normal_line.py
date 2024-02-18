from slicing.stype.lines.line import Line
from slicing.stype.state import State


class EndNormalLine(Line):
    def match(self, line):
        return line.endswith(b';\n') or line.endswith(b';\n\r') or line.endswith(b';\r\n')

    def accept(self, slicer):
        if slicer.state == State.IGNORE: return
        if slicer.state == State.START_NORMAL or slicer.state == State.END_NORMAL:
            slicer.state = State.END_NORMAL
