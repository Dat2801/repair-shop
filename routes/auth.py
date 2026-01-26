from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import pymysql
from database import get_db_connection
import bcrypt
from datetime import datetime, timedelta
import secrets

auth_bp = Blueprint('auth', __name__)

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_session_token():
    """Generate secure session token"""
    return secrets.token_urlsafe(32)

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
                SELECT id, username, password_hash, full_name, role, is_active 
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
            
            # Redirect to home page
            return redirect(url_for('home.index'))
            
        except pymysql.Error as e:
            flash(f'Lỗi đăng nhập: {str(e)}', 'error')
            return render_template('login.html')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('login.html')

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
