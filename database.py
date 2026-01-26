import pymysql
from config import MYSQL_CONFIG

def get_db_connection():
    return pymysql.connect(
        host=MYSQL_CONFIG["host"],
        user=MYSQL_CONFIG["user"],
        password=MYSQL_CONFIG["password"],
        database=MYSQL_CONFIG["db"],
        cursorclass=pymysql.cursors.DictCursor
    )
