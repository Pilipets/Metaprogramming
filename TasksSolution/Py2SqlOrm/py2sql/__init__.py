"""
This package serves as top level for Python to SQL object relationship mapping.
Among the most used objects are Py2SQL, DbConfig, and Column, sql_types.
1. Py2SQL and DbConfig are used to instantiate ORM and connect it with the database.
2. Column, sql_types are used to specify fields that are mapped to the database, and
the type used in the mapping - respectively.

One must instantiate Py2SQL with a path to oracle client libraries, or set
ORACLE_CLIENT environment variable.
Then use database config to initialize the connection before using ORM,
example:
conn_info = DbConfig(
    username = 'temp_user',
    password = 'temp_password',
    dns = 'localhost:1521/orclpdb'
)

oracle_client_dir = 'instantclient-basiclite-windows.x64-19.9.0.0.0dbru\instantclient_19_9'

orm = Py2SQL(oracle_client_dir)
orm.db_connect(conn_info)

To save specified object in the database the user must define what fields are expected
to be mapped with Column(...) class variable.
Example:
    class Student:
        __table_name__ = "another_table"

        id = Column(int)
        name = Column(str, default='sdfd')
        age = Column(int, nullable=False)
        interests = Column(sql_types.Json())
"""

from .sql import sql_types
from .sql import Column

from .orm import Py2SQL, DbConfig