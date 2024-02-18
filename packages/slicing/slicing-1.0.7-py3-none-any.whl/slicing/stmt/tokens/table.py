from slicing.constant import StatementKey, DOO


class Table:
    def __init__(self, token):
        self._token = token

    @classmethod
    def match(cls, token):
        return str(token.ttype) == "Token.Keyword" and token.value.upper() == DOO.Table.name.upper()

    def accept(self, statement):
        statement.info[StatementKey.TableName.name] = StatementKey.WaitFill.name
