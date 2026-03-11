from flask import Blueprint, request, redirect, flash, url_for, session
from app.utils.database import get_db_connection

contact_bp = Blueprint('contact', __name__)

@contact_bp.route("/contact", methods=["POST"])
def contact():
    """Xử lý form đặt lịch sửa xe"""
    try:
        # Lấy dữ liệu từ form
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        bike_brand = request.form.get("bike_brand", "").strip()
        service = request.form.get("service", "").strip()
        pickup_address = request.form.get("pickup_address", "").strip()
        pickup_date = request.form.get("pickup_date", "").strip()
        condition = request.form.get("condition", "").strip()
        
        # Validation
        if not all([name, phone, bike_brand, service, pickup_address, pickup_date]):
            flash('❌ Vui lòng điền đầy đủ thông tin bắt buộc!', 'error')
            return redirect(url_for('home.index') + '#contact')
        
        # Lấy user_id nếu đã đăng nhập
        user_id = session.get('user_id', None)
        
        # Lưu vào database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO bookings 
            (user_id, name, phone, bike_brand, service, pickup_address, pickup_date, condition_description, status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending')
        """, (user_id, name, phone, bike_brand, service, pickup_address, pickup_date, condition))
        
        conn.commit()
        cur.close()
        conn.close()
        
        # Thông báo thành công
        flash(f'✅ Cảm ơn {name}! Chúng tôi đã nhận yêu cầu sửa {bike_brand} và sẽ liên hệ qua số {phone} trong 15 phút.', 'success')
        return redirect(url_for('home.index'))
        
    except Exception as e:
        print(f"Error in contact route: {str(e)}")  # Log lỗi
        flash(f'❌ Có lỗi xảy ra: {str(e)}. Vui lòng thử lại!', 'error')
        return redirect(url_for('home.index') + '#contact')
