# Database Setup Guide

## 📁 Database Files Organization

```
database/
├── README.md (this file)
├── 01_setup_database.sql          # Create main database
├── 02_shop_database.sql           # Create shop tables (products, orders)
├── 03_auth_database.sql           # Create auth tables (users, sessions)
├── 04_parts_categories.sql        # Insert parts categories
├── 05_setup_team.sql              # Create team members
├── 06_update_booking_table.sql    # Update booking schema
├── 07_update_images.sql           # Update image references
├── 08_update_auth_features.sql    # Add OAuth & 2FA columns
└── migrations/                    # Future database migrations
```

## 🔧 SQL Files Description

| File | Purpose | Status |
|------|---------|--------|
| `01_setup_database.sql` | Creates main database and initial tables | ✅ Core |
| `02_shop_database.sql` | Creates products, categories, orders tables | ✅ Core |
| `03_auth_database.sql` | Creates users, authentication tables | ✅ Core |
| `04_parts_categories.sql` | Inserts motorcycle parts categories | ✅ Data |
| `05_setup_team.sql` | Creates team members/staff table | ✅ Core |
| `06_update_booking_table.sql` | Updates booking table schema | ✅ Update |
| `07_update_images.sql` | Updates image storage references | ✅ Update |
| `08_update_auth_features.sql` | Adds OAuth, 2FA, email verification columns | ✅ Feature |

## 🚀 How to Setup Database

### Method 1: Setup from Scratch
```bash
cd database/

# Run in order:
mysql -u root -p < 01_setup_database.sql
mysql -u root -p suaxemay < 02_shop_database.sql
mysql -u root -p suaxemay < 03_auth_database.sql
mysql -u root -p suaxemay < 04_parts_categories.sql
mysql -u root -p suaxemay < 05_setup_team.sql
mysql -u root -p suaxemay < 06_update_booking_table.sql
mysql -u root -p suaxemay < 07_update_images.sql
mysql -u root -p suaxemay < 08_update_auth_features.sql
```

### Method 2: Setup All at Once
```bash
cd database/
cat 01_setup_database.sql 02_shop_database.sql 03_auth_database.sql 04_parts_categories.sql 05_setup_team.sql 06_update_booking_table.sql 07_update_images.sql 08_update_auth_features.sql | mysql -u root -p
```

### Method 3: Using Script
```bash
# Create setup script (automated)
#!/bin/bash
for file in database/*.sql; do
    echo "Running: $file"
    mysql -u root -p suaxemay < "$file"
done
```

## 📊 Database Structure

### Core Tables
- **users** - User accounts, authentication
- **products** - Motorcycle parts/products
- **orders** - Customer orders
- **bookings** - Service bookings
- **team** - Staff/team members
- **categories** - Product categories
- **cart** - Shopping cart items
- **otp_codes** - OTP verification codes

### Authentication Columns (Added by update_auth_features.sql)
- `email_verified` - Email verification status
- `oauth_provider` - OAuth provider (google, facebook)
- `oauth_id` - OAuth provider ID
- `two_factor_enabled` - 2FA status
- `two_factor_secret` - TOTP secret key

## 🔐 Backup & Recovery

### Backup Database
```bash
mysqldump -u root -p suaxemay > database/backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore from Backup
```bash
mysql -u root -p suaxemay < database/backup_20260202_100000.sql
```

## 📝 Database Configuration

Configure in `config.py`:
```python
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_password",
    "db": "suaxemay",
    "charset": "utf8mb4"
}
```

## 🛠️ Troubleshooting

### Error: "Unknown database 'suaxemay'"
- Run `01_setup_database.sql` first

### Error: "Table 'suaxemay.users' doesn't exist"
- Run `03_auth_database.sql`

### Error: "Column 'email_verified' doesn't exist"
- Run `08_update_auth_features.sql`

### Error: "Access denied for user"
- Check MySQL credentials in `config.py`
- Ensure MySQL service is running

## 📚 Related Files

- `app/utils/database.py` - Database connection management
- `config.py` - Database configuration
- `.env.example` - Environment variables template

## 🔗 Next Steps

1. ✅ Run SQL setup files
2. ✅ Configure `config.py`
3. ✅ Start Flask app: `python3 app.py`
4. ✅ Test at: http://127.0.0.1:5000

---

**Last Updated:** February 2, 2026
**Version:** 1.0
