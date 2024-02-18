from slicing.constant import StatementKey, DOO, DOP


class Index:
    def __init__(self, token):
        self._token = token

    @classmethod
    def match(cls, token):
        return str(token.ttype) == "Token.Keyword" and token.value.upper() == DOO.Index.name.upper()

    def accept(self, statement):
        if statement.info[StatementKey.Type.name] == DOP.Create.name.upper():
            statement.info[StatementKey.IndexName.name] = StatementKey.WaitFill.name
