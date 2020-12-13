from py2sql import Py2SQL, DbConfig

conn_info = DbConfig(
    username = 'temp_user',
    password = 'temp_password',
    dns = 'localhost:1521/orclpdb'
)

oracle_client_dir = 'E:\Downloads\instantclient-basiclite-windows.x64-19.9.0.0.0dbru\instantclient_19_9'

orm = Py2SQL(oracle_client_dir)
orm.db_connect(conn_info)
print(orm.db_engine())

import usage

usage.test2(orm)
usage.test3(orm)
usage.test4(orm)