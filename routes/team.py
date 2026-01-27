from flask import Blueprint, render_template
from database import get_db_connection

team_bp = Blueprint('team', __name__, url_prefix='/team')

@team_bp.route('/')
def team_list():
    """Danh sách nhân viên"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM team_members 
        WHERE is_active = TRUE 
        ORDER BY display_order, experience_years DESC
    """)
    team_members = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('team_list.html', team_members=team_members)

@team_bp.route('/<int:member_id>')
def team_detail(member_id):
    """Chi tiết nhân viên"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM team_members WHERE id = %s AND is_active = TRUE
    """, (member_id,))
    member = cursor.fetchone()
    
    if not member:
        cursor.close()
        conn.close()
        return "Không tìm thấy nhân viên", 404
    
    # Parse certifications
    certifications = []
    if member['certifications']:
        certifications = [cert.strip() for cert in member['certifications'].split(',')]
    
    cursor.close()
    conn.close()
    
    return render_template('team_detail.html', member=member, certifications=certifications)

@team_bp.route('/reviews')
def reviews():
    """Trang đánh giá khách hàng"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Lấy đánh giá nổi bật
    cursor.execute("""
        SELECT * FROM customer_reviews 
        WHERE is_approved = TRUE AND is_featured = TRUE
        ORDER BY created_at DESC
        LIMIT 6
    """)
    featured_reviews = cursor.fetchall()
    
    # Lấy tất cả đánh giá
    cursor.execute("""
        SELECT * FROM customer_reviews 
        WHERE is_approved = TRUE
        ORDER BY created_at DESC
    """)
    all_reviews = cursor.fetchall()
    
    # Tính thống kê
    cursor.execute("""
        SELECT 
            COUNT(*) as total_reviews,
            AVG(rating) as avg_rating,
            SUM(CASE WHEN rating = 5 THEN 1 ELSE 0 END) as five_star,
            SUM(CASE WHEN rating = 4 THEN 1 ELSE 0 END) as four_star,
            SUM(CASE WHEN rating = 3 THEN 1 ELSE 0 END) as three_star
        FROM customer_reviews 
        WHERE is_approved = TRUE
    """)
    stats = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template('reviews.html', 
                         featured_reviews=featured_reviews,
                         all_reviews=all_reviews,
                         stats=stats)
