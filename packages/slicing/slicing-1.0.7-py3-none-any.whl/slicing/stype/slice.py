import abc
import uuid
from pathlib import Path

from slicing.info.file_info_writer import FileInfoWriter

from slicing.reader.reader import Reader
from slicing.stmt.condition.always_true import AlwaysTrue
from slicing.stmt.condition.condition import Condition
from slicing.stype.line_number import LineNumber

from slicing.stype.state import State
from slicing.writer import Writer


class Slice(abc.ABC):

    def __init__(self, reader=Reader(),
                 before_condition: Condition = AlwaysTrue(),
                 after_condition: Condition = AlwaysTrue()):
        self._out_put = "xxxx"
        self.line_no = LineNumber()
        self.writer = None
        self._task_id = None
        self._file_list_writer = None
        self.state = State.TO_BE
        self.before_condition = before_condition
        self.after_condition = after_condition
        self.reader = reader
        self.test_flag = -1

    def ready(self, out_put):
        """
        指定输出的文件夹路径，并启动写文件的线程
        :param out_put:
        :type out_put:
        :return:
        :rtype:
        """
        self.out_put = out_put
        self.writer = Writer(self, self.line_no, self.before_condition, self.after_condition)
        self._file_list_writer = FileInfoWriter(Path(self.out_put).joinpath(self.task_id))
        self._file_list_writer.set_id(self.task_id)
        self.writer.start()

    @property
    def out_put(self):
        return self._out_put

    @property
    def file_list_writer(self):
        return self._file_list_writer

    @out_put.setter
    def out_put(self, value):
        self._out_put = value

    @abc.abstractmethod
    def read(self, file: Path):
        ...

    def slice(self, file: Path):
        try:
            self.read(file)
            self.join()
            self.file_list_writer.write()
        except Exception as e:
            self.writer.stop()
            raise e

    def statements(self, file):
        self.reader.read(file, slicer=self)
        # DumpReader(tables=["eclinical_study", "eclinical_study_site"]).read(file, slicer=self)
        # Reader().read(file, self)
        # buffer = []
        # for line in file:
        #     self.test_code(line)
        #     if self.test_flag == -1: continue
        #     if self.test_flag == 0:
        #         self.test_flag = 1
        #         continue
        #     if self.test_flag == -100: break
        #
        #     for s in [IgnoreLine(),
        #               StartNormalLine(),
        #               StartProcedureLine(),
        #               EndProcedureLine(),
        #               EndNormalLine()]:
        #         if s.match(line):
        #             s.accept(self)
        #     if self.state == State.IGNORE:
        #         if self.state != State.START_CREATE_PROCEDURE:
        #             self.state = State.TO_BE
        #         continue
        #     elif self.state == State.START_NORMAL:
        #         buffer.append(line)
        #     elif self.state == State.END_NORMAL:
        #         buffer.append(line)
        #         self.writer.add_statements(buffer.copy())
        #         self.state = State.TO_BE
        #         buffer = []
        #     elif self.state == State.START_CREATE_PROCEDURE:
        #         buffer.append(line)
        #     elif self.state == State.END_CREATE_PROCEDURE:
        #         buffer.append(line)
        #         self.writer.add_statements(buffer.copy())
        #         self.state = State.TO_BE
        #         buffer = []
        #
        # self.last_line(buffer)
        self.writer.finish()

    def last_line(self, buffer):
        """
        处理最后一行，没有换行符的情况
        :param buffer:
        :type buffer:
        :return:
        :rtype:
        """
        if len(buffer) > 0:
            if self.state == State.START_NORMAL:
                self.writer.add_statements(buffer.copy())

    @property
    def task_id(self):
        if self._task_id is None:
            self._task_id = str(uuid.uuid4()).replace("-", "")
        return self._task_id

    def join(self):
        self.writer.join()
