from slicing.constant import StatementKey, DOP


class Insert:
    def __init__(self, token):
        self._token = token

    @classmethod
    def match(cls, token):
        return str(token.ttype) == "Token.Keyword.DML" and token.value.upper() == DOP.Insert.name.upper()

    def accept(self, statement):
        statement.info[StatementKey.Type.name] = self._token.value.upper()
        statement.info[StatementKey.TableName.name] = StatementKey.WaitFill.name
