from . import sql_types
import json

allowed_python_types = {
    str, int, float,
    list, tuple, frozenset, set, dict,
    object
}

def _map_value(sql_type, val):
    if sql_type.__class__ == sql_types.String:
        return f"'{val}'"
    elif sql_type.__class__ == sql_types.Json:
        text = json.dumps(val)
        return f"'text'"
    elif val:
        return sql_type.python_type(val)

class Column():
    def __init__(self, data_type, nullable=True, default=None, auto_increment=False, primary_key=False):
        self.nullable = nullable
        self.auto_increment = auto_increment
        self.primary_key = True if auto_increment else primary_key

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

        self.default = _map_value(self.sql_type, default)

def get_sql_from_python(type):
    if type == str:
        return sql_types.String()
    elif type == int:
        return sql_types.Number()
    elif type == float:
        return sql_types.Number(real=True)
    else:
        return sql_types.Json()