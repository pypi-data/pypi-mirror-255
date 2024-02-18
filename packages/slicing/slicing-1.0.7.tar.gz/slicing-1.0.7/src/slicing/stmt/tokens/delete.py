from slicing.constant import StatementKey, DOP


class Delete:
    def __init__(self, token):
        self._token = token

    @classmethod
    def match(cls, token):
        return str(token.ttype) == "Token.Keyword.DML" and token.value.upper() == DOP.Delete.name.upper()

    def accept(self, statement):
        statement.info[StatementKey.Type.name] = DOP.Delete.name.upper()
