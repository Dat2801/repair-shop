# Cấu Trúc Dự Án Repair Shop

## 📁 Tổ Chức Thư Mục

```
repair-shop/
├── app/                          # Main Flask application
│   ├── __init__.py              # App factory
│   ├── models/                  # Database models (future use with ORM)
│   ├── routes/                  # Blueprint routes
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication routes
│   │   ├── home.py             # Home page routes
│   │   ├── shop.py             # Shop/products routes
│   │   ├── team.py             # Team page routes
│   │   ├── contact.py          # Contact form routes
│   │   └── admin.py            # Admin dashboard routes
│   ├── utils/                   # Helper functions & utilities
│   │   ├── __init__.py
│   │   ├── database.py         # DB connection management
│   │   ├── decorators.py       # @login_required, @admin_only
│   │   ├── constants.py        # App-wide constants
│   │   └── validators.py       # Input validation (future)
│   ├── templates/              # HTML templates
│   │   ├── base.html           # Base template
│   │   ├── auth/               # Authentication templates
│   │   ├── shop/               # Shop templates
│   │   ├── admin/              # Admin templates
│   │   └── ...
│   └── static/                 # Static assets
│       ├── css/
│       ├── js/
│       └── images/
│
├── database/                    # Database files
│   ├── schema.sql              # Main database schema
│   ├── migrations/             # Migration scripts
│   └── seeds/                  # Sample data
│
├── tests/                       # Unit & integration tests
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_shop.py
│   └── test_api.py
│
├── docs/                        # Documentation
│   ├── API.md
│   ├── SETUP.md
│   └── DEPLOYMENT.md
│
├── app.py                       # Entry point (creates app)
├── config.py                    # Configuration (DO NOT commit)
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

## 🔧 Quy ước Mã Hóa

### Blueprints
- Mỗi module (auth, shop, team, etc) là một blueprint riêng
- Tất cả blueprints đăng ký trong `app/__init__.py`

### Utils
- `decorators.py`: Chứa `@login_required`, `@admin_required`
- `constants.py`: Chứa các hằng số dùng chung
- `database.py`: Quản lý kết nối database

### Templates
- Tổ chức theo feature (auth/, shop/, admin/)
- `base.html` là template chung cho tất cả pages

## 📝 Ví Dụ Sử Dụng

### Import Database Connection
```python
from app.utils.database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()
```

### Sử Dụng Decorators
```python
from app.utils.decorators import login_required, admin_required

@auth_bp.route('/profile')
@login_required
def profile():
    # Only logged-in users can access
    pass
```

### Truy Cập Constants
```python
from app.utils.constants import CATEGORIES, OTP_LENGTH

for cat_id, cat_name in CATEGORIES.items():
    print(f"{cat_id}: {cat_name}")
```

## 🚀 Chạy Ứng Dụng

```bash
python app.py
```

App sẽ khởi động ở `http://127.0.0.1:5000`

## 📚 Tài Liệu Thêm

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask Blueprints](https://flask.palletsprojects.com/blueprints/)
- [Flask Application Factory](https://flask.palletsprojects.com/patterns/appfactories/)
