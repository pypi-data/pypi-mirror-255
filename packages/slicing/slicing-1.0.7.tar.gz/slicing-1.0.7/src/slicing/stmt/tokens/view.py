from slicing.constant import StatementKey, DOO


class View:
    def __init__(self, token):
        self._token = token

    @classmethod
    def match(cls, token):
        return str(token.ttype) == "Token.Keyword" and token.value.upper() == DOO.View.name.upper()

    def accept(self, statement):
        statement.info[StatementKey.ViewName.name] = StatementKey.WaitFill.name
