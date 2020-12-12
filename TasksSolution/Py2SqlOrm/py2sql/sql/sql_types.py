class SqlType:
    def __init__(self):
        self.python_type = None


class Number(SqlType):
    __name__ = 'NUMBER'

    def __init__(self, length=0, real=False):
        self.python_type = int
        self.length = length

        if real:
            self.python_type = float
            self.__name__ = 'FLOAT'

class String(SqlType):
    __name__ = 'VARCHAR2'

    def __init__(self, length=255):
        self.python_type = str
        self.length = length


class Json(String):

    def __init__(self):
        super().__init__(4000)