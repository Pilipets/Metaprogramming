class SqlType:
    """Basic class of the sql entity type"""
    def __init__(self):
        self.python_type = None


class Number(SqlType):
    """SQL number type including NUMBER, FLOAT, ..."""
    __name__ = 'NUMBER'

    def __init__(self, length=0, real=False):
        self.python_type = int
        self.length = length

        if real:
            self.python_type = float
            self.__name__ = 'FLOAT'

class String(SqlType):
    """SQL variable length ascii string type"""
    __name__ = 'VARCHAR2'

    def __init__(self, length=255):
        self.python_type = str
        self.length = length


class Json(String):
    """SQL text type aka String(4000)"""
    def __init__(self):
        super().__init__(4000)