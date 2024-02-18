import time

import sqlparse

from slicing.constant import StatementKey, DOO
from slicing.stmt.condition.always_true import AlwaysTrue
from slicing.stmt.condition.condition import Condition
from slicing.stmt.tokens.fr0m import From
from slicing.stmt.tokens.alter import Alter
from slicing.stmt.tokens.call import Call
from slicing.stmt.tokens.create import Create
from slicing.stmt.tokens.delete import Delete
from slicing.stmt.tokens.drop import Drop
from slicing.stmt.tokens.function import Function
from slicing.stmt.tokens.identifier import Identifier
from slicing.stmt.tokens.index import Index
from slicing.stmt.tokens.insert import Insert
from slicing.stmt.tokens.into import Into
from slicing.stmt.tokens.on import On
from slicing.stmt.tokens.procedure import Procedure
from slicing.stmt.tokens.table import Table
from slicing.stmt.tokens.truncate import Truncate
from slicing.stmt.tokens.update import Update
from slicing.stmt.tokens.view import View


class Statement:
    def __init__(self, statement):
        self.original = statement
        # self.fragment = statement[0:self._range_index(statement)].decode("utf-8")
        self.fragment = self.get_fragment(statement)
        self.info = dict()

    def visitor(self):
        parsed = sqlparse.parse(self.fragment)
        if len(parsed) == 0: return
        for token in parsed[0].tokens:
            for token_class in [Create, Drop, Identifier, Insert, Table, Into,
                                Function, View, Procedure, Alter, Update, Index,
                                On, Call, Delete, From, Truncate]:
                if token_class.match(token):
                    token_class(token).accept(self)

    def table(self):
        return self.info.get(StatementKey.TableName.name, "").replace("`", "")

    def view(self):
        return self.info.get(StatementKey.ViewName.name, "").replace("`", "")

    def procedure(self):
        return self.info.get(StatementKey.ProcedureName.name, "").replace("`", "")

    def index(self):
        return self.info.get(StatementKey.IndexName.name, "").replace("`", "")

    def operate_object(self):
        if self.table() and self.index():
            return DOO.Index.name
        elif self.table():
            return DOO.Table.name
        elif self.view():
            return DOO.View.name
        elif self.procedure():
            return DOO.Procedure.name
        return ""

    def operate(self):
        return self.info.get(StatementKey.Type.name)

    def ignore(self):
        if self.info.get(StatementKey.Type.name) is None:
            return True
        if self.info.get(StatementKey.TableName.name) is None \
                and self.info.get(StatementKey.ViewName.name) is None \
                and self.info.get(StatementKey.ProcedureName.name) is None \
                and self.info.get(StatementKey.IndexName.name) is None:
            # return not condition.true(self)
            return True
        return False

    def mysql_version(self):
        return ["50001", "50013"]

    def operate_name(self):
        return self.file_name()

    def file_name(self):
        return self.index() or self.table() or self.view() or self.procedure()

    def get_fragment(self, statement):
        string = statement[0:self._range_index(statement)].decode("utf-8")
        for version in self.mysql_version():
            if string.startswith(f"/*!{version}"):
                string = string.replace(f"/*!{version}", "").replace("*/", "")
        return string

    def _range_index(self, line) -> int:
        def count(i):
            return i if i != -1 else None

        if line.startswith(b'INSERT') or line.startswith(b'insert') or line.startswith(b'Insert'):
            index = count(line.find(b"VALUES")) or count(line.find(b"values")) or count(line.find(b"Values"))
            if index: return index
        if line.startswith(b'CREATE') or line.startswith(b'Create') or line.startswith(b'create'):
            index = count(line.find(b"("))
            if index: return index
        if line.startswith(b"delimiter //") or line.startswith(b"Delimiter //") or line.startswith(b"DELIMITER //"):
            index = count(line.find(b"BEGIN")) or count(line.find(b"Begin")) or count(line.find(b"begin"))
            if index: return index
        if line.startswith(b"Alter") or line.startswith(b"ALTER") or line.startswith(b"alter"):
            index = count(line.find(b"ADD")) or count(line.find(b"Add")) or count(line.find(b"add"))
            if index: return index
            index = count(line.find(b"DROP")) or count(line.find(b"Drop")) or count(line.find(b"drop"))
            if index: return index
            index = count(line.find(b"MODIFY")) or count(line.find(b"Modify")) or count(line.find(b"modify"))
            if index: return index
            index = count(line.find(b"RENAME")) or count(line.find(b"Rename")) or count(line.find(b"rename")) or count(
                line.find(b"ReName"))
            if index: return index
        if line.startswith(b"UPDATE") or line.startswith(b"Update") or line.startswith(b"update"):
            index = count(line.find(b"SET")) or count(line.find(b"set")) or count(line.find(b"Set"))
            if index: return index
        if line.startswith(b"Delete") or line.startswith(b"DELETE") or line.startswith(b"delete"):
            index = count(line.find(b";")) or count(line.find(b";")) or count(line.find(b";"))
            if index: return index
        if line.startswith(b"Truncate") or line.startswith(b"TRUNCATE") or line.startswith(b"truncate"):
            index = count(line.find(b";")) or count(line.find(b";")) or count(line.find(b";"))
            if index: return index
        return 200
