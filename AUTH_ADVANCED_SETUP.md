# Hướng Dẫn Cấu Hình Xác Thực Nâng Cao

## 1. Cài Đặt Dependencies

```bash
pip install -r requirements.txt
```

## 2. Cập Nhật Database

Chạy script SQL để thêm các bảng và cột mới:

```bash
mysql -u root -p suaxemay < update_auth_features.sql
```

## 3. Cấu Hình Google OAuth

### Bước 1: Tạo Google Cloud Project

1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo project mới hoặc chọn project có sẵn
3. Vào **APIs & Services** > **Credentials**

### Bước 2: Tạo OAuth 2.0 Client ID

1. Click **Create Credentials** > **OAuth client ID**
2. Chọn Application type: **Web application**
3. Thêm Authorized JavaScript origins:
   - `http://localhost:5000`
   - `http://127.0.0.1:5000`
   - (Thêm domain production khi deploy)
4. Thêm Authorized redirect URIs:
   - `http://localhost:5000/login/google/callback`
5. Lưu lại **Client ID** và **Client Secret**

### Bước 3: Cập nhật config.py

```python
GOOGLE_CLIENT_ID = "your-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "your-client-secret"
```

## 4. Cấu Hình Email (Gmail)

### Bước 1: Tạo App Password

1. Truy cập [Google Account Security](https://myaccount.google.com/security)
2. Bật **2-Step Verification**
3. Vào **App passwords**
4. Tạo app password mới cho "Mail"
5. Copy password

### Bước 2: Cập nhật config.py

```python
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your-email@gmail.com",
    "sender_password": "your-16-digit-app-password"
}
```

## 5. Cấu Hình Facebook Login (Optional)

### Bước 1: Tạo Facebook App

1. Truy cập [Facebook Developers](https://developers.facebook.com/)
2. Tạo app mới
3. Thêm Facebook Login product
4. Cấu hình Valid OAuth Redirect URIs:
   - `http://localhost:5000/login/facebook/callback`

### Bước 2: Cập nhật config.py

```python
FACEBOOK_CLIENT_ID = "your-facebook-app-id"
FACEBOOK_CLIENT_SECRET = "your-facebook-app-secret"
```

## 6. Chạy Ứng Dụng

```bash
python app.py
```

## 7. Kiểm Tra Tính Năng

### Email Verification
1. Đăng ký tài khoản mới
2. Đăng nhập lần đầu
3. Hệ thống sẽ gửi OTP qua email
4. Nhập OTP để xác thực

### Google OAuth
1. Click nút "Đăng nhập với Google" 
2. Chọn tài khoản Google
3. Tự động đăng nhập hoặc tạo tài khoản mới

### 2FA (Two-Factor Authentication)
1. Vào Profile > Security Settings
2. Bật 2FA
3. Quét QR code bằng Google Authenticator/Authy
4. Lần đăng nhập sau sẽ yêu cầu mã 2FA

## 8. Lưu Ý Bảo Mật

- **KHÔNG** commit file `config.py` vào Git
- Sử dụng `.env` file cho production
- Thay đổi secret keys định kỳ
- Giới hạn số lần thử OTP/2FA
- Log các hoạt động đăng nhập

## 9. Troubleshooting

### Lỗi: "Token verification failed"
- Kiểm tra GOOGLE_CLIENT_ID đúng chưa
- Domain trong Google Console phải khớp với domain đang chạy

### Lỗi: "Cannot send email"
- Kiểm tra app password Gmail
- Bật "Less secure app access" (nếu cần)
- Kiểm tra firewall/antivirus

### Lỗi: "OTP expired"
- Mặc định OTP hết hạn sau 10 phút
- Điều chỉnh `OTP_EXPIRY_MINUTES` trong config.py

## 10. Production Deployment

Khi deploy lên production:

1. **Cập nhật domain trong Google Console**
2. **Sử dụng HTTPS** (bắt buộc cho OAuth)
3. **Sử dụng environment variables**:
   ```python
   import os
   GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
   EMAIL_CONFIG = {
       "sender_email": os.getenv('EMAIL_SENDER'),
       "sender_password": os.getenv('EMAIL_PASSWORD')
   }
   ```
4. **Cấu hình rate limiting** cho API endpoints
5. **Backup database** thường xuyên

## Liên Hệ Hỗ Trợ

Nếu gặp vấn đề, vui lòng liên hệ team phát triển.
