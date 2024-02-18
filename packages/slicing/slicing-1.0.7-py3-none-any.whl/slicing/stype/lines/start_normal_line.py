from slicing.stype.lines.line import Line
from slicing.stype.state import State


class StartNormalLine(Line):
    """
    需放在最后，排除掉所有的特殊行就是普通行
    """
    def match(self, line):
        return True

    def accept(self, slicer):
        if slicer.state == slicer.state.IGNORE: return
        if slicer.state == slicer.state.START_CREATE_PROCEDURE: return
        slicer.state = State.START_NORMAL
