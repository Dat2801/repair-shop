from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import pymysql
from app.utils.database import get_db_connection
import bcrypt
from datetime import datetime, timedelta
import secrets
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pyotp
import qrcode
import io
import base64
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import requests
import json

auth_bp = Blueprint('auth', __name__)

# Import config
try:
    from app.config import GOOGLE_CLIENT_ID, EMAIL_CONFIG, OTP_EXPIRY_MINUTES, OTP_LENGTH
    print(f"DEBUG: GOOGLE_CLIENT_ID loaded: {GOOGLE_CLIENT_ID[:20] if GOOGLE_CLIENT_ID else 'None'}...")
except ImportError as e:
    print(f"ERROR: Failed to import config: {e}")
    GOOGLE_CLIENT_ID = None
    EMAIL_CONFIG = None
    OTP_EXPIRY_MINUTES = 10
    OTP_LENGTH = 6

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_session_token():
    """Generate secure session token"""
    return secrets.token_urlsafe(32)

def generate_otp():
    """Generate random OTP code"""
    return ''.join(random.choices(string.digits, k=OTP_LENGTH))

def send_email_otp(email, otp_code):
    """Send OTP code via email"""
    if not EMAIL_CONFIG:
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = email
        msg['Subject'] = 'Mã xác thực OTP - Motor Việt-Nhật'
        
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #dc143c;">🔐 Mã xác thực OTP</h2>
                    <p>Xin chào,</p>
                    <p>Mã xác thực OTP của bạn là:</p>
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                        <h1 style="color: #dc143c; font-size: 36px; letter-spacing: 8px; margin: 0;">{otp_code}</h1>
                    </div>
                    <p>Mã này có hiệu lực trong {OTP_EXPIRY_MINUTES} phút.</p>
                    <p style="color: #666; font-size: 14px; margin-top: 30px;">
                        Nếu bạn không yêu cầu mã này, vui lòng bỏ qua email này.
                    </p>
                    <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;">
                    <p style="color: #999; font-size: 12px; text-align: center;">
                        Motor Việt-Nhật - Dịch vụ sửa chữa xe máy uy tín
                    </p>
                </div>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def verify_google_token(token):
    """Verify Google OAuth token"""
    try:
        if not GOOGLE_CLIENT_ID:
            print("ERROR: GOOGLE_CLIENT_ID not configured")
            return None
        
        idinfo = id_token.verify_oauth2_token(
            token, 
            google_requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            print(f"ERROR: Invalid issuer: {idinfo['iss']}")
            return None
            
        return {
            'email': idinfo.get('email'),
            'name': idinfo.get('name'),
            'picture': idinfo.get('picture'),
            'email_verified': idinfo.get('email_verified', False)
        }
    except Exception as e:
        print(f"ERROR verifying Google token: {str(e)}")
        return None
    except Exception as e:
        print(f"Error verifying Google token: {e}")
        return None

def is_logged_in():
    """Check if user is logged in"""
    return 'user_id' in session and 'username' in session

def get_current_user():
    """Get current logged in user info"""
    if not is_logged_in():
        return None
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, username, email, full_name, phone, address, role, is_active, created_at, last_login FROM users WHERE id = %s", 
                      (session['user_id'],))
        user = cursor.fetchone()
        return user
    finally:
        cursor.close()
        conn.close()

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Đăng ký tài khoản mới"""
    if is_logged_in():
        return redirect(url_for('home.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        
        # Validate input
        if not all([username, email, password, confirm_password, full_name]):
            flash('Vui lòng điền đầy đủ thông tin!', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Mật khẩu xác nhận không khớp!', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Mật khẩu phải có ít nhất 6 ký tự!', 'error')
            return render_template('register.html')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Check if username or email exists
            cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", 
                          (username, email))
            if cursor.fetchone():
                flash('Tên đăng nhập hoặc email đã tồn tại!', 'error')
                return render_template('register.html')
            
            # Hash password and insert user
            password_hash = hash_password(password)
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, full_name, phone, role)
                VALUES (%s, %s, %s, %s, %s, 'customer')
            """, (username, email, password_hash, full_name, phone))
            
            conn.commit()
            flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
            return redirect(url_for('auth.login'))
            
        except pymysql.Error as e:
            conn.rollback()
            flash(f'Lỗi đăng ký: {str(e)}', 'error')
            return render_template('register.html')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Đăng nhập"""
    if is_logged_in():
        return redirect(url_for('home.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Vui lòng nhập tên đăng nhập và mật khẩu!', 'error')
            return render_template('login.html')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Get user by username or email
            cursor.execute("""
                SELECT id, username, password_hash, full_name, email, role, is_active, email_verified, two_factor_enabled
                FROM users 
                WHERE username = %s OR email = %s
            """, (username, username))
            
            user = cursor.fetchone()
            
            if not user:
                flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'error')
                return render_template('login.html')
            
            if not user['is_active']:
                flash('Tài khoản đã bị khóa!', 'error')
                return render_template('login.html')
            
            # Verify password
            if not verify_password(password, user['password_hash']):
                flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'error')
                return render_template('login.html')
            
            # Check if 2FA is enabled
            if user.get('two_factor_enabled'):
                # Store temp session data
                session['temp_user_id'] = user['id']
                session['temp_username'] = user['username']
                session['temp_full_name'] = user['full_name']
                session['temp_role'] = user['role']
                return redirect(url_for('auth.verify_2fa'))
            
            # Check if email is verified
            if not user.get('email_verified'):
                # Generate and send OTP
                otp_code = generate_otp()
                expiry = datetime.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
                
                cursor.execute("""
                    INSERT INTO otp_codes (user_id, code, expiry, purpose)
                    VALUES (%s, %s, %s, 'email_verification')
                    ON DUPLICATE KEY UPDATE code = %s, expiry = %s, created_at = NOW()
                """, (user['id'], otp_code, expiry, otp_code, expiry))
                conn.commit()
                
                if send_email_otp(user['email'], otp_code):
                    session['verify_email_user_id'] = user['id']
                    session['verify_email'] = user['email']
                    flash('Vui lòng xác thực email của bạn. Mã OTP đã được gửi!', 'warning')
                    return redirect(url_for('auth.verify_email'))
            
            # Update last login
            cursor.execute("UPDATE users SET last_login = NOW() WHERE id = %s", (user['id'],))
            conn.commit()
            
            # Set session
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['role'] = user['role']
            session.permanent = True
            
            flash(f'Chào mừng {user["full_name"]}!', 'success')
            return redirect(url_for('home.index'))
            
        except pymysql.Error as e:
            flash(f'Lỗi đăng nhập: {str(e)}', 'error')
            return render_template('login.html', google_client_id=GOOGLE_CLIENT_ID)
        finally:
            cursor.close()
            conn.close()
    
    return render_template('login.html', google_client_id=GOOGLE_CLIENT_ID)

@auth_bp.route('/login/google', methods=['POST'])
def google_login():
    """Đăng nhập bằng Google OAuth"""
    token = request.json.get('credential')
    
    if not token:
        return jsonify({'success': False, 'message': 'Không có token'}), 400
    
    user_info = verify_google_token(token)
    
    if not user_info:
        return jsonify({'success': False, 'message': 'Token không hợp lệ'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if user exists
        cursor.execute("SELECT id, username, full_name, role, is_active FROM users WHERE email = %s", 
                      (user_info['email'],))
        user = cursor.fetchone()
        
        if user:
            # User exists, login
            if not user['is_active']:
                return jsonify({'success': False, 'message': 'Tài khoản đã bị khóa'}), 403
            
            # Update email_verified
            cursor.execute("UPDATE users SET email_verified = TRUE, last_login = NOW() WHERE id = %s", 
                          (user['id'],))
            conn.commit()
            
        else:
            # Create new user
            username = user_info['email'].split('@')[0] + '_' + secrets.token_hex(4)
            cursor.execute("""
                INSERT INTO users (username, email, full_name, email_verified, oauth_provider, oauth_id, role)
                VALUES (%s, %s, %s, TRUE, 'google', %s, 'customer')
            """, (username, user_info['email'], user_info['name'], user_info['email']))
            conn.commit()
            user_id = cursor.lastrowid
            
            user = {
                'id': user_id,
                'username': username,
                'full_name': user_info['name'],
                'role': 'customer'
            }
        
        # Set session
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['full_name'] = user['full_name']
        session['role'] = user['role']
        session.permanent = True
        
        return jsonify({
            'success': True, 
            'message': f'Chào mừng {user["full_name"]}!',
            'redirect': url_for('home.index')
        })
        
    except pymysql.Error as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

@auth_bp.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    """Xác thực email bằng OTP"""
    if 'verify_email_user_id' not in session:
        flash('Phiên xác thực đã hết hạn!', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        otp_input = request.form.get('otp', '').strip()
        
        if not otp_input:
            flash('Vui lòng nhập mã OTP!', 'error')
            return render_template('verify_email.html', email=session.get('verify_email'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT code, expiry FROM otp_codes 
                WHERE user_id = %s AND purpose = 'email_verification' AND used = FALSE
                ORDER BY created_at DESC LIMIT 1
            """, (session['verify_email_user_id'],))
            
            otp_record = cursor.fetchone()
            
            if not otp_record:
                flash('Mã OTP không tồn tại hoặc đã được sử dụng!', 'error')
                return render_template('verify_email.html', email=session.get('verify_email'))
            
            if datetime.now() > otp_record['expiry']:
                flash('Mã OTP đã hết hạn!', 'error')
                return render_template('verify_email.html', email=session.get('verify_email'))
            
            if otp_input != otp_record['code']:
                flash('Mã OTP không đúng!', 'error')
                return render_template('verify_email.html', email=session.get('verify_email'))
            
            # Mark OTP as used and verify email
            cursor.execute("""
                UPDATE otp_codes SET used = TRUE WHERE user_id = %s AND purpose = 'email_verification'
            """, (session['verify_email_user_id'],))
            
            cursor.execute("""
                UPDATE users SET email_verified = TRUE WHERE id = %s
            """, (session['verify_email_user_id'],))
            
            # Get user info
            cursor.execute("""
                SELECT id, username, full_name, role FROM users WHERE id = %s
            """, (session['verify_email_user_id'],))
            user = cursor.fetchone()
            
            conn.commit()
            
            # Clear temp session
            session.pop('verify_email_user_id', None)
            session.pop('verify_email', None)
            
            # Set full session
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['role'] = user['role']
            session.permanent = True
            
            flash('✅ Email đã được xác thực thành công!', 'success')
            return redirect(url_for('home.index'))
            
        except pymysql.Error as e:
            conn.rollback()
            flash(f'Lỗi: {str(e)}', 'error')
            return render_template('verify_email.html', email=session.get('verify_email'))
        finally:
            cursor.close()
            conn.close()
    
    return render_template('verify_email.html', email=session.get('verify_email'))

