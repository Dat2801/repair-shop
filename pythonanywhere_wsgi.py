"""
PythonAnywhere WSGI Configuration File

HOW TO USE:
1. Tạo tài khoản tại https://www.pythonanywhere.com
2. Vào Dashboard → Web → Add new web app → Manual configuration → Python 3.10
3. Trong tab "Code" → WSGI configuration file → click vào đường dẫn → paste nội dung file này
4. Chỉnh PROJECT_PATH cho đúng username của bạn
"""

import sys
import os

# ── Đường dẫn đến thư mục project ──────────────────────────────────────────
# Thay "your_username" bằng username PythonAnywhere của bạn
PROJECT_PATH = '/home/your_username/repair-shop'

if PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)

# ── Load biến môi trường từ .env ────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_PATH, '.env'))

# ── Tạo Flask app ────────────────────────────────────────────────────────────
from factory import create_app
application = create_app()
