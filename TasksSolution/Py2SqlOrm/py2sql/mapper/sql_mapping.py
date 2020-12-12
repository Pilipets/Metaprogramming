from ..sql import Column
from ..sql.sql_types import String

def get_table_name(cls):
    name = getattr(cls, '__table__name__', cls.__name__)
    return name.upper()

def _get_columns(cls):
    fields = {}
    for k, v in cls.__dict__.items():
        if isinstance(v, Column): fields.update({k.upper(): v})
    return fields

def _map_column(name, val):
    sql_type = val.sql_type
    
    stmt = [name]
    if issubclass(sql_type.__class__, String):
        stmt.append(f'{sql_type.__name__}({sql_type.length})')
    else:
        stmt.append(sql_type.__name__)

    return ' '.join(stmt)

def get_table_create_stmt(cls):
    table_name = get_table_name(cls)
    exec_stmt = [f"CREATE TABLE {table_name} (\n    ", None, '\n)']

    to_insert = _get_columns(cls)
    if not to_insert: return None

    col_sql = [_map_column(name, val) for name, val in to_insert.items()]
    exec_stmt[1] = ',\n    '.join(col_sql)

    return ''.join(exec_stmt)

def get_alter_table_stmt(cls, attributes):
    new_dict = _get_columns(cls)
    cur_dict = {x[1] : x[2] for x in attributes}

    create_dict = lambda arr, mapper: {k:mapper[k] for k in arr}
    new_cols, cur_cols = set(new_dict), set(cur_dict)

    # Get columns to insert, delete columns
    # TODO: Add handling type change here with modify columns
    sym_diff = new_cols ^ cur_cols
    to_insert = create_dict(new_cols & sym_diff, new_dict)
    to_delete = cur_cols & sym_diff

    if not to_insert and not to_delete: return ''

    table_name = get_table_name(cls)
    exec_stmts = []

    if to_insert:
        stmt = [f"ALTER TABLE {table_name}\nADD(", None, ")"]

        col_sql = [_map_column(name, val) for name, val in to_insert.items()]
        stmt[1] = ', '.join(col_sql)

        exec_stmts.append(''.join(stmt))

    if to_delete:
        stmt = [f"ALTER TABLE {table_name}\nDROP (", None, ")"]

        stmt[1] =', '.join(to_delete)
        exec_stmts.append(''.join(stmt))

    return exec_stmts

def get_table_delete_stmt(cls):
    table_name = get_table_name(cls)
    exec_stmt = [f"DROP TABLE {table_name}"]
    return ''.join(exec_stmt)