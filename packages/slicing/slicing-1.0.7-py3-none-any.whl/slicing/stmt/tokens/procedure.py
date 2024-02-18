from slicing.constant import StatementKey, DOO


class Procedure:
    def __init__(self, token):
        self._token = token

    @classmethod
    def match(cls, token):
        return str(token.ttype) == "Token.Keyword" and token.value.upper() == DOO.Procedure.name.upper()

    def accept(self, statement):
        statement.info[StatementKey.ProcedureName.name] = StatementKey.WaitFill.name