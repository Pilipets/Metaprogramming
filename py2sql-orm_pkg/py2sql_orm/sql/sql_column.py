import json

from . import sql_types
from ..mapper import map_value

allowed_python_types = {
    str, int, float,
    list, tuple, frozenset, set, dict,
    object
}

class Column():
    """The class that represents sql table column"""
    def __init__(self, data_type, nullable=True, default=None):
        self.nullable = nullable

        if isinstance(data_type, sql_types.SqlType):
            self.sql_type = data_type
        elif data_type in allowed_python_types:
            self.sql_type = get_sql_from_python(data_type)
        else:
            raise ValueError(
                "Expected SqlType or Python type from ({}), got {}".format(
                    ', '.join(x.__name__ for x in allowed_python_types),
                    data_type.__name__
                )
            )

        if default:
            self.default = map_value(self.sql_type, default)
        else:
            self.default = None

def get_sql_from_python(type):
    """Returns sql type associated with the provided python type"""
    if type == str:
        return sql_types.String()
    elif type == int:
        return sql_types.Number()
    elif type == float:
        return sql_types.Number(real=True)
    else:
        return sql_types.Json()