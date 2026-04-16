"""
Database utilities and connection management
"""

import os
import psycopg2
import psycopg2.extras


def get_db_connection():
    """
    Create and return a PostgreSQL database connection.
    Uses DATABASE_URL environment variable (provided by Render).
    """
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise Exception("DATABASE_URL environment variable is not set")

        connection = psycopg2.connect(
            database_url,
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        connection.autocommit = False
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")
        return None


def close_db_connection(connection):
    """Close database connection"""
    if connection:
        connection.close()
