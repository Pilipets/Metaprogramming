import os
import cx_Oracle
import logging

from .mapper import mapping, get_table_name

logging.basicConfig(level=logging.DEBUG)
class DbConfig:
    def __init__(self, username, password, dns):
        self.username = username
        self.password = password
        self.dns = dns

class OrmException(Exception):
    pass

class Py2SQL:
    def __init__(self, lib_dir : str = None):
        if not lib_dir:
            lib_dir = os.getenv('ORACLE_CLIENT', None)

        if lib_dir is None:
            raise OrmException("Unable to find Oracle client libraries")

        cx_Oracle.init_oracle_client(lib_dir=lib_dir)
        logging.log(logging.DEBUG, "Using client version: {}".format(cx_Oracle.clientversion()))

        self.__conn = None
        self.__dns = ''

    def db_connect(self, config : DbConfig):
        # dns: user/password@dsn
        self.__conn = cx_Oracle.connect(
            config.username, config.password,
            config.dns, encoding='UTF-8')

        logging.log(logging.DEBUG, f"Connected successfully to {config.dns}")

        self.__conn.autocommit = False
        self.__dns = config.dns
    
    def db_disconnect(self):
        self.__conn.close()
        logging.log(logging.DEBUG, f"Disconnected from {self.__dns}")

    def db_engine(self):
        with self.__conn.cursor() as cursor:
            cursor.execute("SELECT banner FROM v$version WHERE ROWNUM = 1")
            return cursor.fetchone()[0]

    def db_name(self):
        return self.__dns

    def db_tables(self):
        with self.__conn.cursor() as cursor:
            cursor.execute("SELECT table_name FROM user_tables")

            table_names = [x[0] for x in cursor.fetchall()]
            return table_names

    def db_table_size(self, cls):
        with self.__conn.cursor() as cursor:
            cursor.execute('''
                select round(bytes/1024/1024,3)|| 'MB'
                from user_segments
                where segment_name=:tb''',
                tb=get_table_name(cls))

            row = cursor.fetchone()
            return row[0] if row else None


    def db_table_structure(self, cls):
        attributes = []
        with self.__conn.cursor() as cursor:
            cursor.execute('''
                select column_id, column_name, data_type
                from user_tab_columns
                where table_name = :tb
                order by column_id''', [get_table_name(cls)])

            for row in cursor:
                attributes.append(row)

        return attributes

    def __table_exists(self, cls):
        with self.__conn.cursor() as cursor:
            cursor.execute('''
                select count(*)
                from user_tables
                where table_name = :tb''', [get_table_name(cls)])
            return cursor.fetchone()[0] > 0

    def save_class(self, cls):
        if self.__table_exists(cls): return False

        sql_stmt = mapping.get_table_create_stmt(cls)
        try:
            with self.__conn.cursor() as cursor:
                cursor.execute(sql_stmt)
        except Exception as ex:
            logging.log(logging.ERROR, ex)
            self.__conn.rollback()
            return False
        else:
            self.__conn.commit()
            return True