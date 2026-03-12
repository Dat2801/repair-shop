"""
Database utilities and connection management
"""

import pymysql
from app.config import MYSQL_CONFIG


def get_db_connection():
    """
    Create and return a database connection
    """
    try:
        connection = pymysql.connect(
            host=MYSQL_CONFIG['host'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password'],
            database=MYSQL_CONFIG['db'],
            charset=MYSQL_CONFIG['charset'],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )
        return connection
    except pymysql.Error as e:
        print(f"Database connection error: {e}")
        return None


def close_db_connection(connection):
    """Close database connection"""
    if connection:
        connection.close()
