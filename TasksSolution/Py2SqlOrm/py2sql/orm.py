import os
import cx_Oracle
import logging

logging.basicConfig(level=logging.DEBUG)
class DbConfig:
    def __init__(self, username, password, dns):
        self.username = username
        self.password = password
        self.dns = dns

class OrmException(Exception):
    pass

class Py2SQL:
    __dbms_name = 'Oracle Database'

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
        self.__dns = config.dns
    
    def db_disconnect(self):
        self.__conn.close()
        logging.log(logging.DEBUG, f"Disconnected from {self.__dns}")

    def db_engine(self):
        return self.__dbms_name, self.__conn.version

    def db_name(self):
        return self.__dns

    def db_tables(self):
        with self.__conn.cursor() as cursor:
            cursor.execute("SELECT table_name FROM user_tables")

            table_names = [x[0] for x in cursor.fetchall()]
            return table_names

    def db_table_size(self, table_name : str):
        with self.__conn.cursor() as cursor:
            cursor.execute('''
                select round(bytes/1024/1024,3)|| 'MB'
                from user_segments
                where segment_name=:tb''',
                tb=table_name)

            row = cursor.fetchone()
            return row[0] if row else None


    def db_table_structure(self, table_name : str):
        attributes = []
        with self.__conn.cursor() as cursor:
            cursor.execute('''
                select column_id, column_name, data_type
                from user_tab_columns
                where table_name = :tb
                order by column_id''', [table_name])

            for row in cursor:
                attributes.append(row)

        return attributes