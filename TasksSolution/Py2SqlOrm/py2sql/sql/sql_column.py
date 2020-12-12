from . import sql_types

allowed_python_types = {
    str, int, float,
    list, tuple, frozenset, set, dict
}

class Column():
    def __init__(self, data_type):
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


def get_sql_from_python(type):
    if type == str:
        return sql_types.String()
    elif type == int:
        return sql_types.Number()
    elif type == float:
        return sql_types.Number(real=True)
    else:
        return sql_types.Json()