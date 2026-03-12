"""
Flask Application Factory
Initializes and configures the Flask app
"""

from flask import Flask
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def create_app(config=None):
    """
    Application Factory
    Creates and configures the Flask app
    """
    app = Flask(__name__, 
                template_folder='app/templates',
                static_folder='app/static')
    
    # Set secret key for session management
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Set default config
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600
    
    # Register blueprints
    from app.routes.home import home_bp
    from app.routes.auth import auth_bp
    from app.routes.shop import shop_bp
    from app.routes.team import team_bp
    from app.routes.contact import contact_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(team_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(admin_bp)
    
    return app
