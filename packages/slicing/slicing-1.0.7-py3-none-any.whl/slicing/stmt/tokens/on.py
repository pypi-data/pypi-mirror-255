from slicing.constant import StatementKey, DOP


class On:
    def __init__(self, token):
        self._token = token

    @classmethod
    def match(cls, token):
        return str(token.ttype) == "Token.Keyword" and token.value.upper() == StatementKey.On.name.upper()

    def accept(self, statement):
        if statement.info[StatementKey.Type.name] == DOP.Create.name.upper() and statement.info[StatementKey.IndexName.name] is not None:
            statement.info[StatementKey.TableName.name] = StatementKey.WaitFill.name
