import sqlparse.sql

from slicing.constant import StatementKey, DOP
from slicing.stmt.tokens.identifier import Identifier


class Function:
    def __init__(self, token):
        self._token = token

    @classmethod
    def match(cls, token):
        return type(token) == sqlparse.sql.Function

    def accept(self, statement):
        self._insert(statement) or self._create_procedure(statement) or self._call_procedure(statement)

    def _insert(self, statement):
        if statement.info.get(StatementKey.Type.name) == DOP.Insert.name.upper() and statement.info.get(
                StatementKey.TableName.name) == StatementKey.WaitFill.name:
            for t in self._token.tokens:
                for token_class in [Identifier]:
                    if token_class.match(t):
                        token_class(t).accept(statement)
            return True

        return False

    def _create_procedure(self, statement):
        if statement.info.get(StatementKey.Type.name) == DOP.Create.name.upper() and statement.info.get(
                StatementKey.ProcedureName.name) == StatementKey.WaitFill.name:
            for t in self._token.tokens:
                for token_class in [Identifier]:
                    if token_class.match(t):
                        token_class(t).accept(statement)
            return True
        return False

    def _call_procedure(self, statement):
        if statement.info.get(StatementKey.Type.name) == DOP.Call.name.upper() and statement.info.get(
                StatementKey.ProcedureName.name) == StatementKey.WaitFill.name:
            for t in self._token.tokens:
                for token_class in [Identifier]:
                    if token_class.match(t):
                        token_class(t).accept(statement)
            return True
        return False