@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    """Gửi lại mã OTP"""
    if 'verify_email_user_id' not in session:
        return jsonify({'success': False, 'message': 'Phiên xác thực đã hết hạn'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT email FROM users WHERE id = %s", (session['verify_email_user_id'],))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': 'Người dùng không tồn tại'}), 404
        
        # Generate new OTP
        otp_code = generate_otp()
        expiry = datetime.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
        
        cursor.execute("""
            INSERT INTO otp_codes (user_id, code, expiry, purpose)
            VALUES (%s, %s, %s, 'email_verification')
            ON DUPLICATE KEY UPDATE code = %s, expiry = %s, created_at = NOW(), used = FALSE
        """, (session['verify_email_user_id'], otp_code, expiry, otp_code, expiry))
        conn.commit()
        
        if send_email_otp(user['email'], otp_code):
            return jsonify({'success': True, 'message': 'Mã OTP mới đã được gửi!'})
        else:
            return jsonify({'success': False, 'message': 'Không thể gửi email'}), 500
            
    except pymysql.Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@auth_bp.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    """Xác thực 2FA"""
    if 'temp_user_id' not in session:
        flash('Phiên đăng nhập đã hết hạn!', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        otp_input = request.form.get('otp', '').strip()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT two_factor_secret FROM users WHERE id = %s
            """, (session['temp_user_id'],))
            user = cursor.fetchone()
            
            if not user or not user['two_factor_secret']:
                flash('Lỗi xác thực 2FA!', 'error')
                return render_template('verify_2fa.html')
            
            # Verify TOTP
            totp = pyotp.TOTP(user['two_factor_secret'])
            if totp.verify(otp_input, valid_window=1):
                # Login successful
                session['user_id'] = session.pop('temp_user_id')
                session['username'] = session.pop('temp_username')
                session['full_name'] = session.pop('temp_full_name')
                session['role'] = session.pop('temp_role')
                session.permanent = True
                
                cursor.execute("UPDATE users SET last_login = NOW() WHERE id = %s", (session['user_id'],))
                conn.commit()
                
                flash(f'Chào mừng {session["full_name"]}!', 'success')
                return redirect(url_for('home.index'))
            else:
                flash('Mã xác thực không đúng!', 'error')
                return render_template('verify_2fa.html')
                
        finally:
            cursor.close()
            conn.close()
    
    return render_template('verify_2fa.html')

@auth_bp.route('/logout')
def logout():
    """Đăng xuất"""
    username = session.get('full_name', 'User')
    session.clear()
    flash(f'Đã đăng xuất. Hẹn gặp lại!', 'success')
    return redirect(url_for('home.index'))

@auth_bp.route('/profile')
def profile():
    """Trang thông tin cá nhân"""
    if not is_logged_in():
        flash('Vui lòng đăng nhập để xem thông tin cá nhân!', 'error')
        return redirect(url_for('auth.login'))
    
    user = get_current_user()
    
    # Get booking history
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT * FROM bookings 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        """, (session['user_id'],))
        bookings = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    
    return render_template('profile.html', user=user, bookings=bookings)

@auth_bp.route('/booking-history')
def booking_history():
    """Trang lịch sử đặt lịch"""
    if not is_logged_in():
        flash('Vui lòng đăng nhập để xem lịch sử đặt lịch!', 'error')
        return redirect(url_for('auth.login'))
    
    user = get_current_user()
    
    # Get all booking history
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT * FROM bookings 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        """, (session['user_id'],))
        bookings = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    
    return render_template('booking_history.html', user=user, bookings=bookings)

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    """Chỉnh sửa thông tin cá nhân"""
    if not is_logged_in():
        flash('Vui lòng đăng nhập!', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        
        # Validation
        if not full_name or len(full_name) < 3:
            flash('Họ tên phải có ít nhất 3 ký tự!', 'error')
            user = get_current_user()
            return render_template('edit_profile.html', user=user)
        
        if not phone or len(phone) < 10 or len(phone) > 11 or not phone.isdigit():
            flash('Số điện thoại không hợp lệ (10-11 chữ số)!', 'error')
            user = get_current_user()
            return render_template('edit_profile.html', user=user)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE users 
                SET full_name = %s, phone = %s, address = %s, updated_at = NOW()
                WHERE id = %s
            """, (full_name, phone, address, session['user_id']))
            
            conn.commit()
            session['full_name'] = full_name
            flash('✅ Cập nhật thông tin thành công!', 'success')
            return redirect(url_for('auth.profile'))
            
        except pymysql.Error as e:
            conn.rollback()
            flash(f'❌ Lỗi cập nhật: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    user = get_current_user()
    return render_template('edit_profile.html', user=user)
