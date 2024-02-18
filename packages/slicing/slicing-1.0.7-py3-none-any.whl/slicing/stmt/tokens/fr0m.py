from slicing.constant import StatementKey


class From:
    def __init__(self, token):
        self._token = token

    @classmethod
    def match(cls, token):
        return str(token.ttype) == "Token.Keyword" and token.value.upper() == StatementKey.From.name.upper()

    def accept(self, statement):
        statement.info[StatementKey.TableName.name] = StatementKey.WaitFill.name
