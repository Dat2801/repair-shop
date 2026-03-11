from flask import Blueprint, render_template, jsonify
from app.utils.database import get_db_connection

admin_bp = Blueprint('admin', __name__)

@admin_bp.route("/api/contacts/count")
def contact_count():
    """API để lấy số lượng liên hệ"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as count FROM contacts")
        result = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({"count": result['count'] if result else 0})
    except:
        return jsonify({"count": 0})

@admin_bp.route("/api/contacts/recent")
def recent_contacts():
    """API để lấy các liên hệ gần đây"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM contacts ORDER BY created_at DESC LIMIT 10")
        contacts = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({"contacts": contacts})
    except Exception as e:
        return jsonify({"error": str(e), "contacts": []})
