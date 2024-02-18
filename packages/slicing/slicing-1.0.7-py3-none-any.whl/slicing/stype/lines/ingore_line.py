import re

from slicing.stype.lines.line import Line
from slicing.stype.state import State


class IgnoreLine(Line):
    def match(self, line):
        return self.empty_line(line) or self.comment_line(line)

    def accept(self, slicer):
        if slicer.state == State.TO_BE:
            slicer.state = State.IGNORE

    def empty_line(self, line):
        """
        判断是否是空行
        :param line:
        :type line:
        :return:
        :rtype:
        """
        return line == b'\r\n' or line == b'\n\r' or line == b'\n'

    def comment_line(self, line):
        """
        判断是注释行
        :param line:
        :type line:
        :return:
        :rtype:
        """
        if line.startswith(b'--') or line.startswith(b'/*'):
            if line.startswith(b'/*!'):
                return False
            patterns = [r'\-\-.*', r'\*.*?\*/']
            for pattern in patterns:
                if re.search(re.compile(pattern), line.decode()):
                    return True
        return False
