# Deploy Repair Shop lên PythonAnywhere (Hoàn Toàn Miễn Phí)

## Tại Sao PythonAnywhere?

- **$0 hoàn toàn** — không cần thẻ tín dụng
- Hỗ trợ Flask + MySQL native
- Không cold start
- URL miễn phí: `your_username.pythonanywhere.com`

**Giới hạn free tier:**
- 512MB storage, CPU hạn chế
- 1 web app
- Domain `.pythonanywhere.com` (không custom domain)
- Đủ dùng cho demo/portfolio

---

## Bước 1: Tạo Tài Khoản

1. Truy cập **https://www.pythonanywhere.com**
2. Nhấn **"Start running Python online in less than a minute!"**
3. Chọn **"Create a Beginner account"** (miễn phí)
4. Điền username, email, password → **Register**

---

## Bước 2: Mở Bash Console

Trong dashboard → **"New console"** → **"Bash**

---

## Bước 3: Upload Code

### Cách 1: Clone từ GitHub (khuyến nghị)
```bash
git clone https://github.com/YOUR_USERNAME/repair-shop.git
cd repair-shop
```

### Cách 2: Upload file ZIP
1. Nén thư mục `repair-shop` thành `repair-shop.zip`
2. Dashboard → **Files** → **Upload a file** → chọn file zip
3. Trong Bash console:
```bash
unzip repair-shop.zip
cd repair-shop
```

---

## Bước 4: Cài Đặt Dependencies

```bash
cd ~/repair-shop
pip3.10 install --user -r requirements.txt
```

---

## Bước 5: Tạo MySQL Database

1. Dashboard → **Databases** tab
2. Đặt **MySQL password** → nhấn **Initialize MySQL**
3. Trong mục **"Create a database"**, nhập tên: `repair_shop_db` → **Create**
4. Ghi lại thông tin:
   - **Host:** `YOUR_USERNAME.mysql.pythonanywhere-services.com`
   - **Username:** `YOUR_USERNAME`
   - **Password:** (password vừa đặt)
   - **Database name:** `YOUR_USERNAME$repair_shop_db`

> **Lưu ý quan trọng:** PythonAnywhere đặt tên database theo format `USERNAME$DBNAME`

---

## Bước 6: Import Database Schema

Trong Bash console:
```bash
cd ~/repair-shop

# Import từng file SQL (thay YOUR_USERNAME và YOUR_PASSWORD)
mysql -u YOUR_USERNAME -p -h YOUR_USERNAME.mysql.pythonanywhere-services.com 'YOUR_USERNAME$repair_shop_db' < database/01_setup_database.sql
mysql -u YOUR_USERNAME -p -h YOUR_USERNAME.mysql.pythonanywhere-services.com 'YOUR_USERNAME$repair_shop_db' < database/02_shop_database.sql
mysql -u YOUR_USERNAME -p -h YOUR_USERNAME.mysql.pythonanywhere-services.com 'YOUR_USERNAME$repair_shop_db' < database/03_auth_database.sql
mysql -u YOUR_USERNAME -p -h YOUR_USERNAME.mysql.pythonanywhere-services.com 'YOUR_USERNAME$repair_shop_db' < database/04_parts_categories.sql
mysql -u YOUR_USERNAME -p -h YOUR_USERNAME.mysql.pythonanywhere-services.com 'YOUR_USERNAME$repair_shop_db' < database/05_setup_team.sql
mysql -u YOUR_USERNAME -p -h YOUR_USERNAME.mysql.pythonanywhere-services.com 'YOUR_USERNAME$repair_shop_db' < database/06_update_booking_table.sql
mysql -u YOUR_USERNAME -p -h YOUR_USERNAME.mysql.pythonanywhere-services.com 'YOUR_USERNAME$repair_shop_db' < database/07_update_images.sql
mysql -u YOUR_USERNAME -p -h YOUR_USERNAME.mysql.pythonanywhere-services.com 'YOUR_USERNAME$repair_shop_db' < database/08_update_auth_features.sql
```

---

## Bước 7: Tạo File .env

Trong Bash console:
```bash
cat > ~/repair-shop/.env << 'EOF'
# Database - PythonAnywhere MySQL
MYSQL_HOST=YOUR_USERNAME.mysql.pythonanywhere-services.com
MYSQL_USER=YOUR_USERNAME
MYSQL_PASSWORD=YOUR_MYSQL_PASSWORD
MYSQL_DB=YOUR_USERNAME$repair_shop_db
MYSQL_PORT=3306
MYSQL_CHARSET=utf8mb4

# Flask
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this

# Email
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Facebook OAuth
FACEBOOK_CLIENT_ID=your-facebook-app-id
FACEBOOK_CLIENT_SECRET=your-facebook-app-secret
EOF
```

---

## Bước 8: Tạo Web App

1. Dashboard → **Web** tab → **"Add a new web app"**
2. Chọn domain: `your_username.pythonanywhere.com` → **Next**
3. Chọn **"Manual configuration"** → **Next**
4. Chọn **Python 3.10** → **Next**

---

## Bước 9: Cấu Hình WSGI

1. Trong tab **Web** → mục **"Code"** → nhấn vào đường dẫn WSGI file
   (ví dụ: `/var/www/your_username_pythonanywhere_com_wsgi.py`)
2. **Xóa toàn bộ nội dung** file đó
3. **Paste nội dung** từ file `pythonanywhere_wsgi.py` trong project
4. Thay `your_username` bằng username thực của bạn
5. **Save**

---

## Bước 10: Cấu Hình Virtual Environment (Tùy Chọn)

Nếu muốn dùng virtualenv thay vì `--user`:
```bash
mkvirtualenv --python=/usr/bin/python3.10 repair-shop-env
cd ~/repair-shop
pip install -r requirements.txt
```

Trong tab **Web** → mục **"Virtualenv"** → nhập:
```
/home/YOUR_USERNAME/.virtualenvs/repair-shop-env
```

---

## Bước 11: Cấu Hình Static Files

Trong tab **Web** → mục **"Static files"**:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/YOUR_USERNAME/repair-shop/app/static/` |

---

## Bước 12: Reload & Kiểm Tra

1. Nhấn nút **"Reload"** màu xanh lá to ở đầu trang Web tab
2. Truy cập `https://YOUR_USERNAME.pythonanywhere.com`

---

## Cập Nhật Code

```bash
# Trong Bash console PythonAnywhere
cd ~/repair-shop
git pull origin main
```

Sau đó nhấn **"Reload"** trong tab Web.

---

## Xử Lý Lỗi Thường Gặp

### Xem error logs
Tab **Web** → mục **"Log files"** → nhấn **error log**

### ModuleNotFoundError
```bash
pip3.10 install --user -r requirements.txt
```
Rồi Reload lại.

### Database connection error
- Kiểm tra `MYSQL_DB` có dạng `USERNAME$repair_shop_db` chưa
- Kiểm tra host đúng format `USERNAME.mysql.pythonanywhere-services.com`

### Static files không load
- Kiểm tra đường dẫn trong mục Static files của tab Web
