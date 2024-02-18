import logging
import os
import threading
import time

import uuid
from pathlib import Path
from queue import Queue

from slicing.stmt.condition.always_true import AlwaysTrue
from slicing.stmt.condition.condition import Condition
from slicing.stmt.statement import Statement
from slicing.stype.line_number import LineNumber

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.ERROR)
handler = logging.FileHandler("MissSQLStatement.txt")
handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class Writer(threading.Thread):
    def __init__(self, slice_ins, line_number: LineNumber,
                 before_condition: Condition = AlwaysTrue(),
                 after_condition: Condition = AlwaysTrue()):
        super().__init__()
        self._slice_ins = slice_ins
        self.__out_path_folder = Path(slice_ins.out_put).joinpath(slice_ins.task_id)
        self.sql_statements = Queue()
        # self._finish = False
        self.stop_event = threading.Event()
        self.line_number = line_number
        self.after_condition = after_condition
        self.before_condition = before_condition

    def add_statements(self, statements: list[bytes]):
        self.sql_statements.put(statements)

    def write_file(self, sql_statement_bytes: list[bytes]):

        statement = Statement(b''.join(sql_statement_bytes))
        if not self.before_condition.true(statement): return

        statement.visitor()

        if not statement.ignore():
            if not self.after_condition.true(statement): return
            self.line_number.add()
            folder = self.create_folder(statement.operate())
            name = statement.file_name()

            file_id = str(uuid.uuid4()).replace("-", "")
            file_name = f'{name}-{file_id}'
            with open(folder.joinpath(Path(f'{file_name}.sql')), 'ab') as f:
                # if statement.operate().upper() == Constant.Create.name.upper():
                #     if statement.operate_object() == Constant.Table.name:
                #         f.write(f'DROP TABLE IF EXISTS `{name}`;\n'.encode("UTF-8"))
                #     elif statement.operate_object() == Constant.View.name:
                #         f.write(f'DROP VIEW IF EXISTS `{name}`;\n'.encode("UTF-8"))
                for sql_bytes in sql_statement_bytes:
                    f.write(sql_bytes)
            size = os.path.getsize(folder.joinpath(Path(f'{file_name}.sql')))
            self._slice_ins.file_list_writer.add_sql(file_id, statement, size, self.line_number)
        else:
            logger.error(statement.original)

    def create_folder(self, operate):
        path = self.__out_path_folder.joinpath(operate)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        return path

    def run(self):
        try:
            while not self.stop_event.is_set():
                # if self.sql_statements.qsize() > 0:
                sql_statement_bytes = self.sql_statements.get()
                if sql_statement_bytes == "Thread Stop": break
                self.write_file(sql_statement_bytes)

        except Exception as e:
            raise e

    def finish(self):
        self.sql_statements.put("Thread Stop")

    def stop(self):
        self.stop_event.set()
        self.finish()


    # def _range_index(self, line) -> int:
    #     def count(i):
    #         return i if i != -1 else None
    #
    #     if line.startswith(b'INSERT') or line.startswith(b'insert') or line.startswith(b'Insert'):
    #         index = count(line.find(b"VALUES")) or count(line.find(b"values")) or count(line.find(b"Values"))
    #         if index: return index
    #     if line.startswith(b'CREATE') or line.startswith(b'Create') or line.startswith(b'create'):
    #         index = count(line.find(b"("))
    #         if index: return index
    #     if line.startswith(b"delimiter //") or line.startswith(b"Delimiter //") or line.startswith(b"DELIMITER //"):
    #         index = count(line.find(b"BEGIN")) or count(line.find(b"Begin")) or count(line.find(b"begin"))
    #         if index: return index
    #     if line.startswith(b"Alter") or line.startswith(b"ALTER") or line.startswith(b"alter"):
    #         index = count(line.find(b"ADD")) or count(line.find(b"Add")) or count(line.find(b"add"))
    #         if index: return index
    #         index = count(line.find(b"DROP")) or count(line.find(b"Drop")) or count(line.find(b"drop"))
    #         if index: return index
    #         index = count(line.find(b"MODIFY")) or count(line.find(b"Modify")) or count(line.find(b"modify"))
    #         if index: return index
    #         index = count(line.find(b"RENAME")) or count(line.find(b"Rename")) or count(line.find(b"rename")) or count(
    #             line.find(b"ReName"))
    #         if index: return index
    #     if line.startswith(b"UPDATE") or line.startswith(b"Update") or line.startswith(b"update"):
    #         index = count(line.find(b"SET")) or count(line.find(b"set")) or count(line.find(b"Set"))
    #         if index: return index
    #     if line.startswith(b"Delete") or line.startswith(b"DELETE") or line.startswith(b"delete"):
    #         index = count(line.find(b";")) or count(line.find(b";")) or count(line.find(b";"))
    #         if index: return index
    #     if line.startswith(b"Truncate") or line.startswith(b"TRUNCATE") or line.startswith(b"truncate"):
    #         index = count(line.find(b";")) or count(line.find(b";")) or count(line.find(b";"))
    #         if index: return index
    #     return 200
