import sqlparse.sql

from slicing.constant import StatementKey


class Identifier:
    def __init__(self, token):
        self._token = token

    @classmethod
    def match(cls, token):
        return token.ttype is None and type(token) == sqlparse.sql.Identifier

    def accept(self, statement):
        for key, value in statement.info.items():
            if value == StatementKey.WaitFill.name:
                statement.info[key] = self._token.value

        # if statement.info.get("TableName") == Constant.WaitFill.name:
        #     statement.info["TableName"] = self._token.value
        # if statement.info.get("ViewName") == Constant.WaitFill.name:
        #     statement.info["ViewName"] = self._token.value
        # if statement.info.get("ProcedureName") == Constant.WaitFill.name:
        #     statement.info["ProcedureName"] = self._token.value
