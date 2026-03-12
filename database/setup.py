#!/usr/bin/env python3
"""
Database Setup Script
Automatically runs all SQL files in correct order
"""

import os
import sys
import pymysql
from pathlib import Path
import getpass

# SQL files in execution order
SQL_FILES = [
    "01_setup_database.sql",
    "02_shop_database.sql",
    "03_auth_database.sql",
    "04_parts_categories.sql",
    "05_setup_team.sql",
    "06_update_booking_table.sql",
    "07_update_images.sql",
    "08_update_auth_features.sql"
]

def get_credentials():
    """Get database credentials from user"""
    print("\n" + "="*50)
    print("🗄️  Motor Việt-Nhật Database Setup")
    print("="*50)
    print()
    
    host = input("MySQL host [localhost]: ").strip() or "localhost"
    user = input("MySQL user [root]: ").strip() or "root"
    password = getpass.getpass("MySQL password: ")
    
    return host, user, password

def execute_sql_file(connection, filename, db_name=None):
    """Execute a SQL file"""
    file_path = Path(__file__).parent / filename
    
    if not file_path.exists():
        print(f"⚠️  File not found: {filename}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        cursor = connection.cursor()
        
        # Split by ; and execute each statement
        statements = [s.strip() for s in sql_content.split(';') if s.strip()]
        
        for statement in statements:
            if statement:
                cursor.execute(statement)
        
        connection.commit()
        cursor.close()
        
        print(f"✅ {filename} completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error running {filename}: {str(e)}")
        return False

def main():
    """Main setup function"""
    try:
        # Get credentials
        host, user, password = get_credentials()
        
        # First, create initial connection to create database
        print("\n▶️  Connecting to MySQL...")
        
        try:
            conn = pymysql.connect(
                host=host,
                user=user,
                password=password,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            print("✅ Connected successfully\n")
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            sys.exit(1)
        
        # Execute SQL files
        print("Starting database setup...\n")
        
        for i, filename in enumerate(SQL_FILES, 1):
            print(f"[{i}/{len(SQL_FILES)}] ▶️  Running: {filename}")
            
            if not execute_sql_file(conn, filename, "suaxemay" if i > 1 else None):
                print(f"\n❌ Setup failed at: {filename}")
                conn.close()
                sys.exit(1)
            print()
        
        conn.close()
        
        # Success message
        print("="*50)
        print("✅ Database setup completed successfully!")
        print("="*50)
        print("\nNext steps:")
        print("1. Update config.py with your database credentials")
        print("2. Run: python3 run.py")
        print("3. Access: http://127.0.0.1:5000")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
