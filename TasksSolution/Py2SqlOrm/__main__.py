from py2sql import Py2SQL, DbConfig, Column, sql_types

def test1(orm):
    print(orm.db_name())
    print(orm.db_engine())

    print(orm.db_tables()[:3])
    print(orm.db_table_size('LOGMNR_PDB_INFO$'))

    print(orm.db_table_structure('LOGMNR_PDB_INFO$'))


conn_info = DbConfig(
    username = 'temp_user',
    password = 'temp_password',
    dns = 'localhost:1521/orclpdb'
)

oracle_client_dir = 'E:\Downloads\instantclient-basiclite-windows.x64-19.9.0.0.0dbru\instantclient_19_9'

orm = Py2SQL(oracle_client_dir)
orm.db_connect(conn_info)

class Student:
    __table_name__ = "student"

    id = Column(int)
    name = Column(str)
    age = Column(int)
    interests = Column(sql_types.Json())

#print(orm.db_engine())
orm.save_class(Student)
#print(orm.db_tables())
del Student.id
Student.weird = Column(sql_types.Number(real=True))

print(orm.db_table_structure(Student))
orm.save_class(Student)
print(orm.db_table_structure(Student))
print(orm.delete_class(Student))