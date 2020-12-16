from ..sql.sql_types import String

from .utils import *

def _map_column(name, val):
    sql_type = val.sql_type
    
    stmt = [name]
    if issubclass(sql_type.__class__, String):
        stmt.append(f'{sql_type.__name__}({sql_type.length})')
    else:
        stmt.append(sql_type.__name__)
        
    if not val.nullable: stmt.append('NOT NULL')
    if val.default: stmt.append(f'DEFAULT {val.default}')

    return ' '.join(stmt)

def get_table_create_stmt(cls):
    """Returns SQL CREATE table statement for the given
    cls class using specified Column fields"""
    table_name = get_table_name(cls)
    exec_stmt = [
        f"CREATE TABLE {table_name} (\n    ",
        "HIDDEN_KEY_ID NUMBER GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1),\n    ",
        None, '\n)']

    to_insert = get_columns(cls)
    if not to_insert: return None

    col_sql = [_map_column(name, val) for name, val in to_insert.items()]
    exec_stmt[2] = ',\n    '.join(col_sql)

    return ''.join(exec_stmt)

def get_alter_table_stmt(cls, attributes):
    """Returns SQL ALTER table statement for the given
    cls class using specified Column fields"""
    new_dict = get_columns(cls)
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
    """Returns SQL DROP table statement for the given
    cls class using specified Column fields"""
    table_name = get_table_name(cls)
    exec_stmt = [f"DROP TABLE {table_name}"]
    return ''.join(exec_stmt)

def get_object_insert_stmt(obj):
    """Returns SQL INSERT INTO table statement for the given
    obj object using associated class"""
    table_columns = get_columns(obj.__class__)
    obj_columns = {x.upper() : y for x, y in vars(obj).items() if x.upper() in table_columns}

    if not obj_columns: return None
    exec_stmt = ""\
        "INSERT INTO {}\n"\
        "({})\n"\
        "VALUES ({})\n"\
        "returning HIDDEN_KEY_ID into :id".format(
            get_table_name(obj.__class__),
            ', '.join(obj_columns.keys()),
            ', '.join(str(map_value(table_columns[x].sql_type, y)) for x, y in obj_columns.items())
        )
    return exec_stmt

def get_object_update_stmt(obj):
    """Returns SQL UPDATE table statement for the given
    obj object using associated class"""
    table_columns = get_columns(obj.__class__)
    obj_columns = {x.upper() : y for x, y in vars(obj).items() if x.upper() in table_columns}

    if not obj_columns: return None

    exec_stmt = ""\
        "UPDATE {}\n"\
        "SET\n"\
        "    {}\n"\
        "WHERE HIDDEN_KEY_ID = {}".format(
            get_table_name(obj.__class__),
            ',\n    '.join('{}={}'.format(
                x, str(map_value(table_columns[x].sql_type, y))) for x, y in obj_columns.items()),
            getattr(obj, '__HIDDEN_KEY_ID')
        )
    return exec_stmt

def get_object_delete_stmt(obj):
    """Returns SQL DELETE FROM table statement for the given
    obj object using associated class"""
    table_columns = get_columns(obj.__class__)

    exec_stmt = ""\
        "DELETE FROM {}\n"\
        "WHERE HIDDEN_KEY_ID = {}".format(
            get_table_name(obj.__class__),
            getattr(obj, '__HIDDEN_KEY_ID')
    )
    return exec_stmt