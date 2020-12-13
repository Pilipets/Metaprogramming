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

        id = Column(int, primary_key=True, auto_increment=True)
        name = Column(str, default='sdfd')
        age = Column(int, nullable=False)
        interests = Column(sql_types.Json())

    print(orm.db_engine())
    orm.save_class(Student)
    print(orm.db_tables())
    print(orm.db_table_structure(Student))
    return
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


def test3():
    import random

    class ComplexGuy:
        def __init__(self, a, b, arr):
            self.a = {0: 'test', 'why':'so easy?'}
            self.b = 23.34e34
            self.c = random.sample(range(-500000, 500000), 15)

    class ComplexType:
        __table_name__ = "simple_type"
    
        interests = Column(set)
        other = Column(object)
        parts = Column(sql_types.Json())

        def __init__(self):
            self.interests = {2,3,4,5,6}
            self.other = ComplexGuy()
            self.parts = [int(23), 'sdsd', 'sdfsdf']

    orm.save_class(ComplexType)
    print(orm.db_table_structure(ComplexType))
    print(orm.db_tables())

    obj = ComplexType()
    orm.save_object(obj)