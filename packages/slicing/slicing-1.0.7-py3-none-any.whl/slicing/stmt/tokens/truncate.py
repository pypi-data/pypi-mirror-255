from slicing.constant import StatementKey, DOP


class Truncate:
    def __init__(self, token):
        self._token = token

    @classmethod
    def match(cls, token):
        return str(token.ttype) == "Token.Keyword" and token.value.upper() == DOP.Truncate.name.upper()

    def accept(self, statement):
        statement.info[StatementKey.Type.name] = self._token.value.upper()