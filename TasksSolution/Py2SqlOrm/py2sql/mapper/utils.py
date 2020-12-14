from ..sql import sql_types
from ..sql import sql_column

from json import dumps, loads, JSONEncoder, JSONDecoder
import pickle
import sys

import traceback 
class PythonObjectEncoder(JSONEncoder):
    """Custom python encoder to convert Python value to SQL value"""
    def default(self, obj):
        try:
            if isinstance(obj, (list, dict, str, int, float, bool, type(None))):
                return JSONEncoder.default(self, obj)
            elif isinstance(obj, (set, frozenset, tuple)):
                return list(obj)
            elif isinstance(obj, object):
                return vars(obj)
            else:
                return {'_python_object': pickle.dumps(obj)}
        except Exception as ex:
            traceback.print_exc() 
            sys.exit()

def as_python_object(dct):
    if '_python_object' in dct:
        return pickle.loads(str(dct['_python_object']))
    return dct

def map_value(sql_type, val):
    if sql_type.__class__ == sql_types.String:
        return f"'{val}'"
    elif sql_type.__class__ == sql_types.Json:
        text = dumps(val, cls=PythonObjectEncoder)
        return f"'{text}'"
    elif val is not None:
        return sql_type.python_type(val)

def get_table_name(cls):
    name = getattr(cls, '__table_name__', cls.__name__)
    return name.upper()

def get_columns(cls):
    fields = {}
    for k, v in cls.__dict__.items():
        if isinstance(v, sql_column.Column): fields.update({k.upper(): v})
    return fields