<h2>Python->SQL object relationship mapper package</h2>

<h4>Description:</h4>
This package serves as top level for <b>Python to SQL object relationship mapping</b>.<br>
Among the most used objects are <i>Py2SQL, DbConfig, and Column, sql_types</i>.<br>
1. <i>Py2SQL</i> and <i>DbConfig</i> are used to instantiate ORM and connect it with the database;<br>
2. <i>Column</i>, <i>sql_types</i> are used to specify fields that are mapped to the database, and
the type used in the mapping - respectively;

<h4>Usage instructions:</h4>
<ol>
    <li>One must instantiate Py2SQL with a path to oracle client libraries, or set
        ORACLE_CLIENT environment variable.
        Then use database config to initialize the connection before using ORM,
        example:<br>
        <code>
        	from py2sql import Py2SQL, DbConfig<br>
        	conn_info = DbConfig(<br>
        	&ensp;&ensp;&ensp;&ensp;username = 'temp_user',<br>
        	&ensp;&ensp;&ensp;&ensp;password = 'temp_password',<br>
        	&ensp;&ensp;&ensp;&ensp;dns = 'localhost:1521/orclpdb'<br>
        	)<br>
        	<br>
        	oracle_client_dir = 'instantclient-basiclite-windows.x64-19.9.0.0.0dbru\instantclient_19_9'<br>
        	<br>
        	orm = Py2SQL(oracle_client_dir)<br>
        	orm.db_connect(conn_info)
        </code>
    </li>
    <li>
    	To save specified object in the database the user must define what fields are expected to be mapped with <i>Column(...)</i> class variable.<br>
		Example:<br>
        <code>
        	class Student:<br>
        	&ensp;&ensp;&ensp;&ensp;__table_name__ = "another_table"<br>
			<br>
        	&ensp;&ensp;&ensp;&ensp;id = Column(int)<br>
        	&ensp;&ensp;&ensp;&ensp;name = Column(str, default='Paul')<br>
        	&ensp;&ensp;&ensp;&ensp;age = Column(int, nullable=False)<br>
        	&ensp;&ensp;&ensp;&ensp;interests = Column(sql_types.Json())
        </code>
	</li>
    <li>Orm supports basic mapping methods like save_object, save_table, delete_table, delete_class as well as other db related methods specified in py2sql 					documentation;
    </li>
</ol>