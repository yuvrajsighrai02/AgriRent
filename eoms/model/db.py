import mysql.connector
from eoms import connect
from mysql.connector import Error
from contextlib import contextmanager

dbconn = None
connection = None


def get_cursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(
        user=connect.dbuser,
        password=connect.dbpass,
        host=connect.dbhost,
        port=connect.dbport,
        database=connect.dbname,
        auth_plugin='mysql_native_password'
    )
    connection.autocommit = True   # ✅ Auto commit enabled
    dbconn = connection.cursor(dictionary=True)
    return dbconn


@contextmanager
def get_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            user=connect.dbuser,
            password=connect.dbpass,
            host=connect.dbhost,
            port=connect.dbport,
            database=connect.dbname,
            auth_plugin='mysql_native_password'
        )
        connection.autocommit = True   # ✅ Auto commit enabled
        yield connection
    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if connection is not None and connection.is_connected():
            connection.close()
