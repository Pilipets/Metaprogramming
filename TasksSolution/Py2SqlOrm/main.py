from py2sql import Py2SQL, DbConfig

conn_info = DbConfig(
    username = 'SYSTEM',
    password = 'admin',
    dns = 'localhost:1521/orcl'
)

oracle_client_dir = 'E:\Downloads\instantclient-basiclite-windows.x64-19.9.0.0.0dbru\instantclient_19_9'

orm = Py2SQL(oracle_client_dir)
orm.db_connect(conn_info)

#print(orm.db_name())
#print(orm.db_engine())

print(orm.db_tables()[:3])

print(orm.db_table_size('LOGMNR_PDB_INFO$'))

print(orm.db_table_structure('LOGMNR_PDB_INFO$'))