from flask import Blueprint, render_template, session
from app.utils.database import get_db_connection

home_bp = Blueprint('home', __name__)

@home_bp.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM services")
    services = cur.fetchall()
    
    # Lấy số lượng sản phẩm trong giỏ hàng
    cart_count = 0
    if session.get('user_id'):
        cur.execute("SELECT SUM(quantity) as total FROM cart WHERE user_id = %s", (session['user_id'],))
        result = cur.fetchone()
        cart_count = result['total'] if result and result['total'] else 0
    
    cur.close()
    conn.close()
    return render_template("index.html", services=services, cart_count=cart_count)
