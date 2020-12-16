import os
import cx_Oracle
import logging

from .mapper import mapping
from .mapper import get_table_name

logging.basicConfig(level=logging.DEBUG)
class DbConfig:
    """Configuration class that is used in Py2SQL to establish
    connection using the provided config"""
    def __init__(self, username, password, dns):
        self.username = username
        self.password = password
        self.dns = dns # dns: user/password@dsn

class OrmException(Exception):
    pass

class Py2SQL:
    """The class that represents object relationship mapping from Python
    into SQL and Oracle DBMS"""
    def __init__(self, lib_dir : str = None):
        """Initializes cx_Oracle with the provided connection libraries
        path by lib_dir or 'ORACLE_CLIENT' environment variables"""
        if not lib_dir:
            lib_dir = os.getenv('ORACLE_CLIENT', None)

        if lib_dir is None:
            raise OrmException("Unable to find Oracle client libraries")

        cx_Oracle.init_oracle_client(lib_dir=lib_dir)
        logging.log(logging.DEBUG, "Using client version: {}".format(cx_Oracle.clientversion()))

        self.__conn = None
        self.__dns = ''

    def db_size(self):
        """Returns size(in MB) of Oracle Database"""
        with self.__conn.cursor() as cursor:
            cursor.execute("SELECT sum(bytes)/1024/1024 size_in_mb FROM dba_data_files")
            return row.fetchone()[0]

    def db_connect(self, config : DbConfig):
        """Initializes and saves connection to database using config"""
        self.__conn = cx_Oracle.connect(
            config.username, config.password,
            config.dns, encoding='UTF-8')

        logging.log(logging.DEBUG, f"Connected successfully to {config.dns}")

        self.__conn.autocommit = False
        self.__dns = config.dns
    
    def db_disconnect(self):
        """Disconnects from the connected database"""
        self.__conn.close()
        logging.log(logging.DEBUG, f"Disconnected from {self.__dns}")

    def db_engine(self):
        """Returns name, version of used DBMS"""
        with self.__conn.cursor() as cursor:
            cursor.execute("SELECT banner FROM v$version WHERE ROWNUM = 1")
            return cursor.fetchone()[0]

    def db_name(self):
        """Returns name of the connected database"""
        return self.__dns

    def db_tables(self):
        """Returns list of names of existing tables in the database"""
        with self.__conn.cursor() as cursor:
            cursor.execute("SELECT table_name FROM user_tables")

            table_names = [x[0] for x in cursor.fetchall()]
            return table_names

    def db_table_size(self, cls):
        """Returns size of the table represented by cls class.
        If not empty and exists - size in MB.
        Otherwise - 0."""
        with self.__conn.cursor() as cursor:
            cursor.execute(
                "select round(bytes/1024/1024,3)|| 'MB'\n"\
                "from user_segments\n"\
                "where segment_name=:tb",
                tb=get_table_name(cls))

            row = cursor.fetchone()
            return row[0] if row else 0


    def db_table_structure(self, cls):
        """Returns ordered table columns with their types"""
        attributes = []
        with self.__conn.cursor() as cursor:
            cursor.execute(
                "select column_id, column_name, data_type\n"\
                "from user_tab_columns\n"
                "where table_name = :tb and column_name != 'HIDDEN_KEY_ID'\n"\
                "order by column_id",
                [get_table_name(cls)]
            )

            for row in cursor:
                attributes.append((row[0]-1, row[1], row[2]))

        return attributes

    def __table_exists(self, cls):
        """Checks if a table already exists in the database:
        Returns true if so, false - otherwise"""
        with self.__conn.cursor() as cursor:
            cursor.execute(
                "select count(*)\n"\
                "from user_tables\n"\
                "where table_name = :tb",
                [get_table_name(cls)]
            )
            return cursor.fetchone()[0] > 0

    def __commit_or_rollback(self, sql_stmt):
        """Executes SQL statements specified by sql_stmt:
        Makes commit in the end or rollback if an error happened.
        Returns error status"""
        if type(sql_stmt) != list: sql_stmt = [sql_stmt]
        try:
            with self.__conn.cursor() as cursor:
                for x in sql_stmt:
                    cursor.execute(x)
        except Exception as ex:
            logging.log(logging.ERROR, ex)
            self.__conn.rollback()
            return False
        else:
            self.__conn.commit()
            return True


    def save_class(self, cls):
        """Saves or updates(if present) table in the database, represented by cls"""
        attributes = self.db_table_structure(cls)
        if attributes:
            sql_stmts = mapping.get_alter_table_stmt(cls, attributes)
            if not sql_stmts: return
            self.__commit_or_rollback(sql_stmts)

        else:
            sql_stmt = mapping.get_table_create_stmt(cls)
            if not sql_stmt: return
            self.__commit_or_rollback(sql_stmt)

    def delete_class(self, cls):
        """Deletes(if present) table in the database, represented by cls"""
        if not self.__table_exists(cls): return

        sql_stmt = mapping.get_table_delete_stmt(cls)
        self.__commit_or_rollback(sql_stmt)

    def __get_all_subclasses(self, cls):
        """Collects recursively all unique subclasses of cls class"""
        return set(cls.__subclasses__()).union(
            [s for c in cls.__subclasses__() for s in self.__get_all_subclasses(c)])

    def save_hierarchy(self, root_cls):
        """Save class hierarchy in the connected database - invokes
        save_class method on root class and all its unique subclasses."""
        for cls in self.__get_all_subclasses(root_cls):
            self.save_class(cls)
        self.save_class(root_cls)

    def delete_hierarchy(self, root_cls):
        """Delete class hierarchy in the connected database - invokes
        delete_class method on root class and all its unique subclasses."""
        for cls in self.__get_all_subclasses(root_cls):
            self.delete_class(cls)
        self.delete_class(root_cls)

    def save_object(self, obj):
        """Save or updates object representation of obj in database"""
        if getattr(obj, '__HIDDEN_KEY_ID', None):
            sql_stmt = mapping.get_object_update_stmt(obj)
            if sql_stmt: self.__commit_or_rollback(sql_stmt)
            return

        sql_stmt = mapping.get_object_insert_stmt(obj)
        if not sql_stmt: return

        try:
            with self.__conn.cursor() as cursor:
                id = cursor.var(cx_Oracle.NUMBER)
                cursor.execute(sql_stmt, id=id)
        except Exception as ex:
            logging.log(logging.ERROR, ex)
            print(sql_stmt)
            self.__conn.rollback()
        else:
            setattr(obj, '__HIDDEN_KEY_ID', int(id.getvalue()[0]))
            self.__conn.commit()

    def delete_object(self, obj):
        """Delete if present object representation of obj in database"""
        if not getattr(obj, '__HIDDEN_KEY_ID', None): return

        sql_stmt = mapping.get_object_delete_stmt(obj)
        if self.__commit_or_rollback(sql_stmt): delattr(obj, '__HIDDEN_KEY_ID')