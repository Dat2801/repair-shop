from flask import Flask
from routes.home import home_bp
from routes.contact import contact_bp
from routes.admin import admin_bp
from routes.auth import auth_bp
from routes.shop import shop_bp
from datetime import timedelta
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.permanent_session_lifetime = timedelta(days=7)  # Session tồn tại 7 ngày

# Đăng ký blueprints
app.register_blueprint(home_bp)
app.register_blueprint(contact_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(shop_bp)

if __name__ == "__main__":
    app.run(debug=True)

