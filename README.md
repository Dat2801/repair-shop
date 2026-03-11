# 🔧 Motor Việt-Nhật (Repair Shop Management)

Hệ thống quản lý cửa hàng sửa chữa xe máy - Việt-Nhật với xác thực nâng cao (Google OAuth, 2FA, Email Verification)

## 📋 Tính Năng Chính

- ✅ **Xác Thực An Toàn**
  - Google OAuth 2.0
  - Email Verification (OTP)
  - Two-Factor Authentication (2FA) với TOTP
  - Mã hóa bcrypt cho passwords

- 🛒 **Quản Lý Shop**
  - Danh sách sản phẩm & phụ tùng
  - Giỏ hàng và thanh toán
  - Lịch sử đơn hàng

- 📅 **Quản Lý Đặt Lịch**
  - Đặt lịch sửa chữa
  - Lịch sử booking
  - Trạng thái xử lý

- 👥 **Quản Lý Nhân Viên**
  - Danh sách nhân viên
  - Đánh giá & review

- 🛡️ **Admin Dashboard**
  - Quản lý sản phẩm
  - Quản lý người dùng
  - Quản lý đơn hàng

## 🚀 Cài Đặt & Chạy

### 1. Yêu Cầu
- Python 3.10+
- MySQL 8.0+
- Virtual Environment

### 2. Clone & Setup

```bash
cd /Users/dat_vh/websuaxe/repair-shop
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Cấu Hình Database

**Cách 1: Chạy script tự động (Khuyên dùng)**
```bash
cd database
python3 setup.py
```

**Cách 2: Chạy SQL files thủ công**
```bash
cd database
mysql -u root -p < 01_setup_database.sql
mysql -u root -p < 02_shop_database.sql
# ... chạy từ 03 đến 08
```

### 4. Cấu Hình Ứng Dụng

Tạo file `.env` từ `.env.example`:
```bash
cp .env.example .env
```

Chỉnh sửa `.env` với:
- Google OAuth credentials
- Gmail SMTP settings
- MySQL credentials

### 5. Chạy Ứng Dụng

```bash
python3 app.py
```

Mở browser: http://127.0.0.1:5000

## 📁 Cấu Trúc Dự Án

```
repair-shop/
├── app/                           # Flask app (factory pattern)
│   ├── __init__.py               # App factory
│   ├── routes/                   # 6 blueprints
│   │   ├── auth.py              # Authentication
│   │   ├── home.py              # Landing page
│   │   ├── shop.py              # Products & orders
│   │   ├── team.py              # Staff & reviews
│   │   ├── contact.py           # Contact form
│   │   └── admin.py             # Admin dashboard
│   ├── templates/               # HTML templates
│   ├── static/                  # CSS, JS, images
│   └── utils/                   # Utilities
│       ├── database.py          # DB connections
│       ├── decorators.py        # Auth decorators
│       └── constants.py         # App constants
│
├── database/                     # Database management
│   ├── setup.py                 # Auto-setup script
│   ├── setup.sh                 # Bash setup script
│   ├── README.md                # Database documentation
│   └── *.sql                    # 8 migration files
│
├── scripts/                      # Utility scripts
│   ├── setup_auth.py            # Setup authentication
│   ├── setup_shop_db.py         # Setup shop database
│   ├── create_bookings_table.py # Create bookings
│   ├── add_more_products.py     # Add test products
│   ├── update_*.py              # Update data scripts
│   ├── check_*.py               # Check/verify scripts
│   └── reset_admin_password.py  # Reset admin password
│
├── tests/                        # Test suite
│   └── test_booking.py          # Booking tests
│
├── app.py                        # App entry point (factory pattern)
├── config.py                     # App configuration
├── config.example.py            # Config template
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── STRUCTURE.md                 # Project structure docs
├── README.md                    # This file
└── docs/                        # Documentation
    ├── STRUCTURE.md            # Architecture
    ├── AUTH_SETUP.md           # Auth configuration
    └── AUTH_ADVANCED_SETUP.md  # Advanced setup
```

## 🔧 Chạy Scripts Utility

### Database Setup
```bash
cd database
python3 setup.py
```

### Kiểm Tra Database
```bash
python3 scripts/check_database.py
```

### Kiểm Tra User
```bash
python3 scripts/check_user.py
```

### Reset Admin Password
```bash
python3 scripts/reset_admin_password.py
```

### Thêm Sản Phẩm Test
```bash
python3 scripts/add_more_products.py
```

### Cập Nhật Hình Ảnh Sản Phẩm
```bash
python3 scripts/update_product_images_manual.py
```

### Chạy Test Booking
```bash
python3 tests/test_booking.py
```

## 🔐 Bảo Mật & Xác Thực

### Google OAuth Setup
1. Vào [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo OAuth 2.0 credentials
3. Thêm Authorized redirect URIs:
   - `http://localhost:5000/auth/google/callback`
   - `http://your-domain.com/auth/google/callback`
4. Lưu Client ID & Secret vào `.env`

### Email Verification
- Sử dụng Gmail SMTP
- Tạo App Password cho Gmail account
- Lưu vào `.env`: `GMAIL_APP_PASSWORD`

### Two-Factor Authentication (2FA)
- Sử dụng TOTP (Time-based One-Time Password)
- Scan QR code bằng Google Authenticator/Authy
- 6 chữ số, cập nhật mỗi 30 giây

## 📚 Tài Liệu Thêm

- [Database Setup Guide](database/README.md)
- [Project Architecture](docs/STRUCTURE.md)
- [Authentication Setup](docs/AUTH_SETUP.md)
- [Advanced Authentication](docs/AUTH_ADVANCED_SETUP.md)

## 🐛 Troubleshooting

### Port 5000 đã sử dụng
```bash
lsof -ti :5000 | xargs kill -9
```

### MySQL Connection Error
```bash
python3 scripts/check_database.py
```

### Gmail SMTP Issues
- Bật 2-Step Verification trên Gmail
- Tạo App Password
- Kiểm tra `.env` có đúng credentials không

## 📝 License

MIT License

## 👤 Author

Motor Việt-Nhật Team

---

**Last Updated**: February 2, 2026
