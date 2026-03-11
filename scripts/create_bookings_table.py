import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymysql
from config import MYSQL_CONFIG

def create_bookings_table():
    """Tạo bảng bookings để lưu thông tin đặt lịch sửa xe"""
    conn = pymysql.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Drop bảng cũ nếu có
        cursor.execute("DROP TABLE IF EXISTS bookings")
        print("🗑️ Đã xóa bảng bookings cũ (nếu có)")
        
        # Tạo bảng bookings
        create_sql = """
            CREATE TABLE bookings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NULL,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(20) NOT NULL,
                bike_brand VARCHAR(50) NOT NULL,
                service VARCHAR(50) NOT NULL,
                pickup_address TEXT NOT NULL,
                pickup_date DATE NOT NULL,
                condition_description TEXT,
                status ENUM('pending', 'confirmed', 'in_progress', 'completed', 'cancelled') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_status (status),
                INDEX idx_created_at (created_at),
                INDEX idx_user_id (user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        cursor.execute(create_sql)
        
        conn.commit()
        print("✅ Đã tạo bảng bookings thành công!")
        
        # Kiểm tra cấu trúc bảng
        cursor.execute("DESCRIBE bookings")
        columns = cursor.fetchall()
        print("\n📋 Cấu trúc bảng bookings:")
        for col in columns:
            print(f"   {col[0]} - {col[1]}")
            
    except pymysql.Error as e:
        print(f"❌ Lỗi: {str(e)}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_bookings_table()
