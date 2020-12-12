from ..sql import Column
from ..sql.sql_types import String

CREATE = 'CREATE TABLE'
DROP = 'DROP TABLE'
INSERT = 'INSERT INTO'
DELETE = 'DELETE FROM'

def get_table_name(cls):
    name = getattr(cls, '__table__name__', cls.__name__)
    return name.upper()

def _get_columns(cls):
    fields = {}
    for k, v in cls.__dict__.items():
        if isinstance(v, Column): fields.update({k: v})
    return fields

def get_table_create_stmt(cls):
    def _map_column(name, val):
        sql_type = val.sql_type

        stmt = [name]
        if issubclass(sql_type.__class__, String):
            stmt.append(f'{sql_type.__name__}({sql_type.length})')
        else:
            stmt.append(sql_type.__name__)

        return ' '.join(stmt)

    table_name = getattr(cls, '__table_name__', cls.__name__)
    exec_stmt = [f"{CREATE} {table_name} (\n    "]

    table_columns = _get_columns(cls)
    col_sql = []
    for name, val in table_columns.items():
        col_sql.append(_map_column(name, val))

    exec_stmt.append(',\n    '.join(col_sql))
    exec_stmt.append('\n)')

    return ''.join(exec_stmt)