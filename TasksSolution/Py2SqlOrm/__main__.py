from py2sql import Py2SQL, DbConfig, Column, sql_types

conn_info = DbConfig(
    username = 'temp_user',
    password = 'temp_password',
    dns = 'localhost:1521/orclpdb'
)

oracle_client_dir = 'E:\Downloads\instantclient-basiclite-windows.x64-19.9.0.0.0dbru\instantclient_19_9'

orm = Py2SQL(oracle_client_dir)
orm.db_connect(conn_info)