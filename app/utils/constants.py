"""
Constants used throughout the application
"""

# User roles
ROLE_CUSTOMER = 'customer'
ROLE_ADMIN = 'admin'

# OTP settings
OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 10

# Email settings
EMAIL_SUBJECT_OTP = 'Mã xác thực từ Motor Việt-Nhật'
EMAIL_SUBJECT_WELCOME = 'Chào mừng đến Motor Việt-Nhật'

# Product categories
CATEGORIES = {
    'genuine': 'Phụ tùng chính hãng',
    'zin': 'Phụ tùng zin',
    'battery': 'Pin xe',
    'tires': 'Lốp xe',
    'oil': 'Dầu nhớt'
}

# Pagination
ITEMS_PER_PAGE = 12
