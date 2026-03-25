"""
Database utilities and connection management
"""

import pymysql
from config import MYSQL_CONFIG


def get_db_connection():
    """
    Create and return a database connection.
    Supports Cloud SQL Unix socket when MYSQL_HOST starts with /cloudsql/.
    """
    try:
        host = MYSQL_CONFIG['host']
        common = dict(
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password'],
            database=MYSQL_CONFIG['db'],
            charset=MYSQL_CONFIG['charset'],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )

        if host.startswith('/cloudsql/'):
            connection = pymysql.connect(unix_socket=host, **common)
        else:
            connection = pymysql.connect(host=host, port=MYSQL_CONFIG.get('port', 3306), **common)

        return connection
    except pymysql.Error as e:
        print(f"Database connection error: {e}")
        return None


def close_db_connection(connection):
    """Close database connection"""
    if connection:
        connection.close()
