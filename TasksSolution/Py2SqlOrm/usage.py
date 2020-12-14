from py2sql import Column, sql_types

def test2(orm):
    class Student:
        __table_name__ = "another_table"

        id = Column(int)
        name = Column(str, default='sdfd')
        age = Column(int, nullable=False)
        interests = Column(sql_types.Json())

    print(orm.db_engine())
    orm.save_class(Student)
    print(orm.db_tables())
    print(orm.db_table_structure(Student))

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


def test3(orm):
    import random

    class ComplexGuy:
        def __init__(self):
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


def test4(orm):
    class Student:
        __table_name__ = "student"

        id = Column(int)
        name = Column(str, default='sdfd')
        age = Column(int, nullable=False)
        interests = Column(sql_types.Json())

        def __init__(self, name, age, interests):
            self.name = name
            self.age = age
            self.interests = interests

    orm.save_class(Student)
    print(orm.db_table_structure(Student))

    s1 = Student('Peter', 234, (1e4, 'sd', 0))
    s2 = Student('Eureka', -43, {'fd':'3223', 'sdd':43})

    print(orm.db_table_size(Student))
    orm.save_object(s1)
    orm.save_object(s2)
    s1.name = 'Changed'
    orm.save_object(s1)
    print(orm.db_table_size(Student))
    orm.delete_object(s1)
    orm.delete_object(s1)
    orm.delete_object(s2)
    print(orm.db_table_size(Student))

def test5(orm):
    class Student:
        __table_name__ = "student_extended"

        name = Column(sql_types.String())
        age = Column(sql_types.Number(32), nullable=False)
        interests = Column(sql_types.Json())

        def __init__(self, name, age, interests):
            self.name = name
            self.age = age
            self.interests = interests


    orm.delete_class(Student)
    orm.save_class(Student)
    print(orm.db_tables())
    print(orm.db_table_size(Student))
    for i in range(1):
        s = Student(f'Student{i}', i, [i, i+1, i+2])
        orm.save_object(s)

    print(orm.db_table_size(Student))