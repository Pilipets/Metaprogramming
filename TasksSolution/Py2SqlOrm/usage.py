from py2sql import Py2SQL, DbConfig, Column, sql_types
def test1(orm):
    print(orm.db_name())
    print(orm.db_engine())

    print(orm.db_tables()[:3])
    print(orm.db_table_size('LOGMNR_PDB_INFO$'))

    print(orm.db_table_structure('LOGMNR_PDB_INFO$'))

def test2(orm):
    class Student:
        __table_name__ = "student"

        id = Column(int)
        name = Column(str)
        age = Column(int)
        interests = Column(sql_types.Json())

    print(orm.db_engine())
    orm.save_class(Student)
    print(orm.db_tables())
    del Student.id
    Student.weird = Column(sql_types.Number(real=True))

    print(orm.db_table_structure(Student))
    orm.save_class(Student)
    print(orm.db_table_structure(Student))
    print(orm.delete_class(Student))

    class Other(Student):
        pass

    class Good(Student):
        pass

    class Again(Other, Good):
        pass

    orm.save_hierarchy(Student)
    print(orm.db_tables())
    orm.delete_hierarchy(Student)
    print(orm.db_tables())

