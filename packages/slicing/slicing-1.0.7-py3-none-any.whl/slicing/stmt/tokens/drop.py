from slicing.constant import StatementKey, DOP


class Drop:
    def __init__(self, token):
        self._token = token

    @classmethod
    def match(cls, token):
        return str(token.ttype) == "Token.Keyword.DDL" and token.value.upper() == DOP.Drop.name.upper()

    def accept(self, statement):
        statement.info[StatementKey.Type.name] = self._token.value.upper()
